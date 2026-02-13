from google import genai
from config import GEMINI_API_KEY


def generate_solution_post(problem_number, problem_name, difficulty, link, code):
    """
    Generates a structured LeetCode solution post using Gemini 2.5 Flash.
    Returns formatted Markdown content as a string.
    """

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)

        prompt = f"""
        You are an expert technical writer creating a high-quality LeetCode solution post.

        Problem Details:
        Number: {problem_number}
        Name: {problem_name}
        Difficulty: {difficulty}
        Link: {link}

        Python 3 Solution:
        {code}

        Instructions:

        1. Generate a strong, descriptive, professional Title.
        - The title MUST mention:
            • The core technique used (e.g., HashMap, Sorting, Two Pointers, DP, Greedy, etc.)
            • The time complexity (Big-O notation)
            • Python
        - Example style:
            "O(n) HashMap-Based Python Solution | Clean and Simple Approach"

        2. Generate structured Markdown sections:

        ## Intuition

        ## Approach

        ## Time Complexity

        ## Space Complexity

        ## Code

        3. The Code section MUST be formatted exactly like:

        ```python3
        {code}
        ```
        4. The content should be concise, clear, and professional, suitable for a high-quality LeetCode solution post.
        """
        response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

        if not response or not response.text:
            return "⚠ Gemini returned empty response."

        return response.text.strip()

    except Exception as e:
        return f"⚠ Error generating solution post: {str(e)}"