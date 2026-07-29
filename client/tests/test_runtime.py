import unittest
from unittest.mock import patch

from client.app.runtime import MonitorRuntime, SensorSuite


class StaticSensor:
    def __init__(self, reading):
        self.reading = reading

    def read(self):
        return self.reading

    def close(self):
        pass


class SequenceSensor(StaticSensor):
    def __init__(self, readings):
        self.readings = iter(readings)

    def read(self):
        return next(self.readings)


class MonitorRuntimeTest(unittest.TestCase):
    def test_non_finite_sensor_value_skips_payload_and_marks_only_that_sensor_failed(self):
        sensors = SensorSuite(
            dht22=StaticSensor({"temperature": float("nan"), "humidity": 50.0}),
            bme280=StaticSensor({"pressure": 1000.0}),
            mhz19c=StaticSensor({"co2": 500}),
        )
        runtime = MonitorRuntime(sensors, notifications_enabled=False)

        with patch("client.app.runtime.send_to_server") as sender:
            self.assertFalse(runtime.run_once())

        sender.assert_not_called()
        self.assertEqual(runtime.health.sensor.dht22.fail_count, 1)
        self.assertEqual(runtime.health.sensor.bme280.read_count, 1)
        self.assertEqual(runtime.health.sensor.mhz19c.read_count, 1)

    def test_failure_notification_is_thresholded_and_recovery_is_sent_once(self):
        sensors = SensorSuite(StaticSensor(None), StaticSensor(None), StaticSensor(None))
        runtime = MonitorRuntime(sensors, notifications_enabled=True)

        with patch("client.app.runtime.notify_discord", return_value=True) as notify:
            runtime._notify_failure("sensor:dht22", 2, 1, "failed", [])
            runtime._notify_failure("sensor:dht22", 2, 2, "failed", [])
            runtime._notify_failure("sensor:dht22", 2, 3, "failed", [])
            runtime._notify_recovery("sensor:dht22", "recovered", 3)
            runtime._notify_recovery("sensor:dht22", "recovered", 3)

        self.assertEqual(notify.call_count, 2)

    def test_sensor_recovers_on_the_next_cycle_without_partial_first_payload(self):
        sensors = SensorSuite(
            dht22=SequenceSensor([None, {"temperature": 25.0, "humidity": 50.0}]),
            bme280=SequenceSensor([{"pressure": 1000.0}, {"pressure": 1000.0}]),
            mhz19c=SequenceSensor([{"co2": 500}, {"co2": 500}]),
        )
        runtime = MonitorRuntime(sensors, notifications_enabled=False)

        with patch("client.app.runtime.send_to_server", return_value=1) as sender:
            self.assertFalse(runtime.run_once())
            self.assertTrue(runtime.run_once())

        self.assertEqual(sender.call_count, 1)
        self.assertEqual(runtime.health.sensor.dht22.consecutive_fail_count, 0)
        self.assertEqual(runtime.health.sensor.dht22.read_count, 1)

    def test_start_and_normal_stop_notifications_are_emitted(self):
        sensors = SensorSuite(
            dht22=StaticSensor({"temperature": 25.0, "humidity": 50.0}),
            bme280=StaticSensor({"pressure": 1000.0}),
            mhz19c=StaticSensor({"co2": 500}),
        )
        runtime = MonitorRuntime(sensors, notifications_enabled=True)

        with patch("client.app.runtime.send_to_server", return_value=1), patch("client.app.runtime.notify_discord", return_value=True) as notify:
            runtime.run_forever(iterations=1, interval=0)

        titles = [call.args[1]["embeds"][0]["title"] for call in notify.call_args_list]
        self.assertEqual(titles, ["Client started", "Client stopped"])
