import os
from config import LEETCODE_REPO_PATH


def add_new_solution(problem_number, problem_name, difficulty, link, solution_code, filename):
    difficulty = difficulty.lower()

    if difficulty not in ["easy", "medium", "hard"]:
        raise ValueError("Difficulty must be easy, medium, or hard")

    folder_path = os.path.join(LEETCODE_REPO_PATH, difficulty)

    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"{difficulty} folder not found")
    file_path = os.path.join(folder_path, filename)

    file_content = f'''"""
LeetCode {problem_number}_{problem_name}
Difficulty: {difficulty.capitalize()}
Link: {link}
"""

{solution_code}
'''

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(file_content)

    update_readme(problem_number, problem_name, link, difficulty)

    print("✅ Solution added locally (not pushed).")


def update_readme(problem_number, problem_name, link, difficulty):
    import re
    import os
    from config import LEETCODE_REPO_PATH

    readme_path = os.path.join(LEETCODE_REPO_PATH, "README.md")

    with open(readme_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    section_header = f"## {difficulty.capitalize()}"
    new_entry = f"- [{problem_number}_{problem_name}]({link})\n"

    updated_lines = []
    inside_section = False
    section_entries = []

    for line in lines:
        stripped = line.strip()

        # Detect start of target section
        if stripped == section_header:
            inside_section = True
            updated_lines.append(line)
            continue

        # Detect start of another section
        if stripped.startswith("## ") and inside_section:
            # Sort entries before leaving section
            section_entries.append(new_entry)

            section_entries = sorted(
                set(section_entries),  # remove duplicates
                key=lambda x: int(re.search(r"\[(\d+)_", x).group(1))
            )

            updated_lines.extend(section_entries)
            section_entries = []
            inside_section = False
            updated_lines.append(line)
            continue

        if inside_section:
            if stripped.startswith("- ["):
                section_entries.append(line)
            else:
                updated_lines.append(line)
        else:
            updated_lines.append(line)

    # If section was at end of file
    if inside_section:
        section_entries.append(new_entry)

        section_entries = sorted(
            set(section_entries),
            key=lambda x: int(re.search(r"\[(\d+)_", x).group(1))
        )

        updated_lines.extend(section_entries)

    with open(readme_path, "w", encoding="utf-8") as f:
        f.writelines(updated_lines)

    print("✅ README updated and sorted.")




import re
import shutil


def find_solution_file(problem_number):
    for difficulty in ["easy", "medium", "hard"]:
        folder_path = os.path.join(LEETCODE_REPO_PATH, difficulty)
        if not os.path.exists(folder_path):
            continue

        for file in os.listdir(folder_path):
            if file.startswith(f"{problem_number}_"):
                return difficulty, os.path.join(folder_path, file)

    return None, None


def edit_solution():
    old_number = input("Enter existing problem number to edit: ").strip()

    old_difficulty, old_path = find_solution_file(old_number)

    if not old_path:
        print("❌ Solution not found.")
        return

    print(f"Found in '{old_difficulty}': {old_path}")

    new_number = input("New problem number (Enter to keep same): ").strip()
    new_name = input("New problem name (Enter to keep same): ").strip()
    new_difficulty = input("New difficulty (easy/medium/hard or Enter to keep same): ").strip()
    new_link = input("New link (Enter to keep same): ").strip()

    with open(old_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract existing values
    name_match = re.search(r'LeetCode\s+\d+_(.+)', content)
    link_match = re.search(r'Link:\s+(.*)', content)
    diff_match = re.search(r'Difficulty:\s+(\w+)', content)

    current_name = name_match.group(1) if name_match else ""
    current_link = link_match.group(1) if link_match else ""
    current_diff = diff_match.group(1).lower() if diff_match else old_difficulty

    final_number = new_number if new_number else old_number
    final_name = new_name if new_name else current_name
    final_link = new_link if new_link else current_link
    final_difficulty = new_difficulty.lower() if new_difficulty else current_diff

    safe_name = final_name.replace(" ", "_")
    extension = old_path.split(".")[-1]

    new_filename = f"{final_number}_{safe_name}.{extension}"
    new_folder = os.path.join(LEETCODE_REPO_PATH, final_difficulty)

    if not os.path.exists(new_folder):
        print("❌ Target difficulty folder not found.")
        return

    new_path = os.path.join(new_folder, new_filename)

    # Update header inside file
    updated_content = re.sub(
        r'LeetCode\s+\d+_.+',
        f'LeetCode {final_number}_{final_name}',
        content
    )

    updated_content = re.sub(
        r'Difficulty:\s+\w+',
        f'Difficulty: {final_difficulty.capitalize()}',
        updated_content
    )

    updated_content = re.sub(
        r'Link:\s+.*',
        f'Link: {final_link}',
        updated_content
    )

    with open(new_path, "w", encoding="utf-8") as f:
        f.write(updated_content)

    if old_path != new_path:
        os.remove(old_path)

    print("✅ File updated.")

    update_readme_on_edit(
        old_number,
        final_number,
        final_name,
        final_link,
        old_difficulty,
        final_difficulty
    )



def update_readme_on_edit(old_number, new_number, new_name, new_link, old_diff, new_diff):
    readme_path = os.path.join(LEETCODE_REPO_PATH, "README.md")

    with open(readme_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    updated_lines = []
    for line in lines:
        if line.strip().startswith(f"- [{old_number}_"):
            continue
        updated_lines.append(line)

    # Reuse existing sorting logic by calling update_readme
    update_readme(new_number, new_name, new_link, new_diff)

    print("✅ README updated after edit.")