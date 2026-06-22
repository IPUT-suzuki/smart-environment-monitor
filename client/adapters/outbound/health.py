import json
import logging
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass

from config.settings import WEB_HEALTH_TIMEOUT_SECONDS, WEB_HEALTH_URL
from app.logging import log_debug_data
from domain.models import ClientHeartBeat

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class HeartbeatResult:
    success: bool
    status_code: int = 0
    error: str = ""


def sanitize_url_for_log(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    host = parsed.hostname or ""
    if parsed.port is not None:
        host = f"{host}:{parsed.port}"
    path = parsed.path or "/"
    if parsed.scheme and host:
        return f"{parsed.scheme}://{host}{path}"
    if parsed.scheme:
        return f"{parsed.scheme}:{path}"
    return path


def send_heartbeat(health: ClientHeartBeat, web_health_url: str | None = None, timeout: float | None = None) -> HeartbeatResult:
    url = web_health_url or WEB_HEALTH_URL
    request_timeout = WEB_HEALTH_TIMEOUT_SECONDS if timeout is None else timeout
    if not url:
        logger.warning("heartbeat URL is not set")
        return HeartbeatResult(False, error="heartbeat URL is not set")
    log_debug_data(logger, "heartbeat request", {
        "url": sanitize_url_for_log(url),
        "payload": asdict(health),
    })
    request = urllib.request.Request(
        url,
        data=json.dumps(asdict(health)).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=request_timeout) as response:
            status = response.getcode()
        if 200 <= status < 300:
            logger.debug("heartbeat sent: url=%s status=%s", sanitize_url_for_log(url), status)
            return HeartbeatResult(True, status)
        logger.warning("heartbeat failed: status=%s", status)
        return HeartbeatResult(False, status, f"HTTP {status}")
    except urllib.error.HTTPError as error:
        logger.warning("heartbeat failed: status=%s", error.code)
        logger.debug("heartbeat HTTP error: url=%s status=%s", sanitize_url_for_log(url), error.code)
        return HeartbeatResult(False, error.code, f"HTTP {error.code}")
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        logger.warning("heartbeat request failed: %s", error)
        logger.debug("heartbeat request error detail: url=%s error=%r", sanitize_url_for_log(url), error)
        return HeartbeatResult(False, error=str(error))
