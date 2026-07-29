"""Validation rules shared by sensor TCP payloads and Web manual input."""

import math
from typing import Any


MEASUREMENT_FIELDS = ("temperature", "humidity", "pressure", "co2")
MEASUREMENT_DECIMAL_PLACES = {
    "temperature": 1,
    "humidity": 1,
    "pressure": 1,
    "co2": 0,
}


def _has_at_most_decimal_places(value: float, places: int) -> bool:
    scale = 10 ** places
    scaled = value * scale
    return math.isclose(scaled, round(scaled), rel_tol=0, abs_tol=1e-9)


def validate_measurement_data(
    values: Any,
    *,
    prefix: str = "sensor_data",
    reject_unknown: bool = True,
) -> str | None:
    """Validate the complete four-value snapshot emitted by the sensors."""
    if not isinstance(values, dict):
        return f"{prefix} must be an object"

    if reject_unknown:
        unknown = sorted(set(values) - set(MEASUREMENT_FIELDS))
        if unknown:
            return f"{prefix} contains unsupported fields: {', '.join(unknown)}"

    for field in MEASUREMENT_FIELDS:
        if field not in values:
            return f"{prefix}.{field} is required"
        value = values[field]
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(value)
        ):
            return f"{prefix}.{field} must be a finite number"

        decimal_places = MEASUREMENT_DECIMAL_PLACES[field]
        if decimal_places == 0:
            if not isinstance(value, int):
                return f"{prefix}.{field} must be an integer"
        elif not _has_at_most_decimal_places(float(value), decimal_places):
            return f"{prefix}.{field} must have at most {decimal_places} decimal place"

    return None
