"""Application settings loaded from environment variables."""
import os

# Configurable upload limit in Megabytes (default: 250 MB = 262,144,000 bytes)
MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", 250))
# If MAX_UPLOAD_BYTES is explicitly specified in env, use that; otherwise calculate from MB
MAX_UPLOAD_BYTES: int = int(os.getenv("MAX_UPLOAD_BYTES", MAX_UPLOAD_SIZE_MB * 1024 * 1024))

MAX_ANALYSIS_ROWS: int = int(os.getenv("MAX_ANALYSIS_ROWS", 20_000))
TESSERACT_CMD: str | None = os.getenv("TESSERACT_CMD")
ANTHROPIC_API_KEY: str | None = os.getenv("ANTHROPIC_API_KEY")
FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
