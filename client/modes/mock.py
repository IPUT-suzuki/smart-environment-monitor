import logging
import time

from config.settings import (
    DEFAULT_SEND_INTERVAL,
    DISCORD_WEBHOOK_URL,
    HEARTBEAT_INTERVAL,
)
from services.notification.discord import notify_discord
from sensor.dummy import get_dummy_data
from services.payload import build_payload, build_server_disconnect_error_embed
from services.sender import send_to_server
from services.heartbeart import send_heartbeat

logger = logging.getLogger(__name__)

last_heart_beat = 0

sensor_read = False
sensor_data = False
heartbeat_error = None


def run_mock_mode(args):
    logger.info("start mock mode")

    while True:
        try:
            sensor_data = get_dummy_data()
            sensor_read = True
            logger.debug(sensor_data)
            payload = build_payload(sensor_data)
            sensor_data = True
            send_to_server(payload, args.server_addr, args.server_port)

            logger.info("mock sensor data sent")
        except OSError as e:
            heartbeat_error = None
            logger.error("socket send failed: %s", e)
            embed_message = build_server_disconnect_error_embed(
                payload, args.server_addr, args.server_port
            )
            notify_discord(DISCORD_WEBHOOK_URL, embed_message)
            time.sleep(DEFAULT_SEND_INTERVAL)

        except KeyboardInterrupt:
            logger.info("Ctrl + C\nstop mock mode")
            break

        finally:
            now = time.monotonic()
            if now - last_heart_beat >= HEARTBEAT_INTERVAL:
                send_heartbeat(sensor_read, sensor_data, heartbeat_error)
                last_heart_beat = now
            time.sleep
