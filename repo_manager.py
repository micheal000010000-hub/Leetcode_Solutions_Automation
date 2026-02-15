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