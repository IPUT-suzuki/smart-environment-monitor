import logging
import time
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Protocol

from adapters.outbound.discord import notify_discord
from adapters.outbound.health import send_heartbeat
from adapters.outbound.tcp import send_to_server
from app.logging import log_debug_data
from config.settings import (
    CLIENT_ID,
    CLIENT_REGION,
    DEFAULT_SEND_INTERVAL,
    DISCORD_WEBHOOK_URL,
    HEALTH_REPORT_FAILURE_NOTIFY_THRESHOLD,
    HEARTBEAT_INTERVAL,
    SENSOR_FAILURE_NOTIFY_THRESHOLD,
    SERVER_SEND_FAILURE_NOTIFY_THRESHOLD,
)
from domain.health import JST, now_string, record_health_report, record_send_failure, record_send_success, update_sensor_health
from domain.models import ClientHeartBeat, ClientMetaData, ClientRuntimeHealth, SensorData
from domain.payload import build_sensor_payload

logger = logging.getLogger(__name__)


class Sensor(Protocol):
    def read(self) -> dict | None: ...
    def close(self) -> None: ...


@dataclass
class SensorSuite:
    dht22: Sensor
    bme280: Sensor
    mhz19c: Sensor

    def close(self) -> None:
        self.dht22.close()
        self.bme280.close()
        self.mhz19c.close()


def build_notification(title: str, color: int, fields: list[tuple[str, str]], health: ClientHeartBeat) -> dict:
    return {
        "embeds": [{
            "title": title,
            "color": color,
            "fields": [
                {"name": "Client ID", "value": health.client.client_id, "inline": True},
                {"name": "Region", "value": health.client.region, "inline": True},
                {"name": "Datetime", "value": now_string(), "inline": False},
                *({"name": name, "value": value, "inline": False} for name, value in fields),
            ],
        }]
    }


