import logging
from pathlib import Path

from adapters.tcp_server import SensorTcpServer
from config.settings import SERVER_ADDR, SERVER_PORT
from repositories.csv_sensor_repository import CsvSensorRepository
from tests.roundtrip import run_roundtrip_test

logger = logging.getLogger(__name__)
DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "sensor_data.csv"


def run_main_mode(args) -> None:
    server = SensorTcpServer(
        args.server_addr or SERVER_ADDR,
        args.server_port or SERVER_PORT,
        CsvSensorRepository(DATA_PATH),
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Ctrl+C: stop server")
    finally:
        server.close()


def run_test_mode(args) -> None:
    if args.target != "roundtrip":
        raise ValueError("test mode requires --target roundtrip")
    if args.count < 1:
        raise ValueError("--count must be at least 1")
    run_roundtrip_test(args.count)
