import board
import busio
from adafruit_bme280 import basic as adafruit_bme280

def get_bme280_data(address):
    if not address:
        raise ValueError("BME280 I2C address is not set. Please check config.py")
    i2c = busio.I2C(board.SCL, board.SDA)
    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=address)
    return bme280.pressure
