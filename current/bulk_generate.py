import os
import re
import time
import gc
from dotenv import load_dotenv
from config import LEETCODE_REPO_PATH, OLLAMA_MODEL
from services.generation_service import generate_solution_post

TARGET_DIFFICULTY = "medium"

load_dotenv()


def extract_metadata_and_code(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract from docstring at top
    number_match = re.search(r"LeetCode\s+(\d+)", content)
    difficulty_match = re.search(r"Difficulty:\s+(\w+)", content)
    link_match = re.search(r"Link:\s+(https?://\S+)", content)

    if not number_match:
        print(f"Warning: Skipping {file_path} - no LeetCode number found")
        return None

    problem_number = number_match.group(1)
    difficulty = difficulty_match.group(1) if difficulty_match else "Unknown"
    link = link_match.group(1).strip() if link_match else ""

    filename = os.path.basename(file_path)
    name_part = re.sub(r"^\d+_?-?\s*", "", filename).replace(".py", "").strip()
    problem_name = name_part

    # Extract code AFTER the closing """ of the docstring
    docstring_end = content.find('"""', content.find('"""') + 1)
    solution_code = content[docstring_end + 3:].strip()

    if not solution_code:
        print(f"Warning: Skipping {file_path} - no solution code found")
        return None

    return problem_number, problem_name, difficulty, link, solution_code


def main():
    output_folder = os.path.join(os.getcwd(), "bulk_generated_posts_ollama")
    os.makedirs(output_folder, exist_ok=True)

    folder_path = os.path.join(LEETCODE_REPO_PATH, TARGET_DIFFICULTY)

    if not os.path.exists(folder_path):
        print(f"Folder not found: {folder_path}")
        return

    files = [f for f in sorted(os.listdir(folder_path)) if f.endswith(".py")]

    print(f"\nProcessing {TARGET_DIFFICULTY.upper()} ({len(files)} files)")
    print(f"Model: {OLLAMA_MODEL}\n")

    generated = 0
    skipped = 0
    failed = 0
    metadata_failed = 0

    for idx, file in enumerate(files, 1):
        file_path = os.path.join(folder_path, file)
        data = extract_metadata_and_code(file_path)

        if not data:
            print(f"[{idx}/{len(files)}] SKIPPED: {file} - metadata extraction failed")
            metadata_failed += 1
            skipped += 1
            continue

        problem_number, problem_name, diff, link, code = data
        output_file = os.path.join(output_folder, f"{problem_number}_{problem_name}.md")

        if os.path.exists(output_file):
            print(f"[{idx}/{len(files)}] SKIPPED: Problem {problem_number} - already exists")
            skipped += 1
            continue

        print(f"[{idx}/{len(files)}] Processing: Problem {problem_number} - {problem_name}...", end=" ", flush=True)

        result = generate_solution_post(
            problem_number=problem_number,
            problem_name=problem_name,
            difficulty=diff,
            link=link,
            code=code,
            language="Python",
            include_repo_link=False,
        )

        if result.startswith("Warning: Could not connect"):
            print("\n\nOLLAMA NOT RUNNING!")
            print("Start it with: ollama serve")
            print("Then run this script again.\n")
            return

        elif result.startswith("Warning: Request timed out"):
            print("TIMEOUT (model took too long)")
            failed += 1

        elif result and not result.startswith("Warning:"):
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(result)
            print("SUCCESS")
            generated += 1

        else:
            print(f"FAILED: {result}")
            failed += 1

        gc.collect()
        time.sleep(2)

    print(f"\n{'='*60}")
    print("FINAL RESULTS:")
    print(f"{'='*60}")
    print(f"Generated         : {generated}")
    print(f"Skipped (exists)  : {skipped - metadata_failed}")
    print(f"Metadata failed   : {metadata_failed}")
    print(f"Failed            : {failed}")
    print(f"Output folder     : {output_folder}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
