# LeetCode AutoSync Studio

LeetCode AutoSync Studio helps you automate the repetitive parts of maintaining a LeetCode solutions repository.

It combines:
- local repository updates (save solutions and update the target LeetCode README),
- local LLM generation (Ollama) for structured writeups,
- metrics logging for quality and performance tracking,
- a Streamlit UI for daily workflow,
- compatibility layers for legacy scripts.

The project is designed so you can focus on solving problems while the tool handles organization, markdown generation, and reporting.

## What This Project Actually Does

At a practical level, each generation run can do all of the following in one flow:

1. Accept problem metadata and code.
2. Optionally save the solution file into your LeetCode repo by difficulty (`easy`, `medium`, `hard`).
3. Update and sort your target LeetCode README section.
4. Call Ollama to generate a structured explanation.
5. Normalize the output format and append your original code block.
6. Save publish-ready markdown into a local output folder.
7. Log full run metrics to SQLite and export to Excel.
8. Optionally attach feedback (`accepted_for_posting`, edit distance).

## Core Capabilities

- Single-run generation from UI or CLI
- Queue and batch processing in UI
- Local solution file creation and README synchronization
- Prompt and response analytics (speed, token usage, completeness, format quality)
- Health checks for Ollama/model/runtime files
- One-click git add + commit + force push workflow
- Legacy launcher for archived script versions

## Architecture Overview

The codebase is organized to keep responsibilities separated:

- Entry points
	- `run_current.py`: launcher for `ui`, `cli`, `bulk`, `status`
	- `run_legacy.py`: launcher for archived scripts
	- `ui_app.py`: Streamlit app entrypoint

- Current implementation modules
	- `current/config.py`: environment variables and runtime settings
	- `current/autosync.py`: interactive CLI workflow with background generation queue
	- `current/bulk_generate.py`: batch generation from existing Python solution files
	- `current/git_manager.py`: git add/commit/push implementation
	- `current/llm_generator.py`: compatibility wrapper over modern generation service

- Service layer (`services/`)
	- `generation_service.py`: prompt creation, Ollama call, output assembly, error handling
	- `metrics_service.py`: SQLite schema, run logging, feedback updates, Excel export
	- `repo_service.py`: wrapper around repository and git operations
	- `system_service.py`: runtime and Ollama health snapshots

- UI layer (`ui/`)
	- `pages.py`: tab content and interactions
	- `activity.py`: in-memory activity stream for the UI
	- `theme.py`: shared styling
	- `constants.py`: tab names and language-extension mapping

- Compatibility wrappers at project root
	- `autosync.py`, `config.py`, `llm_generator.py`, `git_manager.py`, `bulk_generate.py`
	- These forward to `current/` implementations so older imports keep working.

## Repository Structure

```text
LeetCode-AutoSync-Studio/
|-- run_current.py
|-- run_legacy.py
|-- ui_app.py
|-- current/
|-- services/
|-- ui/
|-- docs/
|-- archive/legacy_versions/
|-- llm_stats/                   # runtime metrics DB + Excel export
|-- copy_paste_solution/         # generated markdown output
`-- bulk_generated_posts_ollama/ # bulk mode output
```

## End-to-End Flow

### Generate Flow (UI or service call)

1. You submit problem number, name, difficulty, link, language, and code.
2. If `save_to_repo` is enabled, solution file is created in your LeetCode repo and README is updated.
3. Prompt is constructed with strict section instructions.
4. Ollama is called through `OLLAMA_GENERATE_URL`.
5. Output is cleaned:
	 - accidental code blocks are removed from analysis section,
	 - title length limit is enforced,
	 - final `## Code` section is appended from your original code.
6. Markdown is written to `copy_paste_solution/structured_solution_<number>_<name>.md`.
7. Run metadata is persisted in `llm_stats/runs.db`.
8. Excel export is refreshed automatically.

### Git Flow (UI Git tab)

The git action runs:
- `git add .`
- `git commit -m commit_<dd_mm_yyyy>`
- `git push -f`

