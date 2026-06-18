import logging
import time

from config import DEFAULT_SEND_INTERVAL
from sensor.dummy import get_dummy_data
from payload import build_payload
from sender import send_to_server

logger = logging.getLogger(__name__)


def run_mock_mode(args):
    logger.info("start mock mode")

    while True:
        try:
            sensor_data = get_dummy_data()
            raw_data = build_payload(sensor_data)
            send_to_server(raw_data, args.server_addr, args.server_port)

            logger.info("mock sensor data sent")

        except OSError as e:
            logger.error("socket send failed: %s", e)

        except KeyboardInterrupt:
            logger.info("Ctrl + C\nstop mock mode")
            break

        time.sleep(DEFAULT_SEND_INTERVAL)
