import threading
import queue
import os
import winsound
import subprocess
import time

from llm_generator import generate_solution_post
from services.repo_service import add_solution, edit_existing_solution, push_changes


generation_queue = queue.Queue()
active_lock = threading.Lock()
active_tasks = 0
shutdown_event = threading.Event()

notification_messages = []
notification_lock = threading.Lock()

MODEL_NAME = "mistral:latest"


def stop_ollama():
    try:
        print("Stopping model...")
        subprocess.run(["ollama", "stop", MODEL_NAME], capture_output=True)
    except Exception as exc:
        print(f"Warning: Could not stop Ollama cleanly: {exc}")


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

        with active_lock:
            active_tasks += 1

        structured_post = generate_solution_post(
            problem_number,
            problem_name,
            difficulty,
            link,
            solution_code,
            language_name,
        )

        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(base_dir)
        copy_folder = os.path.join(project_root, "copy_paste_solution")
        os.makedirs(copy_folder, exist_ok=True)

        safe_problem_name = problem_name.replace(" ", "_")
        structured_filename = f"structured_solution_{problem_number}_{safe_problem_name}.md"
        structured_path = os.path.join(copy_folder, structured_filename)

        with open(structured_path, "w", encoding="utf-8") as handle:
            handle.write(structured_post)

        with notification_lock:
            notification_messages.append(
                f"DONE: {problem_number} - Saved at {structured_path}"
            )

        try:
            winsound.Beep(1000, 300)
        except Exception:
            pass

        generation_queue.task_done()

        with active_lock:
            active_tasks -= 1


def show_queue_status():
    with active_lock:
        print("\nQueue Status")
        print(f"Waiting: {generation_queue.qsize()}")
        print(f"Processing: {active_tasks}")


def main():
    worker_thread = threading.Thread(target=background_worker)
    worker_thread.start()

    language_map = {
        "1": ("py", "Python"),
        "2": ("sql", "SQL"),
        "3": ("cpp", "C++"),
        "4": ("java", "Java"),
    }

    while True:
        with notification_lock:
            if notification_messages:
                print("\nCompleted Tasks:")
                for msg in notification_messages:
                    print(msg)
                notification_messages.clear()

        print("\n==== LeetCode AutoSync ====")
        print("1 -> Add new solution locally")
        print("2 -> Push existing changes to GitHub")
        print("3 -> Show queue status")
        print("4 -> Edit existing solution")
        print("5 -> Exit (wait for queue)")

        choice = input("Select option: ").strip()

        if choice == "1":
            problem_number = input("Problem number: ").strip()
            problem_name = input("Problem name: ").strip()
            difficulty = input("Difficulty (easy/medium/hard): ").strip()
            link = input("Problem link: ").strip()

            print("\nSelect Language:")
            print("1 -> Python")
            print("2 -> SQL")
            print("3 -> C++")
            print("4 -> Java")

            lang_choice = input("Enter option number: ").strip()

            if lang_choice not in language_map:
                print("Invalid language selection.")
                continue

            extension, language_name = language_map[lang_choice]

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

            add_solution(
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

            print(f"\nAdded {problem_number} to queue.")
            show_queue_status()

        elif choice == "2":
            push_changes()

        elif choice == "3":
            show_queue_status()

        elif choice == "4":
            edit_existing_solution()

        elif choice == "5":
            print("\nWaiting for queue to finish...")

            while True:
                with active_lock:
                    remaining = generation_queue.qsize() + active_tasks

                if remaining == 0:
                    print("Queue empty.")
                    shutdown_event.set()
                    generation_queue.put(None)
                    worker_thread.join(timeout=5)
                    print("AutoSync exiting cleanly.")
                    return

                time.sleep(0.5)

        else:
            print("Invalid option selected.")


if __name__ == "__main__":
    main()
