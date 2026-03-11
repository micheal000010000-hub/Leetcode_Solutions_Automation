# Legacy Versions

This folder contains historical snapshots preserved for reference and independent execution.

## Run Legacy Targets

From project root:

```bash
python run_legacy.py --list
python run_legacy.py autosync_v1
python run_legacy.py autosync_v2
python run_legacy.py autosync_v3
python run_legacy.py bulk_v1
python run_legacy.py llm_v1
```

## Notes

- `run_legacy.py` ensures scripts execute with the project root as working directory.
- Environment variables from `.env` are still required for scripts that use `config.py`.

## Archived Module Snapshots

- `config_prev_version.py`
- `git_manager_prev_version.py`
- `autosync_prev_version.py`
- `autosync_prev_version_17_02_2026.py`
- `autosync_prev_version_21_02_2026.py`
- `bulk_generate_prev_version.py`
- `llm_generator_prev_version.py`
