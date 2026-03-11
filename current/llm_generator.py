from config import OLLAMA_MODEL, PROMPT_VERSION
from services.generation_service import generate_solution_post as _generate_solution_post
from services.metrics_service import build_run_record, log_run_record


def log_token_usage(problem_number, problem_name, response_data):
    """Backward-compatible logger for legacy call paths."""
    record = build_run_record(
        problem_number=problem_number,
        problem_name=problem_name,
        difficulty="",
        language="",
        model=OLLAMA_MODEL,
        prompt_version=PROMPT_VERSION,
        prompt="",
        code="",
        response_text=(response_data or {}).get("response", ""),
        response_data=response_data or {},
        http_status=200,
        error_type="",
        error_message="",
        timeout_flag=0,
    )
    log_run_record(record)


def generate_solution_post(
    problem_number,
    problem_name,
    difficulty,
    link,
    code,
    language,
    include_repo_link=True,
):
    """Compatibility wrapper around the new generation service."""
    return _generate_solution_post(
        problem_number=problem_number,
        problem_name=problem_name,
        difficulty=difficulty,
        link=link,
        code=code,
        language=language,
        include_repo_link=include_repo_link,
    )
