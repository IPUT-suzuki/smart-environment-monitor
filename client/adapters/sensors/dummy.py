import random


def _move_value(
    value: float,
    min_value: float,
    max_value: float,
    step: float,
    digits: int = 1,
    stay_rate: float = 0.2,
) -> float:
    """
    前回値から少しだけ上下させる。
    stay_rate の確率で前回値のままにする。
    """

    # たまに前回値のまま返す
    if random.random() < stay_rate:
        return round(value, digits)

    value += random.uniform(-step, step)

    if value < min_value:
        value = min_value
    elif value > max_value:
        value = max_value

    return round(value, digits)


class DummyDHT22Sensor:
    def __init__(self):
        self.temperature = random.uniform(24.0, 26.0)
        self.humidity = random.uniform(45.0, 55.0)

    def read(self) -> dict[str, float]:
        self.temperature = _move_value(
            value=self.temperature,
            min_value=20.0,
            max_value=35.0,
            step=0.2,
            digits=1,
            stay_rate=0.3,
        )

        self.humidity = _move_value(
            value=self.humidity,
            min_value=30.0,
            max_value=80.0,
            step=0.5,
            digits=1,
            stay_rate=0.2,
        )

        return {
            "temperature": self.temperature,
            "humidity": self.humidity,
        }

    def close(self) -> None:
        return None


class DummyBME280Sensor:
    def __init__(self):
        self.pressure = random.uniform(1000.0, 1020.0)

    def read(self) -> dict[str, float]:
        self.pressure = _move_value(
            value=self.pressure,
            min_value=950.0,
            max_value=1050.0,
            step=0.3,
            digits=1,
            stay_rate=0.4,
        )

        return {
            "pressure": self.pressure,
        }

    def close(self) -> None:
        return None


class DummyMHZ19CSensor:
    def __init__(self):
        self.co2 = random.uniform(400, 600)

    def read(self) -> dict[str, int]:
        self.co2 = _move_value(
            value=self.co2,
            min_value=400,
            max_value=1200,
            step=10,
            digits=0,
            stay_rate=0.3,
        )

        return {
            "co2": int(self.co2),
        }

    def close(self) -> None:
        return None