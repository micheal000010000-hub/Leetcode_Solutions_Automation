import os
from typing import Dict, List

import requests

from config import OLLAMA_BASE_URL, OLLAMA_MODEL
from services.metrics_service import get_metrics_paths


def check_ollama_health(timeout_seconds: int = 4) -> Dict[str, str]:
    tags_url = f"{OLLAMA_BASE_URL}/api/tags"
    try:
        response = requests.get(tags_url, timeout=timeout_seconds)
        if response.status_code != 200:
            return {
                "reachable": "False",
                "message": f"Ollama reachable but returned {response.status_code}",
                "model_loaded": "Unknown",
                "models": "",
            }

        payload = response.json() if response.content else {}
        models_payload: List[Dict] = payload.get("models", [])
        model_names = [m.get("name", "") for m in models_payload if isinstance(m, dict)]
        target_present = any(OLLAMA_MODEL in name for name in model_names)

        return {
            "reachable": "True",
            "message": "Ollama is reachable",
            "model_loaded": str(target_present),
            "models": ", ".join(model_names[:8]),
        }

    except requests.exceptions.Timeout:
        return {
            "reachable": "False",
            "message": "Connection timed out",
            "model_loaded": "Unknown",
            "models": "",
        }
    except requests.exceptions.RequestException as exc:
        return {
            "reachable": "False",
            "message": f"Connection failed: {str(exc)}",
            "model_loaded": "Unknown",
            "models": "",
        }


def get_project_runtime_snapshot() -> Dict[str, str]:
    paths = get_metrics_paths()
    stats_dir = paths["stats_dir"]
    copy_dir = os.path.join(os.path.dirname(stats_dir), "copy_paste_solution")

    return {
        "stats_dir_exists": str(os.path.exists(stats_dir)),
        "metrics_db_exists": str(os.path.exists(paths["db_path"])),
        "excel_exists": str(os.path.exists(paths["excel_path"])),
        "copy_folder_exists": str(os.path.exists(copy_dir)),
        "metrics_db_path": paths["db_path"],
        "excel_path": paths["excel_path"],
    }
