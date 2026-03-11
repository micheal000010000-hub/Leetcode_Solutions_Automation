import shutil
import threading
import queue
import os
import winsound  # For notification beep (Windows)

from repo_manager import add_new_solution
from git_manager import push_to_github
from llm_generator import generate_solution_post
from config import LEETCODE_REPO_PATH


# 🔹 Background queue
generation_queue = queue.Queue()


def background_worker():
    while True:
        task = generation_queue.get()

        if task is None:
            break

        (
            problem_number,
            problem_name,
            difficulty,
            link,
            solution_code,
            language_name,
        ) = task

        print(f"\n🔄 Generating structured post for {problem_number}...")

        structured_post = generate_solution_post(
            problem_number,
            problem_name,
            difficulty,
            link,
            solution_code,
            language_name,
        )

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        copy_folder = os.path.join(BASE_DIR, "copy_paste_solution")

        # Do NOT clear folder every time anymore
        os.makedirs(copy_folder, exist_ok=True)

        safe_problem_name = problem_name.replace(" ", "_")
        structured_filename = (
            f"structured_solution_{problem_number}_{safe_problem_name}.md"
        )

        structured_path = os.path.join(copy_folder, structured_filename)

        with open(structured_path, "w", encoding="utf-8") as f:
            f.write(structured_post)

        print(f"\n✅ DONE: {problem_number} - Ready to copy 🚀")
        print(f"📂 Saved at: {structured_path}")

        # 🔔 Notification sound
        try:
            winsound.Beep(1000, 500)
        except:
            pass

        generation_queue.task_done()


def main():
    # 🔹 Start background worker
    worker_thread = threading.Thread(target=background_worker, daemon=True)
    worker_thread.start()

    LANGUAGE_MAP = {
        "1": ("py", "Python"),
        "2": ("sql", "SQL"),
        "3": ("cpp", "C++"),
        "4": ("java", "Java"),
    }

    while True:
        print("\n==== LeetCode AutoSync ====")
        print("1 → Add new solution locally")
        print("2 → Push existing changes to GitHub")
        print("3 → Exit (Exit has yto be selected to stop the background worker thread gracefully)")

        choice = input("Select option: ").strip()

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
                continue

            extension, language_name = LANGUAGE_MAP[lang_choice]

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

            # 🔹 Instant local add
            add_new_solution(
                problem_number,
                problem_name,
                difficulty,
                link,
                solution_code,
                filename,
            )

            # 🔹 Push to background queue
            generation_queue.put(
                (
                    problem_number,
                    problem_name,
                    difficulty,
                    link,
                    solution_code,
                    language_name,
                )
            )

            print(
                f"\n📥 {problem_number} added to background generation queue."
            )
            print(
                f"🕒 Current queue size: {generation_queue.qsize()}"
            )

        elif choice == "2":
            push_to_github()

        elif choice == "3":
            print("Exiting...")
            generation_queue.put(None)
            break

        else:
            print("Invalid option selected.")


if __name__ == "__main__":
    main()