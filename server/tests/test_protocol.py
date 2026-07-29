import unittest

from server.domain.protocol import validate_payload


def valid_payload():
    return {
        "client_id": "client-a",
        "region": "tokyo",
        "datetime": "2026-07-29 10:00:00",
        "session_id": "session-a",
        "sequence": 1,
        "sensor_data": {"temperature": 25.0, "humidity": 50.0, "pressure": 1000.0, "co2": 500},
    }


class ProtocolValidationTest(unittest.TestCase):
    def test_accepts_complete_finite_payload(self):
        self.assertIsNone(validate_payload(valid_payload()))

    def test_rejects_non_finite_measurement_values(self):
        for value in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=value):
                payload = valid_payload()
                payload["sensor_data"]["temperature"] = value
                self.assertEqual(validate_payload(payload), "sensor_data.temperature must be a finite number")

    def test_rejects_boolean_measurement_value(self):
        payload = valid_payload()
        payload["sensor_data"]["co2"] = True
        self.assertEqual(validate_payload(payload), "sensor_data.co2 must be a finite number")

    def test_rejects_incomplete_or_unknown_measurement_fields(self):
        payload = valid_payload()
        payload["sensor_data"].pop("humidity")
        self.assertEqual(validate_payload(payload), "sensor_data.humidity is required")

        payload = valid_payload()
        payload["sensor_data"]["voltage"] = 3.3
        self.assertEqual(
            validate_payload(payload),
            "sensor_data contains unsupported fields: voltage",
        )

    def test_rejects_measurement_precision_different_from_sensor_output(self):
        invalid_values = {
            "temperature": 25.12,
            "humidity": 50.12,
            "pressure": 1000.12,
            "co2": 500.0,
        }
        for field, value in invalid_values.items():
            with self.subTest(field=field):
                payload = valid_payload()
                payload["sensor_data"][field] = value
                self.assertIsNotNone(validate_payload(payload))
