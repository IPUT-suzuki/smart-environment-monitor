import logging

from adapters.sensors.dummy import DummyBME280Sensor, DummyDHT22Sensor, DummyMHZ19CSensor
from app.runtime import MonitorRuntime, SensorSuite
from config.settings import BME280_ADDR, DHT22_GPIO, SERIAL_BAUDRATE, SERIAL_PORT, SERIAL_TIMEOUT
from tests.targets import run_test_target

logger = logging.getLogger(__name__)


def run_main_mode(args) -> None:
    from adapters.sensors.bme280 import BME280Sensor
    from adapters.sensors.dht22 import DHT22Sensor
    from adapters.sensors.mhz19c import MHZ19CSensor

    sensors = SensorSuite(
        dht22=DHT22Sensor(DHT22_GPIO),
        bme280=BME280Sensor(BME280_ADDR),
        mhz19c=MHZ19CSensor(SERIAL_PORT, SERIAL_BAUDRATE, SERIAL_TIMEOUT),
    )
    logger.info("start main mode")
    logger.debug(
        "mode args: mode=main server=%s:%s iterations=%s interval=%s notifications_enabled=%s",
        args.server_addr or "configured",
        args.server_port or "configured",
        args.iterations,
        args.interval,
        not args.no_notify,
    )
    MonitorRuntime(sensors, args.server_addr, args.server_port, not args.no_notify, mode_name="main").run_forever(args.iterations, args.interval)


def run_mock_mode(args) -> None:
    sensors = SensorSuite(DummyDHT22Sensor(), DummyBME280Sensor(), DummyMHZ19CSensor())
    logger.info("start mock mode")
    logger.debug(
        "mode args: mode=mock server=%s:%s iterations=%s interval=%s notifications_enabled=%s",
        args.server_addr or "configured",
        args.server_port or "configured",
        args.iterations,
        args.interval,
        not args.no_notify,
    )
    MonitorRuntime(sensors, args.server_addr, args.server_port, not args.no_notify, mode_name="mock").run_forever(args.iterations, args.interval)


def run_test_mode(args) -> None:
    logger.debug("mode args: mode=test target=%s", args.target)
    run_test_target(args.target)
