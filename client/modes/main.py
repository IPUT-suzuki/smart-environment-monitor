import logging
import time

from config import DEFAULT_SEND_INTERVAL, DISCORD_WEBHOOK_URL
from sensor.dummy import get_dummy_data
from notification.discord import notify_discord
from payload import build_payload
from sender import send_to_server

logger = logging.getLogger(__name__)


def run_main_mode(args):
    logger.info("start mock mode")

    while True:
        try:
            sensor_data = get_dummy_data()
            raw_data = build_payload(sensor_data)
            send_to_server(raw_data, args.server_addr, args.server_port)

            logger.info("mock sensor data sent")
            time.sleep(DEFAULT_SEND_INTERVAL)

        except OSError as e:
            logger.error("socket send failed: %s", e)
            message = "サーバーへのデータ送信に失敗しました。\n" f"エラー内容: {e}"
            notify_discord(DISCORD_WEBHOOK_URL, message)
            time.sleep(DEFAULT_SEND_INTERVAL)
        except KeyboardInterrupt:
            logger.info("Ctrl + C\nstop mock mode")
            break
