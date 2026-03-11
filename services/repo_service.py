from typing import Dict

from git_manager import push_to_github
from repo_manager import add_new_solution, edit_solution


def add_solution(
    problem_number: str,
    problem_name: str,
    difficulty: str,
    link: str,
    solution_code: str,
    filename: str,
) -> None:
    add_new_solution(
        problem_number=problem_number,
        problem_name=problem_name,
        difficulty=difficulty,
        link=link,
        solution_code=solution_code,
        filename=filename,
    )


def edit_existing_solution() -> None:
    edit_solution()


def push_changes() -> Dict[str, str]:
    return push_to_github()