Important: push is force push by design in the current implementation.

### Status Flow (CLI)

`python run_current.py status` returns a JSON snapshot that includes:
- Ollama reachability,
- metrics database presence,
- run counts and averages,
- active prompt version.

## UI Tabs Explained

- Generate
	- Main authoring surface for single run and queueing.
	- Supports optional repo save, optional repo link append, and feedback capture.

- Queue
	- Shows recent run status (`Success` or `Failed`) with sortable run fields.

- Metrics
	- Summaries, trend charts, prompt-version comparisons, and Excel export button.

- Activity
	- Event stream and live runtime health checks.

- Git
	- Executes configured add/commit/force-push workflow and displays outputs.

- Settings
	- Displays resolved paths and active runtime configuration.

- Copy Solutions
	- Browser for generated markdown files with easy copy workflow.

- About
	- High-level purpose and user-facing context.

## Metrics and Analytics

### Primary storage

- SQLite database: `llm_stats/runs.db`

### Excel export

- Workbook path: `llm_stats/token_usage.xlsx`
- Fallback file is created with timestamp if workbook is locked by another app.

### Workbook sheets

- `Usage`: per-run detailed records
- `Summary`: aggregate metrics
- `PromptVersionSummary`: prompt/model grouped performance
- `ModelSummary`: model-level aggregates
- `Legend`: field definitions and legacy markers

### Tracked signals include

- token counts and output/input ratio
- duration and tokens/sec
- response quality flags (`Title`, `Intuition`, `Approach`, complexity sections, code block)
- format and completeness scores
- prompt hash, prompt text preview, raw response text
- human feedback (`accepted_for_posting`, `manual_edit_distance`)

## Configuration

Create a `.env` file in project root.

Required:

```env
LEETCODE_REPO_PATH=/absolute/path/to/your/leetcode-repo
```

Common settings:

```env
GITHUB_REPO_URL=https://github.com/your-user/your-repo

OLLAMA_URL=http://localhost:11434
OLLAMA_GENERATE_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=mistral

LLM_NUM_PREDICT=800
LLM_TEMPERATURE=0.2
LLM_TIMEOUT_SECONDS=600

PROMPT_VERSION=v1.0.0
PROMPT_STRATEGY=analysis_only_append_code_v1
TITLE_LETTER_COUNT=75
```

Optional legacy key:

```env
GEMINI_API_KEY=
```

## Installation

```bash
pip install -r requirements.txt
```

You also need Ollama installed and running locally.

## How To Run

### Preferred launcher

```bash
python run_current.py ui
python run_current.py cli
python run_current.py bulk
python run_current.py status
```

### Direct entry points

```bash
python autosync.py
streamlit run ui_app.py
```

### Legacy launcher

```bash
python run_legacy.py --list
python run_legacy.py autosync_v1
python run_legacy.py autosync_v2
python run_legacy.py autosync_v3
python run_legacy.py bulk_v1
python run_legacy.py llm_v1
```

## Assumptions and Caveats

- `LEETCODE_REPO_PATH` must point to an existing repository that has `easy/`, `medium/`, and `hard/` folders plus a top-level README.
- Git tab uses force push (`git push -f`). Use with caution.
- CLI autosync imports `winsound` (Windows-specific). UI mode is the safest default across platforms.
- Metrics export runs frequently; if Excel file is open, fallback export naming is used.
- Root-level modules are compatibility shims; active code is under `current/` and `services/`.

## Quick Start

1. Set `.env` with your repository path and Ollama config.
2. Run `python run_current.py ui`.
3. Open Generate tab and submit one problem.
4. Confirm output markdown in `copy_paste_solution/`.
5. Review run analytics in Metrics tab.
6. Push from Git tab when ready.

## Legacy and Versioning Notes

- Archived snapshots are stored under `archive/legacy_versions/`.
- Use `run_current.py` for active workflows.
- Use `run_legacy.py` only when you intentionally want older behavior.
