from datetime import datetime, timedelta, timezone

from domain.models import HealthReportHealth, SensorHealth, ServerSendHealth

JST = timezone(timedelta(hours=9))


def now_string() -> str:
    return datetime.now(JST).isoformat(timespec="seconds")


def update_sensor_health(health: SensorHealth, read_ok: bool, error: str = "") -> None:
    health.connect = read_ok
    health.read = read_ok
    if read_ok:
        health.read_count += 1
        health.consecutive_fail_count = 0
        health.last_success_at = now_string()
        health.error = ""
        return

    health.fail_count += 1
    health.consecutive_fail_count += 1
    health.last_failed_at = now_string()
    health.error = error


def record_send_success(health: ServerSendHealth, received_count: int, sequence: int) -> None:
    health.success = True
    health.success_count += 1
    health.received_count = received_count
    health.last_ack_sequence = sequence
    health.consecutive_fail_count = 0
    health.last_success_at = now_string()
    health.error = ""


def record_send_failure(health: ServerSendHealth, error: Exception) -> None:
    health.success = False
    health.fail_count += 1
    health.consecutive_fail_count += 1
    health.last_failed_at = now_string()
    health.error = str(error)


def record_health_report(health: HealthReportHealth, success: bool, status_code: int = 0, error: str = "") -> None:
    health.success = success
    health.last_status_code = status_code
    if success:
        health.success_count += 1
        health.consecutive_fail_count = 0
        health.last_success_at = now_string()
        health.error = ""
        return
    health.fail_count += 1
    health.consecutive_fail_count += 1
    health.last_failed_at = now_string()
    health.error = error
