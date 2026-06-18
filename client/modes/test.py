import logging

from config import DISCORD_WEBHOOK_URL
from notification.discord import notify_discord

logger = logging.getLogger(__name__)


def run_test_mode(args):
    if args.target == "notification":
        logger.info("start notification test")
        notify_discord(DISCORD_WEBHOOK_URL, "smart-environment-monitor notification test")
        return

    raise ValueError("test mode requires --target notification")
