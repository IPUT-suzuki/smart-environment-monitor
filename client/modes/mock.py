import logging
import time

from config import DEFAULT_SEND_INTERVAL,DISCORD_WEBHOOK_URL,CLIENT_REGION,CLIENT_ID
from services.notification.discord import notify_discord
from sensor.dummy import get_dummy_data
from services.payload import build_payload,build_server_disconnect_error_embed
from services.sender import send_to_server

logger = logging.getLogger(__name__)


def run_mock_mode(args):
    logger.info("start mock mode")

    while True:
        try:
            sensor_data = get_dummy_data()
            logger.debug(sensor_data)
            payload = build_payload(sensor_data)
            send_to_server(payload, args.server_addr, args.server_port)

            logger.info("mock sensor data sent")
            time.sleep(DEFAULT_SEND_INTERVAL)
        except OSError as e:
            logger.error("socket send failed: %s", e)
            embed_message = build_server_disconnect_error_embed(payload,args.server_addr, args.server_port)
            notify_discord(DISCORD_WEBHOOK_URL,embed_message)
            time.sleep(DEFAULT_SEND_INTERVAL)

        except KeyboardInterrupt:
            logger.info("Ctrl + C\nstop mock mode")
            break