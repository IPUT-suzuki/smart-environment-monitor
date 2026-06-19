import logging

from config import SERVER_ADDR, SERVER_PORT

logger = logging.getLogger(__name__)


def run_test_mode(args):
    logger.info("start test mode")
    logger.info(
        "server config: %s:%s",
        args.server_addr or SERVER_ADDR,
        args.server_port or SERVER_PORT,
    )
