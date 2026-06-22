import logging

from adapters.sensors.lib.dht22_takemoto import DHT22, DHT22CRCError, DHT22MissingDataError

logger = logging.getLogger(__name__)


class DHT22Sensor:
    def __init__(self, gpio: int):
        self._sensor = DHT22(gpio)

    def read(self) -> dict[str, float] | None:
        try:
            temperature, humidity, _ = self._sensor.read()
            return {"temperature": round(temperature, 1), "humidity": round(humidity, 1)}
        except (DHT22CRCError, DHT22MissingDataError, OSError) as error:
            logger.warning("DHT22 read failed: %s", error)
            return None
        except Exception:
            logger.exception("unexpected DHT22 read failure")
            return None

    def close(self) -> None:
        self._sensor.close()
