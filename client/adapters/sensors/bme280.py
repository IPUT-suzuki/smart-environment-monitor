import logging

import board
import busio
from adafruit_bme280 import basic as adafruit_bme280

logger = logging.getLogger(__name__)


class BME280Sensor:
    def __init__(self, address: int):
        i2c = busio.I2C(board.SCL, board.SDA)
        self._sensor = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=address)

    def read(self) -> dict[str, float] | None:
        try:
            return {"pressure": round(self._sensor.pressure, 1)}
        except Exception as error:
            logger.warning("BME280 read failed: %s", error)
            return None

    def close(self) -> None:
        return None
