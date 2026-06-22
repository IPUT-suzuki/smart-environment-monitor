import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=True)


def require_env(name):  # .envにデータが設定されているかチェック
    value = os.getenv(name)
    if not value:
        raise ValueError(f"{name} is not set. Please check .env")
    return value


def env_int(name, default, minimum=0, base=10):
    value = os.getenv(name)
    if value in (None, ""):
        return default
    try:
        parsed = int(value, base)
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


SERVER_ADDR = require_env("SERVER_ADDR")
SERVER_PORT = env_int("SERVER_PORT", int(require_env("SERVER_PORT")), minimum=1)

WEB_HEALTH_URL = os.getenv("WEB_HEALTH_URL")
CLIENT_REGION = require_env("CLIENT_REGION")
CLIENT_ID = require_env("CLIENT_ID")

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

DEFAULT_SEND_INTERVAL = env_float("SEND_INTERVAL_SECONDS", 4)
HEARTBEAT_INTERVAL = env_float("HEARTBEAT_INTERVAL_SECONDS", 10)
SENSOR_FAILURE_NOTIFY_THRESHOLD = env_int("SENSOR_FAILURE_NOTIFY_THRESHOLD", 3, minimum=1)
HEALTH_REPORT_FAILURE_NOTIFY_THRESHOLD = env_int("HEALTH_REPORT_FAILURE_NOTIFY_THRESHOLD", 3, minimum=1)
SERVER_SEND_FAILURE_NOTIFY_THRESHOLD = env_int("SERVER_SEND_FAILURE_NOTIFY_THRESHOLD", 3, minimum=1)

TCP_TIMEOUT_SECONDS = env_float("TCP_TIMEOUT_SECONDS", 5)
WEB_HEALTH_TIMEOUT_SECONDS = env_float("WEB_HEALTH_TIMEOUT_SECONDS", 5)
DISCORD_TIMEOUT_SECONDS = env_float("DISCORD_TIMEOUT_SECONDS", 5)

# dht22関連設定
DHT22_GPIO = env_int("DHT22_GPIO", 26)

# mh_z19c関連設定
SERIAL_PORT = os.getenv("SERIAL_PORT", "/dev/serial0")
SERIAL_BAUDRATE = env_int("SERIAL_BAUDRATE", 9600, minimum=1)
SERIAL_TIMEOUT = env_float("SERIAL_TIMEOUT_SECONDS", 1)

# bme280関連設定
BME280_ADDR = env_int("BME280_ADDR", 0x76, base=0)
