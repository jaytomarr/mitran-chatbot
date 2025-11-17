import os
from dotenv import load_dotenv
load_dotenv(override=False)


def get_env_bool(name: str, default: bool) -> bool:
    val = os.environ.get(name)
    if val is None:
        return default
    return str(val).strip().lower() in {"1", "true", "yes", "on"}


MODEL_NAME = os.environ.get("MODEL_NAME", "gemini-2.5-flash")
GOOGLE_SEARCH_TOOL_ENABLED = get_env_bool("GOOGLE_SEARCH_TOOL_ENABLED", True)
SESSION_MAX_TURNS = int(os.environ.get("SESSION_MAX_TURNS", "12"))
SYSTEM_PROMPT_PATH = os.environ.get("SYSTEM_PROMPT_PATH", os.path.join("prompts", "system.txt"))
GEMINI_API_KEY_ENV = "GEMINI_API_KEY"