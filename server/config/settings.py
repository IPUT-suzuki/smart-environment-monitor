import os
import math
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=True)
BASE_DIR = Path(__file__).resolve().parents[2]


def require_env(name):  # .envにデータが設定されているかチェック
    value = os.getenv(name)
    if not value:
        raise ValueError(f"{name} is not set. Please check .env")
    return value


def env_int(name, default, minimum=0):
    value = os.getenv(name)
    if value in (None, ""):
        return default
    try:
        parsed = int(value)
    except ValueError as error:
        raise ValueError(f"{name} must be an integer") from error
    if parsed < minimum:
        raise ValueError(f"{name} must be at least {minimum}")
    return parsed


def env_float(name, default, minimum=0):
    value = os.getenv(name)
    if value in (None, ""):
        return default
    try:
        parsed = float(value)
    except ValueError as error:
        raise ValueError(f"{name} must be a number") from error
    if not math.isfinite(parsed) or parsed <= minimum:
        raise ValueError(f"{name} must be greater than {minimum}")
    return parsed


def env_path(name, default):
    path = Path(os.getenv(name, default))
    return path if path.is_absolute() else BASE_DIR / path


SERVER_ADDR = os.getenv("SERVER_ADDR", "0.0.0.0")
SERVER_PORT = env_int("SERVER_PORT", 9000, minimum=1)
SENSOR_DATA_PATH = env_path("SENSOR_DATA_PATH", "data/sensor_data.csv")
TCP_ACCEPT_TIMEOUT_SECONDS = env_float("TCP_ACCEPT_TIMEOUT_SECONDS", 0.5)
TCP_CONNECTION_TIMEOUT_SECONDS = env_float("TCP_CONNECTION_TIMEOUT_SECONDS", 10)
TCP_MAX_REQUEST_BYTES = env_int("TCP_MAX_REQUEST_BYTES", 1_048_576, minimum=1)
TCP_SHUTDOWN_TIMEOUT_SECONDS = env_float("TCP_SHUTDOWN_TIMEOUT_SECONDS", 2)
CSV_LOCK_TIMEOUT_SECONDS = env_float("CSV_LOCK_TIMEOUT_SECONDS", 5)
CSV_LOCK_STALE_AFTER_SECONDS = env_float("CSV_LOCK_STALE_AFTER_SECONDS", 60)
