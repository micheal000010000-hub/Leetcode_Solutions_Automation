
import shutil
from repo_manager import add_new_solution
from git_manager import push_to_github
from llm_generator import generate_solution_post
from config import LEETCODE_REPO_PATH
import os

def main():
    print("==== LeetCode AutoSync ====")
    print("1 → Add new solution locally")
    print("2 → Push existing changes to GitHub")

    choice = input("Select option (1 or 2): ").strip()
    LANGUAGE_MAP = {
    "1": ".py",
    "2": ".sql",
    "3": ".cpp",
    "4": ".java"
    }

    if choice == "1":
        problem_number = input("Problem number: ").strip()
        problem_name = input("Problem name: ").strip()
        difficulty = input("Difficulty (easy/medium/hard): ").strip()
        link = input("Problem link: ").strip()

        print("\nSelect Language:")
        print("1 → Python")
        print("2 → SQL")
        print("3 → C++")
        print("4 → Java")

        lang_choice = input("Enter option number: ").strip()

        if lang_choice not in LANGUAGE_MAP:
            print("Invalid language selection.")
            return

        extension = LANGUAGE_MAP[lang_choice]

        print("\nPaste your solution below. Type END on a new line to finish:")

        lines = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            lines.append(line)

        solution_code = "\n".join(lines)

        safe_problem_name = problem_name.replace(" ", "_")
        filename = f"{problem_number}_{safe_problem_name}.{extension}"

        add_new_solution(
            problem_number,
            problem_name,
            difficulty,
            link,
            solution_code,
            filename
        )

        # Step 2: Generate LLM content
        print("Generating structured solution post using Mistral...")

        structured_post = generate_solution_post(
            problem_number,
            problem_name,
            difficulty,
            link,
            solution_code
        )

        

        # Step 3: Prepare "copy paste this solution" folder
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        copy_folder = os.path.join(BASE_DIR, "copy_paste_solution")

        # If folder exists → clear it completely
        if os.path.exists(copy_folder):
            shutil.rmtree(copy_folder)

        # Recreate fresh empty folder
        os.makedirs(copy_folder)

        # Generate clean filename
        safe_problem_name = problem_name.replace(" ", "_")
        structured_filename = f"structured_solution_{problem_number}_{safe_problem_name}.md"

        structured_path = os.path.join(copy_folder, structured_filename)

        # Save structured markdown
        with open(structured_path, "w", encoding="utf-8") as f:
            f.write(structured_post)

        print("\n✅ Structured solution generated.")
        print(f"📂 Saved at: {structured_path}")
        print("👉 Folder was cleared and recreated.")
        print("👉 Please copy and paste into LeetCode Solutions section.")
        output_file = os.path.join(
            copy_folder,
            f"{problem_number}_{problem_name}_solution_post.md"
        )

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(structured_post)

        print("\n✅ Structured solution generated.")
        print(f"📂 Saved at: {output_file}")
        print("👉 Please copy and paste into LeetCode Solutions section.")

    elif choice == "2":
        push_to_github()

    else:
        print("Invalid option selected.")


if __name__ == "__main__":
    main()