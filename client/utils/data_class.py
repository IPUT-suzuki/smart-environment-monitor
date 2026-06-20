from typing import TypedDict
from dataclasses import dataclass, field
from config.settings import CLIENT_ID, CLIENT_REGION


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


# クライアント側の基本的なデータに関する定義
@dataclass
class ClientMetaData:
    client_id: str
    region: str


# サーバー送信状態
@dataclass
class ServerSendHealth:
    success: bool = False
    fail_count: int = 0
    consecutive_fail_count: int = 0
    last_success_at: str = ""
    last_failed_at: str = ""
    last_status_code: int = 0
    error: str = ""


# クライアントのプログラム全体の稼働状況
@dataclass
class ClientRuntimeHealth:
    started_at: str
    last_loop_at: str = ""
    loop_count: int = 0
    uptime_seconds: int = 0


# センサーの稼働状況に関する項目に関する定義
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


# クライアント側の各センサー稼働状況に関する定義
@dataclass
class SensorHeartBeat:
    bme280: SensorHealth = field(default_factory=lambda: SensorHealth("BME280"))
    dht22: SensorHealth = field(default_factory=lambda: SensorHealth("DHT22"))
    mhz19c: SensorHealth = field(default_factory=lambda: SensorHealth("MHZ19C"))


# 送信する形式
@dataclass
class ClientHeartBeat:
    client: ClientMetaData = field(default_factory=ClientMetaData)
    sensor: SensorHeartBeat = field(default_factory=SensorHeartBeat)
    server_send: ServerSendHealth = field(default_factory=ServerSendHealth)
    runtime: ClientRuntimeHealth = field(default_factory=ClientRuntimeHealth)
