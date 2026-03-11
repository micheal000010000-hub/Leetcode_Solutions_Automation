# LeetCode AutoSync

LeetCode AutoSync provides both terminal and UI workflows for managing your LeetCode solutions, generating structured explanations with Ollama, and tracking prompt-performance metrics.

## What Is Improved

- High-contrast UI for better readability.
- Responsive layout and first-time onboarding guide.
- Dedicated Activity and Health view to understand live system state.
- Organized project layout with `services/`, `ui/`, `docs/`, and `archive/`.
- Expanded LLM run analytics in SQLite with Excel export.

## Features

- Add new LeetCode solutions by difficulty.
- Auto-update and sort your main LeetCode `README.md`.
- Generate structured markdown solution posts.
- Track run quality, throughput, and format completeness.
- Capture human feedback (`accepted_for_posting`, `manual_edit_distance`).
- Export metrics to Excel.
- Push repository changes with date-based commit message.

## Project Structure

```text
leetcode-autosync/
|-- autosync.py              # compatibility wrapper -> current.autosync
|-- ui_app.py
|-- run_current.py
|-- run_legacy.py
|-- config.py                # compatibility wrapper -> current.config
|-- llm_generator.py         # compatibility wrapper -> current.llm_generator
|-- repo_manager.py
|-- git_manager.py           # compatibility wrapper -> current.git_manager
|-- bulk_generate.py         # compatibility wrapper -> current.bulk_generate
|-- requirements.txt
|
|-- current/
|   |-- __init__.py
|   |-- autosync.py
|   |-- bulk_generate.py
|   |-- config.py
|   |-- git_manager.py
|   `-- llm_generator.py
|
|-- services/
|   |-- __init__.py
|   |-- generation_service.py
|   |-- metrics_service.py
|   |-- repo_service.py
|   `-- system_service.py
|
|-- ui/
|   |-- __init__.py
|   |-- activity.py
|   |-- constants.py
|   |-- pages.py
|   `-- theme.py
|
|-- docs/
|   `-- ARCHITECTURE.md
|
|-- archive/
|   `-- legacy_versions/
|       |-- README.md
|       |-- autosync_prev_version.py
|       |-- autosync_prev_version_17_02_2026.py
|       |-- autosync_prev_version_21_02_2026.py
|       |-- bulk_generate_prev_version.py
|       `-- llm_generator_prev_version.py
|
|-- llm_stats/
|   |-- runs.db
|   `-- token_usage.xlsx
|
|-- copy_paste_solution/
`-- bulk_generated_posts_ollama/
```

## Setup

Create `.env` in project root:

```env
LEETCODE_REPO_PATH=C:/Users/YourName/Documents/LeetCode Solutions
GITHUB_REPO_URL=https://github.com/your-username/your-repo

OLLAMA_URL=http://localhost:11434
OLLAMA_GENERATE_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=mistral

LLM_NUM_PREDICT=800
LLM_TEMPERATURE=0.2
LLM_TIMEOUT_SECONDS=600
PROMPT_VERSION=v1.0.0
PROMPT_STRATEGY=analysis_only_append_code_v1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

Current workflow launcher:

```bash
python run_current.py cli
python run_current.py ui
python run_current.py bulk
```

Direct commands:

```bash
python autosync.py
streamlit run ui_app.py
```

Legacy workflow launcher:

```bash
python run_legacy.py --list
python run_legacy.py autosync_v1
python run_legacy.py autosync_v2
python run_legacy.py autosync_v3
python run_legacy.py bulk_v1
python run_legacy.py llm_v1
```

## UI Tabs

- `Generate`: create solution post and save feedback metrics.
- `Queue`: monitor recent run outcomes.
- `Metrics`: analyze trends and prompt-version comparisons.
- `Activity`: inspect event stream plus health/runtime checks.
- `Git`: execute add/commit/push workflow.
- `Settings`: inspect active paths and configuration.

## Metrics Storage

Primary source:
- `llm_stats/runs.db`

Excel export:
- `llm_stats/token_usage.xlsx`

Excel sheets:
- `Usage`
- `Summary`
- `PromptVersionSummary`

## Prompt Optimization Flow

1. Update `PROMPT_VERSION` for each prompt iteration.
2. Run multiple generations for each version.
3. Compare quality and speed in `Metrics` tab.
4. Add feedback from the `Generate` tab.
5. Export workbook for review and tracking.

## Notes

- `GEMINI_API_KEY` is optional and no longer required for startup.
- Runtime DB (`llm_stats/runs.db`) is ignored from git.
- Force push is still part of existing git flow.
- Legacy snapshot scripts are preserved under `archive/legacy_versions/`.
- Use `run_current.py` for current flows and `run_legacy.py` for archived flows.
- Active implementations now live in `current/`; root files are compatibility wrappers.
