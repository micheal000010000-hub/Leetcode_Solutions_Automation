import subprocess
from datetime import datetime
from config import LEETCODE_REPO_PATH


def push_to_github():
    today = datetime.now().strftime("%d_%m_%Y")
    commit_message = f"commit_{today}"

    add_result = subprocess.run(
        ["git", "add", "."],
        cwd=LEETCODE_REPO_PATH,
        capture_output=True,
        text=True,
    )
    commit_result = subprocess.run(
        ["git", "commit", "-m", commit_message],
        cwd=LEETCODE_REPO_PATH,
        capture_output=True,
        text=True,
    )
    push_result = subprocess.run(
        ["git", "push", "-f"],
        cwd=LEETCODE_REPO_PATH,
        capture_output=True,
        text=True,
    )

    ok = add_result.returncode == 0 and push_result.returncode == 0

    if ok:
        print("Changes pushed to GitHub.")
    else:
        print("Git push workflow completed with errors.")

    return {
        "ok": str(ok),
        "commit_message": commit_message,
        "add_output": (add_result.stdout + add_result.stderr).strip(),
        "commit_output": (commit_result.stdout + commit_result.stderr).strip(),
        "push_output": (push_result.stdout + push_result.stderr).strip(),
    }
