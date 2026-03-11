# Architecture Overview

## Goal

Keep generation, metrics, repository operations, and UI responsibilities cleanly separated so each area can evolve independently.

## Layered Structure

- Entry Points
  - `autosync.py`: terminal workflow and queue execution.
  - `ui_app.py`: Streamlit app entrypoint.

- Core Services (`services/`)
  - `generation_service.py`: prompt construction + Ollama call + run logging.
  - `metrics_service.py`: SQLite persistence, Excel export, quality scoring, feedback updates.
  - `repo_service.py`: wrappers over repository and git operations.
  - `system_service.py`: runtime health checks and status snapshot.

- UI Package (`ui/`)
  - `theme.py`: high-contrast responsive styling.
  - `pages.py`: tab content rendering and interactions.
  - `activity.py`: UI event stream and activity state helpers.
  - `constants.py`: tab names and language mapping.

- Compatibility Modules
  - `llm_generator.py`: preserved API wrapper for old call sites.
  - `repo_manager.py` and `git_manager.py`: existing operation implementations.

- Runtime Data
  - `llm_stats/runs.db`: source-of-truth run data.
  - `llm_stats/token_usage.xlsx`: exported workbook for review.
  - `copy_paste_solution/`: generated markdown output.

- Archive
  - `archive/legacy_versions/`: historical snapshots moved from root.

## Why This Layout Works

- UI changes do not require touching core generation logic.
- Metric schema can grow without changing CLI workflows.
- Legacy compatibility remains intact while new structure stays clean.
- New team members can find responsibilities by folder quickly.
