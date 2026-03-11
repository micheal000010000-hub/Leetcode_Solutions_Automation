import subprocess
from datetime import datetime
from config import LEETCODE_REPO_PATH


def push_to_github():
    today = datetime.now().strftime("%d_%m_%Y")
    commit_message = f"commit_{today}"

    subprocess.run(["git", "add", "."], cwd=LEETCODE_REPO_PATH)
    subprocess.run(["git", "commit", "-m", commit_message], cwd=LEETCODE_REPO_PATH)
    subprocess.run(["git", "push", "-f"], cwd=LEETCODE_REPO_PATH)

    print("Changes pushed to GitHub.")
