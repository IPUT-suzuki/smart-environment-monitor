from datetime import datetime

from client.config.settings import CLIENT_ID, CLIENT_REGION
from client.domain.health import JST
from client.domain.models import SensorData, ServerSendData


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
