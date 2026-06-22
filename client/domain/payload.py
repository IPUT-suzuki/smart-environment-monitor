from datetime import datetime

from config.settings import CLIENT_ID, CLIENT_REGION
from domain.health import JST
from domain.models import SensorData, ServerSendData


def build_sensor_payload(sensor_data: SensorData, session_id: str, sequence: int) -> ServerSendData:
    """Build the stable TCP payload consumed by the existing server."""
    return {
        "client_id": CLIENT_ID,
        "region": CLIENT_REGION,
        "datetime": datetime.now(JST).strftime("%Y-%m-%d %A %H:%M:%S"),
        "session_id": session_id,
        "sequence": sequence,
        "sensor_data": sensor_data,
    }
