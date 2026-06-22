import random


class DummyDHT22Sensor:
    def read(self) -> dict[str, float]:
        return {
            "temperature": round(random.uniform(23.0, 30.0), 1),
            "humidity": round(random.uniform(39.0, 60.0), 1),
        }

    def close(self) -> None:
        return None


class DummyBME280Sensor:
    def read(self) -> dict[str, float]:
        return {"pressure": round(random.uniform(900.0, 1400.0), 1)}

    def close(self) -> None:
        return None


class DummyMHZ19CSensor:
    def read(self) -> dict[str, int]:
        return {"co2": round(random.uniform(500, 800))}

    def close(self) -> None:
        return None
