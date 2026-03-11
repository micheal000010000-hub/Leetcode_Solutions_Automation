import argparse
import subprocess
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
LEGACY_DIR = ROOT_DIR / "archive" / "legacy_versions"

LEGACY_TARGETS = {
    "autosync_v1": "autosync_prev_version.py",
    "autosync_v2": "autosync_prev_version_17_02_2026.py",
    "autosync_v3": "autosync_prev_version_21_02_2026.py",
    "bulk_v1": "bulk_generate_prev_version.py",
    "llm_v1": "llm_generator_prev_version.py",
}


def run_target(target_key: str) -> int:
    script_name = LEGACY_TARGETS[target_key]
    script_path = LEGACY_DIR / script_name
    if not script_path.exists():
        print(f"Legacy script not found: {script_path}")
        return 1

    return subprocess.call([sys.executable, str(script_path)], cwd=str(ROOT_DIR))


def print_targets() -> None:
    print("Available legacy targets:")
    for key, value in LEGACY_TARGETS.items():
        print(f"- {key}: {value}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run archived legacy workflows")
    parser.add_argument(
        "target",
        nargs="?",
        choices=list(LEGACY_TARGETS.keys()),
        help="Legacy target key to run",
    )
    parser.add_argument("--list", action="store_true", help="List available legacy targets")
    args = parser.parse_args()

    if args.list:
        print_targets()
        return 0

    if args.target:
        return run_target(args.target)

    print_targets()
    selection = input("Enter target key to run: ").strip()
    if selection not in LEGACY_TARGETS:
        print("Invalid target key.")
        return 1

    return run_target(selection)


if __name__ == "__main__":
    raise SystemExit(main())
