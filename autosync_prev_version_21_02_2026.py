import shutil
import threading
import queue
import os
import winsound

from repo_manager import add_new_solution
from git_manager import push_to_github
from llm_generator import generate_solution_post
from config import LEETCODE_REPO_PATH


generation_queue = queue.Queue()
active_lock = threading.Lock()
active_tasks = 0
shutdown_event = threading.Event()
auto_exit_requested = False

notification_messages = []
notification_lock = threading.Lock()


def background_worker():
    global active_tasks

    while not shutdown_event.is_set():
        try:
            task = generation_queue.get(timeout=1)
        except queue.Empty:
            continue

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

        # ✅ increment safely
        with active_lock:
            active_tasks += 1

        # 🚀 generate OUTSIDE lock (important)
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
        os.makedirs(copy_folder, exist_ok=True)

        safe_problem_name = problem_name.replace(" ", "_")
        structured_filename = (
            f"structured_solution_{problem_number}_{safe_problem_name}.md"
        )

        structured_path = os.path.join(copy_folder, structured_filename)

        with open(structured_path, "w", encoding="utf-8") as f:
            f.write(structured_post)

        # ✅ buffer notification instead of printing
        with notification_lock:
            notification_messages.append(
                f"✅ DONE: {problem_number} - Saved at {structured_path}"
            )

        # optional beep (safe)
        try:
            winsound.Beep(1000, 400)
        except:
            pass

        generation_queue.task_done()

        # ✅ decrement safely
        with active_lock:
            active_tasks -= 1


def show_queue_status():
    with active_lock:
        print("\n📊 Queue Status")
        print(f"🕒 Waiting in queue: {generation_queue.qsize()}")
        print(f"⚙ Currently processing: {active_tasks}")


def safe_exit():
    with active_lock:
        remaining = generation_queue.qsize() + active_tasks

    if remaining > 0:
        print(f"\n⚠ There are {remaining} solution(s) still being processed.")
        print("1 → Wait for completion")
        print("2 → Force exit (remaining jobs will be lost)")

        decision = input("Choose option: ").strip()

        if decision == "1":
            print("\n⏳ Waiting for all tasks to complete...")
            generation_queue.join()
            print("✅ All tasks completed. Exiting safely.")
        elif decision == "2":
            print("⚠ Force exiting. Remaining tasks will be lost.")
        else:
            print("Invalid option. Returning to menu.")
            return False

    shutdown_event.set()
    generation_queue.put(None)
    return True


def main():
    global auto_exit_requested
    worker_thread = threading.Thread(target=background_worker, daemon=True)
    worker_thread.start()

    LANGUAGE_MAP = {
        "1": ("py", "Python"),
        "2": ("sql", "SQL"),
        "3": ("cpp", "C++"),
        "4": ("java", "Java"),
    }

    while True:

        # 🚀 AUTO EXIT CHECK
        if auto_exit_requested:
            with active_lock:
                remaining = generation_queue.qsize() + active_tasks

            if remaining == 0:
                print("\n✅ Queue empty. Auto-exiting.")
                shutdown_event.set()
                generation_queue.put(None)
                break


        # 🔔 SAFE notification display (ONLY main thread prints)
        with notification_lock:
            if notification_messages:
                print("\n🔔 Completed Tasks:")
                for msg in notification_messages:
                    print(msg)
                notification_messages.clear()

        print("\n==== LeetCode AutoSync ====")
        print("1 → Add new solution locally")
        print("2 → Push existing changes to GitHub")
        print("3 → Show queue status")
        print("4 → Edit existing solution")
        print("5 → Exit")

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

            add_new_solution(
                problem_number,
                problem_name,
                difficulty,
                link,
                solution_code,
                filename,
            )

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

            print(f"\n📥 Added {problem_number} to queue.")
            show_queue_status()

        elif choice == "2":
            push_to_github()

        elif choice == "3":
            show_queue_status()

        elif choice == "4":
            from repo_manager import edit_solution
            edit_solution()

        elif choice == "5":
            auto_exit_requested = True
            print("\n⏳ Waiting for queue to finish...")

            # 🔥 WAIT LOOP (this was missing)
            while True:
                with active_lock:
                    remaining = generation_queue.qsize() + active_tasks

                if remaining == 0:
                    print("✅ Queue empty. Auto-exiting.")
                    shutdown_event.set()
                    generation_queue.put(None)
                    return  # <-- IMPORTANT: exit main completely

                # small sleep prevents CPU burn
                import time
                time.sleep(0.5)

        else:
            print("Invalid option selected.")


if __name__ == "__main__":
    main()