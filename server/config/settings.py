import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=True)


def require_env(name):  # .envにデータが設定されているかチェック
    value = os.getenv(name)
    if not value:
        raise ValueError(f"{name} is not set. Please check .env")
    return value


SERVER_ADDR = require_env("SERVER_ADDR")
SERVER_PORT = int(require_env("SERVER_PORT"))
