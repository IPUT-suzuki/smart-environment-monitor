"""Hardware and integration checks invoked by `main.py --mode test`."""
import logging
from collections.abc import Callable

from config.settings import BME280_ADDR, DHT22_GPIO, DISCORD_WEBHOOK_URL, SERIAL_BAUDRATE, SERIAL_PORT, SERIAL_TIMEOUT

logger = logging.getLogger(__name__)

# 関数に_を接頭詞につけることでできる限りこのファイル内のみで使うことを明示的にしている。
# 外部からでも使うことは可能だが今回の場合は内部でしか使わないので採用。
def _read_sensor(name: str, sensor) -> None:
    try:
        reading = sensor.read()
        if reading is None:
            raise RuntimeError(f"{name} read failed")
        logger.info("%s sensor test passed: %s", name, reading)
    finally:
        sensor.close()


def test_notification() -> None:
    from adapters.outbound.discord import notify_discord

    if not notify_discord(DISCORD_WEBHOOK_URL, "smart-environment-monitor notification test"):
        raise RuntimeError("Discord notification test failed")


def test_dht22() -> None:
    from adapters.sensors.dht22 import DHT22Sensor

    sensor = DHT22Sensor(DHT22_GPIO)
    _read_sensor("DHT22", sensor)


def test_bme280() -> None:
    from adapters.sensors.bme280 import BME280Sensor

    sensor = BME280Sensor(BME280_ADDR)
    _read_sensor("BME280", sensor)


def test_mhz19c() -> None:
    from adapters.sensors.mhz19c import MHZ19CSensor

    sensor = MHZ19CSensor(SERIAL_PORT, SERIAL_BAUDRATE, SERIAL_TIMEOUT)
    _read_sensor("MH-Z19C", sensor)


TEST_TARGETS: dict[str, Callable[[], None]] = {
    "notification": test_notification,
    "dht22": test_dht22,
    "bme280": test_bme280,
    "mhz19c": test_mhz19c,
}


def run_test_target(target: str | None) -> None:
    if target == "all":
        for test in TEST_TARGETS.values():
            test()
        return
    try:
        TEST_TARGETS[target]()  # type: ignore[index]
    except KeyError as error:
        available = ", ".join((*TEST_TARGETS, "all"))
        raise ValueError(f"test mode requires --target one of: {available}") from error
