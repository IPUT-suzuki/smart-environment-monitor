from dataclasses import dataclass, field
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
    session_id: str
    sequence: int
    sensor_data: SensorData


@dataclass
class ClientMetaData:
    client_id: str
    region: str


@dataclass
class ServerSendHealth:
    success: bool = False
    success_count: int = 0
    received_count: int = 0
    last_ack_sequence: int = 0
    fail_count: int = 0
    consecutive_fail_count: int = 0
    last_success_at: str = ""
    last_failed_at: str = ""
    last_status_code: int = 0
    error: str = ""


@dataclass
class HealthReportHealth:
    success: bool = False
    success_count: int = 0
    fail_count: int = 0
    consecutive_fail_count: int = 0
    last_success_at: str = ""
    last_failed_at: str = ""
    last_status_code: int = 0
    error: str = ""


@dataclass
class ClientRuntimeHealth:
    started_at: str
    last_loop_at: str = ""
    loop_count: int = 0
    uptime_seconds: int = 0


@dataclass
class SensorHealth:
    name: str
    connect: bool = False
    read: bool = False
    read_count: int = 0
    fail_count: int = 0
    consecutive_fail_count: int = 0
    last_success_at: str = ""
    last_failed_at: str = ""
    error: str = ""


@dataclass
class SensorHeartBeat:
    bme280: SensorHealth = field(default_factory=lambda: SensorHealth("BME280"))
    dht22: SensorHealth = field(default_factory=lambda: SensorHealth("DHT22"))
    mhz19c: SensorHealth = field(default_factory=lambda: SensorHealth("MHZ19C"))


@dataclass
class ClientHeartBeat:
    client: ClientMetaData
    runtime: ClientRuntimeHealth
    sensor: SensorHeartBeat = field(default_factory=SensorHeartBeat)
    server_send: ServerSendHealth = field(default_factory=ServerSendHealth)
    health_report: HealthReportHealth = field(default_factory=HealthReportHealth)
