from typing import Any

from common.measurement_schema import validate_measurement_data


def validate_payload(payload: Any) -> str | None:
    if not isinstance(payload, dict):
        return "payload must be a JSON object"
    for field in ("client_id", "region", "datetime", "session_id"):
        if not isinstance(payload.get(field), str) or not payload[field]:
            return f"{field} must be a non-empty string"
    sequence = payload.get("sequence")
    if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 1:
        return "sequence must be a positive integer"
    return validate_measurement_data(payload.get("sensor_data"))
