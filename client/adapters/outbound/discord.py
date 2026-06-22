import json
import logging
import urllib.error
import urllib.request

from app.logging import log_debug_data
from config.settings import DISCORD_TIMEOUT_SECONDS

logger = logging.getLogger(__name__)


def notify_discord(webhook_url: str | None, message: str | dict, timeout: float | None = None) -> bool:
    if not webhook_url:
        logger.warning("Discord notification skipped: DISCORD_WEBHOOK_URL is not set")
        return False
    if not webhook_url.startswith(("https://discord.com/api/webhooks/", "https://discordapp.com/api/webhooks/")):
        logger.warning("Discord notification skipped: invalid webhook URL")
        return False
    request_body = message if isinstance(message, dict) else {"content": message}
    request_timeout = DISCORD_TIMEOUT_SECONDS if timeout is None else timeout
    payload = json.dumps(request_body).encode("utf-8")
    log_debug_data(logger, "Discord request payload", request_body)
    request = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "smart-environment-monitor/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=request_timeout):
            pass
        logger.info("Discord notification sent")
        logger.debug("Discord request accepted")
        return True
    except urllib.error.HTTPError as error:
        logger.error("Discord notification failed: HTTP %s", error.code)
        response_body = error.read().decode("utf-8", errors="replace")[:2048]
        if response_body:
            logger.debug("Discord error response: %s", response_body)
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        logger.error("Discord notification failed: %s", error)
    return False
