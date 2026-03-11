import argparse
import subprocess
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent


def run_ui() -> int:
    return subprocess.call(
        [sys.executable, "-m", "streamlit", "run", str(ROOT_DIR / "ui_app.py")],
        cwd=str(ROOT_DIR),
    )


def run_cli() -> int:
    from autosync import main

    main()
    return 0


def run_bulk() -> int:
    from bulk_generate import main

    main()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run current LeetCode AutoSync workflows")
    parser.add_argument(
        "mode",
        choices=["ui", "cli", "bulk"],
        help="Workflow mode to run",
    )
    args = parser.parse_args()

    if args.mode == "ui":
        return run_ui()
    if args.mode == "cli":
        return run_cli()
    return run_bulk()


if __name__ == "__main__":
    raise SystemExit(main())
