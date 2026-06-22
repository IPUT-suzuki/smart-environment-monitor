from typing import Any

SENSOR_FIELDS = ("temperature", "humidity", "pressure", "co2")


def validate_payload(payload: Any) -> str | None:
    if not isinstance(payload, dict):
        return "payload must be a JSON object"
    for field in ("client_id", "region", "datetime", "session_id"):
        if not isinstance(payload.get(field), str) or not payload[field]:
            return f"{field} must be a non-empty string"
    sequence = payload.get("sequence")
    if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 1:
        return "sequence must be a positive integer"
    sensor_data = payload.get("sensor_data")
    if not isinstance(sensor_data, dict):
        return "sensor_data must be an object"
    for field in SENSOR_FIELDS:
        value = sensor_data.get(field)
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return f"sensor_data.{field} must be a number"
    return None
