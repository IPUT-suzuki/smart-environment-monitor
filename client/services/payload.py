import datetime

from config import CLIENT_ID, CLIENT_REGION


def build_payload(sensor_data: dict) -> dict:
    return {
        "client_id": CLIENT_ID,
        "region": CLIENT_REGION,
        "datetime": datetime.datetime.now().isoformat(),
        "sensor_data": sensor_data,
    }
