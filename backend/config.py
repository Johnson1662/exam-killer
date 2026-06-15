from pathlib import Path
import re

DATA_DIR = Path("data")
DB_PATH = Path("exam_killer.db")
MAX_PAGES = 30

ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx", ".png", ".jpg", ".jpeg"}
MAX_UPLOAD_SIZE = 200 * 1024 * 1024  # 200 MB


def sanitize_dirname(name: str) -> str:
    """Windows-illegal characters \\ / : * ? \" < > | replaced with space."""
    return re.sub(r'[\\/:*?"<>|]', ' ', name).strip()

# ── Default LLM provider (OpenCode Zen) ─────────────────────────────

DEFAULT_LLM_ENDPOINT = "https://opencode.ai/zen/v1"
DEFAULT_LLM_MODEL = "deepseek-v4-flash-free"
