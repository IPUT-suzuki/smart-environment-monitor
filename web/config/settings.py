import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=True)


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
    if parsed <= minimum:
        raise ValueError(f"{name} must be greater than {minimum}")
    return parsed


def env_bool(name, default=False):
    value = os.getenv(name)
    if value in (None, ""):
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"{name} must be a boolean")


def env_path(name, default):
    path = Path(os.getenv(name, default))
    return path if path.is_absolute() else BASE_DIR / path


WEB_HOST = os.getenv("WEB_HOST", "0.0.0.0")
WEB_PORT = env_int("WEB_PORT", 5000, minimum=1)
WEB_DEBUG = env_bool("WEB_DEBUG", False)
SENSOR_DATA_PATH = env_path("SENSOR_DATA_PATH", "data/sensor_data.csv")
HEALTH_HISTORY_PATH = env_path("HEALTH_HISTORY_PATH", "data/health_history.csv")
HEALTH_OFFLINE_AFTER_SECONDS = env_float("HEALTH_OFFLINE_AFTER_SECONDS", 30)
HEALTH_STREAM_RETRY_MILLISECONDS = env_int("HEALTH_STREAM_RETRY_MILLISECONDS", 3000, minimum=1)
HEALTH_STREAM_KEEPALIVE_SECONDS = env_float("HEALTH_STREAM_KEEPALIVE_SECONDS", 15)
