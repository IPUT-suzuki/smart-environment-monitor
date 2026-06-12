import socket
import datetime
import time
import json
import lgpio
from sensor.dht22 import get_dht_data
from sensor.mh_z19c import get_mhz19c_data,MHZ19CReadError
from sensor.bme280 import get_bme280_data
from sensor.dht22_takemoto import DHT22CRCError,DHT22MissingDataError

try:
    from config import *
except ValueError as e:
    print(e)
    exit(1)

while True:
    try:
        time.sleep(DEFAULT_SEND_INTERVAL)
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((SERVER_ADDR, SERVER_PORT))
        tempe, humid = get_dht_data(DHT22_GPIO)
        co2 = get_mhz19c_data(SERIAL_PORT,SERIAL_BAUDRATE,SERIAL_TIMEOUT)
        pressure = get_bme280_data(BME280_ADDR)
        timestamp = datetime.datetime.now().isoformat()
        rowData = {
            "time": timestamp,
            "region": CLIENT_REGION,
            "id":CLIENT_ID,
            "tempe": tempe,
            "humid": humid,
            "CO2": co2,
            "pressure":pressure
        }
        print(rowData)
        payload = json.dumps(rowData).encode("utf-8")
        conn.sendall(payload)
        conn.close()
        
    except socket.error as e:
        conn.close()
        print(e)
        break
    except lgpio.error as e:
        print(e)
    except DHT22MissingDataError as e:
        print(e)
    except DHT22CRCError as e:
        print(e)
    except MHZ19CReadError as e:
        print(e)