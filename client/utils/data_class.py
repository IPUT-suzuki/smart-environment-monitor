from typing import TypedDict

class SensorData(TypedDict):
    temperature: float
    humidity: float
    pressure: float
    co2: int

class ServerSendData(TypedDict):
    client_id: str
    region: str
    datetime: str
    sensor_data: SensorData
