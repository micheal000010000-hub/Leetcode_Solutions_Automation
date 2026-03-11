import os
from dotenv import load_dotenv

load_dotenv()

LEETCODE_REPO_PATH = os.getenv("LEETCODE_REPO_PATH")

GITHUB_REPO_URL = os.getenv("GITHUB_REPO_URL", "")

# Optional legacy key. Kept for backward compatibility if Gemini is re-enabled.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

OLLAMA_BASE_URL = os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/")
OLLAMA_GENERATE_URL = os.getenv("OLLAMA_GENERATE_URL", f"{OLLAMA_BASE_URL}/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")

LLM_NUM_PREDICT = int(os.getenv("LLM_NUM_PREDICT", "800"))
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.2"))
LLM_TIMEOUT_SECONDS = int(os.getenv("LLM_TIMEOUT_SECONDS", "600"))
PROMPT_VERSION = os.getenv("PROMPT_VERSION", "v1.0.0")
PROMPT_STRATEGY = os.getenv("PROMPT_STRATEGY", "analysis_only_append_code_v1")

if not LEETCODE_REPO_PATH:
    raise ValueError("LEETCODE_REPO_PATH not set")