# main+mock実行部分
class MonitorRuntime:
    def __init__(
        self,
        sensors: SensorSuite,
        server_addr: str | None = None,
        server_port: int | None = None,
        notifications_enabled: bool = True,
        mode_name: str = "main",
    ):
        started_at = now_string()
        self.sensors = sensors
        self.server_addr = server_addr
        self.server_port = server_port
        self.session_id = str(uuid.uuid4())
        self.sequence = 0
        self.notifications_enabled = notifications_enabled
        self.mode_name = mode_name
        self.health = ClientHeartBeat(
            client=ClientMetaData(client_id=CLIENT_ID, region=CLIENT_REGION),
            runtime=ClientRuntimeHealth(started_at=started_at),
        )
        self._alerted: set[str] = set()

    def _notify_failure(self, key: str, threshold: int, count: int, title: str, fields: list[tuple[str, str]]) -> None:
        if count == threshold:
            self._alerted.add(key)
            self._send_notification(title, 0xE74C3C, fields)

    def _notify_recovery(self, key: str, title: str, failure_count: int) -> None:
        if key in self._alerted:
            self._alerted.remove(key)
            self._send_notification(title, 0x2ECC71, [("Failure Count", str(failure_count))])

    def _send_notification(self, title: str, color: int, fields: list[tuple[str, str]]) -> None:
        payload = build_notification(title, color, fields, self.health)
        if self.notifications_enabled:
            log_debug_data(logger, "discord event queued", {"title": title, "payload": payload})
            notify_discord(DISCORD_WEBHOOK_URL, payload)
            return
        log_debug_data(logger, "discord event skipped by --no-notify", {"title": title, "payload": payload})

    def _log_sensor_debug(self, name: str, data: dict | None, error: str) -> None:
        if data is None:
            logger.debug("sensor read failed: sensor=%s error=%s", name, error)
            return
        log_debug_data(logger, "sensor read success", {"sensor": name, "data": data})

    def _log_health_snapshot(self, label: str) -> None:
        log_debug_data(logger, f"health snapshot ({label})", asdict(self.health))

    def run_once(self) -> bool:
        """Read all sensors and send only a complete sensor snapshot."""
        self.health.runtime.loop_count += 1
        self.health.runtime.last_loop_at = now_string()
        self.health.runtime.uptime_seconds = int(datetime.now(JST).timestamp() - datetime.fromisoformat(self.health.runtime.started_at).timestamp())
        logger.debug(
            "loop start: mode=%s loop_count=%d uptime_seconds=%d session_id=%s",
            self.mode_name,
            self.health.runtime.loop_count,
            self.health.runtime.uptime_seconds,
            self.session_id,
        )

        dht_data = self.sensors.dht22.read()
        bme_data = self.sensors.bme280.read()
        mhz_data = self.sensors.mhz19c.read()
        readings = (
            ("dht22", dht_data, self.health.sensor.dht22, "DHT22 read failed"),
            ("bme280", bme_data, self.health.sensor.bme280, "BME280 read failed"),
            ("mhz19c", mhz_data, self.health.sensor.mhz19c, "MH-Z19C read failed"),
        )
        for name, data, sensor_health, error in readings:
            update_sensor_health(sensor_health, data is not None, error)
            self._log_sensor_debug(name, data, error)
            if data is None:
                logger.warning("%s: consecutive_fail_count=%d", error, sensor_health.consecutive_fail_count)
                self._notify_failure(
                    f"sensor:{name}", SENSOR_FAILURE_NOTIFY_THRESHOLD, sensor_health.consecutive_fail_count,
                    f"Sensor error: {name}", [("Consecutive Failures", str(sensor_health.consecutive_fail_count)), ("Error", error)],
                )
            else:
                self._notify_recovery(f"sensor:{name}", f"Sensor recovered: {name}", sensor_health.fail_count)
        self._log_health_snapshot("after_sensor_reads")

        if any(data is None for _, data, _, _ in readings):
            logger.info("sensor payload skipped: at least one sensor read failed")
            return False

        sensor_data: SensorData = {
            "temperature": dht_data["temperature"],
            "humidity": dht_data["humidity"],
            "pressure": bme_data["pressure"],
            "co2": mhz_data["co2"],
        }
        self.sequence += 1
        payload = build_sensor_payload(sensor_data, self.session_id, self.sequence)
        log_debug_data(logger, "sensor payload ready", payload)
        try:
            received_count = send_to_server(payload, self.server_addr, self.server_port)
            record_send_success(self.health.server_send, received_count, self.sequence)
            self._notify_recovery("server_send", "Server send recovered", self.health.server_send.fail_count)
            logger.info("sensor data sent")
            self._log_health_snapshot("after_server_send_success")
            return True
        except OSError as error:
            record_send_failure(self.health.server_send, error)
            logger.error("socket send failed: %s", error)
            self._notify_failure(
                "server_send", SERVER_SEND_FAILURE_NOTIFY_THRESHOLD, self.health.server_send.consecutive_fail_count,
                "Server send error", [("Server", f"{self.server_addr or 'configured'}:{self.server_port or 'configured'}"), ("Error", str(error))],
            )
            self._log_health_snapshot("after_server_send_failure")
            return False
    
    # 継続的に実行する関数。
    def run_forever(self, iterations: int | None = None, interval: float | None = None) -> None:
        last_heartbeat_at = time.monotonic()
        completed = 0
        sleep_interval = DEFAULT_SEND_INTERVAL if interval is None else interval
        try:
            log_debug_data(logger, "client runtime start", {
                "mode": self.mode_name,
                "client_id": self.health.client.client_id,
                "region": self.health.client.region,
                "session_id": self.session_id,
                "server": f"{self.server_addr or 'configured'}:{self.server_port or 'configured'}",
                "interval": sleep_interval,
                "heartbeat_interval": HEARTBEAT_INTERVAL,
                "iterations": iterations,
                "notifications_enabled": self.notifications_enabled,
            })
            self._log_health_snapshot("startup")
            self._send_notification("Client started", 0x3498DB, [("Session ID", self.session_id)])
            while True:
                self.run_once()
                completed += 1
                now = time.monotonic()
                if now - last_heartbeat_at >= HEARTBEAT_INTERVAL:
                    result = send_heartbeat(self.health)
                    record_health_report(self.health.health_report, result.success, result.status_code, result.error)
                    log_debug_data(logger, "health report result", asdict(result))
                    if result.success:
                        self._notify_recovery("health_report", "Health report recovered", self.health.health_report.fail_count)
                    else:
                        self._notify_failure(
                            "health_report", HEALTH_REPORT_FAILURE_NOTIFY_THRESHOLD, self.health.health_report.consecutive_fail_count,
                            "Health report error", [("Error", result.error), ("HTTP Status", str(result.status_code))],
                        )
                    self._log_health_snapshot("after_health_report")
                    last_heartbeat_at = now
                if iterations is not None and completed >= iterations:
                    logger.debug("runtime exit by iterations: completed=%d limit=%d", completed, iterations)
                    break
                time.sleep(sleep_interval)
        except KeyboardInterrupt:
            logger.info("Ctrl+C: stop monitor")
        finally:
            self._log_health_snapshot("shutdown")
            self.sensors.close()
            self._send_notification(
                "Client stopped", 0x95A5A6,
                [("Uptime Seconds", str(self.health.runtime.uptime_seconds)), ("Send Success", str(self.health.server_send.success_count)), ("Send Failure", str(self.health.server_send.fail_count))],
            )
