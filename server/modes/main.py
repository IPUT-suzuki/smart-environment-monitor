import logging

from config import SERVER_ADDR, SERVER_PORT
from services.server import start_server

logger = logging.getLogger(__name__)


def run_main_mode(args):
    server_addr = args.server_addr or SERVER_ADDR
    server_port = args.server_port or SERVER_PORT
    logger.info("start main mode")
    start_server(server_addr, server_port)
