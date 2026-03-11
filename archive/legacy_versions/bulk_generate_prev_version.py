import os
import re
from urllib import response
from google import genai
from config import GEMINI_API_KEY, LEETCODE_REPO_PATH


client = genai.Client(api_key=GEMINI_API_KEY)


def extract_metadata_and_code(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract metadata
    number_match = re.search(r"LeetCode\s+(\d+)_", content)
    difficulty_match = re.search(r"Difficulty:\s+(\w+)", content)
    link_match = re.search(r"Link:\s+(.*)", content)

    if not number_match:
        return None

    problem_number = number_match.group(1)
    difficulty = difficulty_match.group(1) if difficulty_match else "Unknown"
    link = link_match.group(1).strip() if link_match else ""

    # Extract problem name from filename
    filename = os.path.basename(file_path)
    name_part = filename.split("_", 1)[1].replace(".py", "")
    problem_name = name_part

    # Extract code (everything after triple quotes)
    code_start = content.find('"""', content.find('"""') + 3)
    solution_code = content[code_start + 3:].strip()

    return problem_number, problem_name, difficulty, link, solution_code


def generate_post(problem_number, problem_name, difficulty, link, code):

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
   - Mention the core technique used.
   - Mention the time complexity.
   - Mention Python.
   - Example style:
     "O(n) HashMap-Based Python Solution | Clean Approach"

2. Generate structured Markdown sections:

## Intuition
## Approach
## Time Complexity
## Space Complexity
## Code

3. Code section MUST use:

```python3
{code}
Keep it clean and professional.
"""
    
    response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
)

    return response.text.strip() if response.text else None


def main():
    output_folder = os.path.join(os.getcwd(), "bulk_generated_posts")

    if os.path.exists(output_folder):
        print("Clearing old bulk folder...")
        import shutil
        shutil.rmtree(output_folder)

    os.makedirs(output_folder)

    total_processed = 0

    for difficulty in ["easy", "medium", "hard"]:
        folder_path = os.path.join(LEETCODE_REPO_PATH, difficulty)

        if not os.path.exists(folder_path):
            continue

        for file in os.listdir(folder_path):
            if file.endswith(".py"):

                file_path = os.path.join(folder_path, file)
                data = extract_metadata_and_code(file_path)

                if not data:
                    continue

                problem_number, problem_name, diff, link, code = data

                print(f"Generating for {problem_number} - {problem_name}...")

                post = generate_post(problem_number, problem_name, diff, link, code)

                if not post:
                    print(f"⚠ Failed for {problem_number}")
                    continue

                output_file = os.path.join(
                    output_folder,
                    f"{problem_number}_{problem_name}.md"
                )

                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(post)

                total_processed += 1

            print("\n✅ Done.")
            print(f"Generated {total_processed} structured solution posts.")
            print(f"📂 Check folder: {output_folder}")
            print("👉 Copy-paste into LeetCode Solutions section.")
            print("👉 Delete this script after use if desired.")

if __name__ == "__main__":
    main()