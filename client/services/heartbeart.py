import datetime
import json
import logging
import urllib.error
import urllib.request

from config.settings import CLIENT_ID, CLIENT_REGION, WEB_HEALTH_INTERVAL

logger = logging.getLogger(__name__)


def send_heartbeat(
    sensor_read_ok,
    sensor_data_ok,
    error=None,
    web_health_url=None,
    uptime_seconds=None,
    failure_count=0,
    timeout=5,
):
    url = web_health_url or WEB_HEALTH_INTERVAL
    if not url:
        logger.warning("heartbeat url is not set")
        return False

    jst = datetime.timezone(datetime.timedelta(hours=9))
    payload = {
        "client_id": CLIENT_ID,
        "region": CLIENT_REGION,
        "datetime": datetime.datetime.now(jst).strftime("%Y-%m-%d %A %H:%M:%S"),
        "alive": True,
        "sensor_read_ok": bool(sensor_read_ok),
        "sensor_data_ok": bool(sensor_data_ok),
        "error": str(error) if error else None,
        "uptime_seconds": uptime_seconds,
        "failure_count": int(failure_count),
    }

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status_code = response.getcode()
            if 200 <= status_code < 300:
                logger.debug("heartbeat sent: status=%s", status_code)
                return True

            logger.warning("heartbeat failed: status=%s", status_code)
            return False

    except urllib.error.HTTPError as e:
        logger.warning("heartbeat failed: status=%s", e.code)
        return False
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        logger.warning("heartbeat request failed: %s", e)
        return False
