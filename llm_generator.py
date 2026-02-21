from config import GITHUB_REPO_URL
import requests
OLLAMA_URL = "http://localhost:11434/api/generate"  # Default Ollama endpoint
OLLAMA_MODEL = "mistral"



def generate_solution_post(problem_number, problem_name, difficulty, link, code, language):
    """
    Generates a structured LeetCode solution post using Mistral via Ollama.
    Returns formatted Markdown content as a string.
    """

    try:
        prompt = f"""You are an expert technical writer creating a high-quality LeetCode solution post.

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
    • The core technique used (e.g., HashMap, Sorting, Two Pointers, DP, Greedy, etc.)
    • The time complexity (Big-O notation)
- Here The code should not be changed at all
- Here The details have to be mentioned based on the laguage asssociated with the code provided as Input
- Never change the language of input code provided in the input based on that response have to be generated based on the laguage of the code provided in the input

2. Generate structured Markdown sections:

## Intuition

## Approach

## Time Complexity

## Space Complexity

## Code

3. The Code section MUST be formatted exactly like:
```{language}
{code}


```

4. The content should be concise, clear, and professional, suitable for a high-quality LeetCode solution post."""
        # print(f"Generated prompt for {language} command")
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "num_predict": 800,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.2,
            },
            timeout=600,
        )
        if response.status_code != 200:
            return f"⚠ Ollama returned status code {response.status_code}"

        response_data = response.json()
        # print(f"Ollama response for {language} command is: {response_data}")
        generated_text = response_data.get("response", "").strip()
        if GITHUB_REPO_URL:
            generated_text += (
                "\n\n---\n"
                f"🔗 **GitHub Repository:** {GITHUB_REPO_URL}\n"
            )

        if not generated_text:
            return "⚠ Mistral returned empty response."

        return generated_text

    except requests.exceptions.Timeout:
        return "⚠ Request timed out. Mistral took too long to respond."
    except requests.exceptions.RequestException as e:
        return f"⚠ Network error: {str(e)}"
    except Exception as e:
        return f"⚠ Error generating solution post: {str(e)}"