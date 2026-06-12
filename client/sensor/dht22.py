from . import dht22_takemoto as dht22


def get_dht_data(gpio:int) -> tuple[float, float]:
    if not gpio:
        raise ValueError("DHT22 GPIO pin is not set. Please check config.py")
    dht22_instance = dht22.DHT22(gpio)
    tempe,hum,check = dht22_instance.read()
    return float(tempe), float(hum)
