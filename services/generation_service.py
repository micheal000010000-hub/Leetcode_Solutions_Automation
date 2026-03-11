import re
from typing import Any, Dict, Optional

import requests

from config import (
    GITHUB_REPO_URL,
    LLM_NUM_PREDICT,
    LLM_TEMPERATURE,
    LLM_TIMEOUT_SECONDS,
    OLLAMA_GENERATE_URL,
    OLLAMA_MODEL,
    PROMPT_STRATEGY,
    PROMPT_VERSION,
)
from services.metrics_service import build_run_record, log_run_record


def build_generation_prompt(
    problem_number: str,
    problem_name: str,
    difficulty: str,
    link: str,
    code: str,
    language: str,
) -> str:
    return f"""You are an expert technical writer creating a high-quality LeetCode solution post.

Problem Details:
Number: {problem_number}
Name: {problem_name}
Difficulty: {difficulty}
Link: {link}

{language} Solution:
{code}

Instructions:

1. Generate a strong, descriptive, professional Title.
- The title MUST mention:
    - The core technique used
    - The time complexity (Big-O notation)
- The explanation must match the provided language

2. Generate markdown using exactly these sections and no additional top-level sections:

Title: <single line title>
## Intuition
## Approach
## Time Complexity
## Space Complexity

3. Do NOT include any code block and do NOT add a ## Code section.
4. Keep the response concise, technical, and ready for markdown publishing.
"""


def _markdown_language_tag(language: str) -> str:
    mapping = {
        "python": "python",
        "sql": "sql",
        "c++": "cpp",
        "java": "java",
    }
    return mapping.get((language or "").strip().lower(), "text")


def _strip_code_sections(text: str) -> str:
    content = (text or "").strip()
    if not content:
        return ""

    # Remove fenced code blocks if model accidentally returns them.
    content = re.sub(r"```[\s\S]*?```", "", content)
    # Remove trailing explicit code sections if present.
    content = re.sub(r"(?ims)^##\s*Code\b[\s\S]*$", "", content).strip()
    return content


def _compose_final_output(
    analysis_text: str,
    code: str,
    language: str,
    include_repo_link: bool,
) -> str:
    cleaned_body = _strip_code_sections(analysis_text)
    if not cleaned_body:
        cleaned_body = "Title: Solution Explanation\n\n## Intuition\nUnable to generate model explanation."

    lang_tag = _markdown_language_tag(language)
    final_text = (
        f"{cleaned_body}\n\n## Code\n"
        f"```{lang_tag}\n{code}\n```"
    )

    if include_repo_link and GITHUB_REPO_URL:
        final_text += "\n\n---\n" + f"Repository: {GITHUB_REPO_URL}\n"

    return final_text


def _classify_http_error(status_code: Optional[int]) -> str:
    if status_code is None:
        return ""
    if 500 <= status_code <= 599:
        return "HTTP_SERVER_ERROR"
    if 400 <= status_code <= 499:
        return "HTTP_CLIENT_ERROR"
    if status_code != 200:
        return "HTTP_UNEXPECTED_STATUS"
    return ""


def generate_solution_post_with_metadata(
    problem_number: str,
    problem_name: str,
    difficulty: str,
    link: str,
    code: str,
    language: str,
    include_repo_link: bool = True,
) -> Dict[str, Any]:
    """Generate a structured post through Ollama and return text plus run metadata."""

    prompt = build_generation_prompt(
        problem_number=problem_number,
        problem_name=problem_name,
        difficulty=difficulty,
        link=link,
        code=code,
        language=language,
    )

    response_data: Dict[str, Any] = {}
    response_text = ""
    llm_response_text = ""
    error_type = ""
    error_message = ""
    timeout_flag = 0
    http_status: Optional[int] = None
    code_appended_externally = 0
    llm_returned_code_block = 0

    try:
        response = requests.post(
            OLLAMA_GENERATE_URL,
            json={
                "model": OLLAMA_MODEL,
                "num_predict": LLM_NUM_PREDICT,
                "prompt": prompt,
                "stream": False,
                "temperature": LLM_TEMPERATURE,
            },
            timeout=LLM_TIMEOUT_SECONDS,
        )

        http_status = response.status_code
        if response.status_code != 200:
            error_type = _classify_http_error(response.status_code)
            error_message = f"Ollama returned status code {response.status_code}"
            response_text = f"Warning: {error_message}"
        else:
            response_data = response.json()
            llm_response_text = response_data.get("response", "").strip()
            if not llm_response_text:
                error_type = "EMPTY_RESPONSE"
                error_message = "Model returned empty response"
                response_text = "Warning: Mistral returned empty response."
            else:
                llm_returned_code_block = int("```" in llm_response_text or "## Code" in llm_response_text)
                response_text = _compose_final_output(
                    analysis_text=llm_response_text,
                    code=code,
                    language=language,
                    include_repo_link=include_repo_link,
                )
                code_appended_externally = 1

    except requests.exceptions.Timeout:
        timeout_flag = 1
        error_type = "TIMEOUT"
        error_message = "Request timed out"
        response_text = "Warning: Request timed out."

    except requests.exceptions.ConnectionError as exc:
        error_type = "CONNECTION_ERROR"
        error_message = str(exc)
        response_text = "Warning: Could not connect to Ollama. Check if it is running."

    except requests.exceptions.RequestException as exc:
        error_type = "REQUEST_ERROR"
        error_message = str(exc)
        response_text = f"Warning: Network error: {str(exc)}"

    except Exception as exc:
        error_type = "UNEXPECTED_ERROR"
        error_message = str(exc)
        response_text = f"Warning: Error generating solution post: {str(exc)}"

    record = build_run_record(
        problem_number=problem_number,
        problem_name=problem_name,
        problem_link=link,
        difficulty=difficulty,
        language=language,
        model=OLLAMA_MODEL,
        prompt_version=PROMPT_VERSION,
        prompt_strategy=PROMPT_STRATEGY,
        prompt=prompt,
        code=code,
        response_text=response_text,
        llm_response_text=llm_response_text,
        response_data=response_data,
        http_status=http_status,
        error_type=error_type,
        error_message=error_message,
        timeout_flag=timeout_flag,
        llm_returned_code_block=llm_returned_code_block,
        code_appended_externally=code_appended_externally,
        retry_count=0,
        manual_edit_distance=None,
        accepted_for_posting=None,
    )
    log_run_record(record)

    return {
        "text": response_text,
        "run_id": record["run_id"],
        "error_type": error_type,
        "http_status": http_status,
    }


def generate_solution_post(
    problem_number: str,
    problem_name: str,
    difficulty: str,
    link: str,
    code: str,
    language: str,
    include_repo_link: bool = True,
) -> str:
    result = generate_solution_post_with_metadata(
        problem_number=problem_number,
        problem_name=problem_name,
        difficulty=difficulty,
        link=link,
        code=code,
        language=language,
        include_repo_link=include_repo_link,
    )
    return result["text"]
