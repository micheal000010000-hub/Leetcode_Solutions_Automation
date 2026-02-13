import os
from dotenv import load_dotenv

load_dotenv()

LEETCODE_REPO_PATH = os.getenv("LEETCODE_REPO_PATH")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not LEETCODE_REPO_PATH:
    raise ValueError("LEETCODE_REPO_PATH not set")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not set")