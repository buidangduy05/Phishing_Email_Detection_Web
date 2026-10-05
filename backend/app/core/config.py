import os
from pathlib import Path


APP_NAME = "Mailguard Email Analysis API"
MAX_UPLOAD_SIZE = 20 * 1024 * 1024
ARTIFACTS_DIR = Path(__file__).resolve().parents[2] / "artifacts"


def get_allowed_origins() -> list[str]:
    configured_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173")
    return [origin.strip() for origin in configured_origins.split(",") if origin.strip()]
