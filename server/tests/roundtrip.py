import csv
import logging
import json
import socket
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

from adapters.tcp_server import SensorTcpServer
from repositories.csv_sensor_repository import CSV_FIELDS, CsvSensorRepository

logger = logging.getLogger(__name__)
ROOT_DIR = Path(__file__).resolve().parents[2]


def _read_ack(connection: socket.socket) -> dict:
    response = bytearray()
    while b"\n" not in response:
        response.extend(connection.recv(4096))
    return json.loads(response.split(b"\n", 1)[0].decode("utf-8"))


def _verify_framing_and_deduplication(host: str, port: int, repository: CsvSensorRepository) -> None:
    payload = {
        "client_id": "integration-test",
        "region": "test",
        "datetime": "2026-06-22 Monday 00:00:00",
        "session_id": str(uuid.uuid4()),
        "sequence": 1,
        "sensor_data": {"temperature": 1.0, "humidity": 2.0, "pressure": 3.0, "co2": 4},
    }
    line = (json.dumps(payload) + "\n").encode("utf-8")
    with socket.create_connection((host, port), timeout=5) as connection:
        connection.sendall(line[:7])
        connection.sendall(line[7:])
        acknowledgement = _read_ack(connection)
    if not acknowledgement.get("ok") or acknowledgement.get("sequence") != 1:
        raise RuntimeError("fragmented payload acknowledgement failed")
    rows_after_first_send = repository.total_rows()
    with socket.create_connection((host, port), timeout=5) as connection:
        connection.sendall(line)
        acknowledgement = _read_ack(connection)
    if not acknowledgement.get("ok") or not acknowledgement.get("duplicate"):
        raise RuntimeError("duplicate payload was not acknowledged as duplicate")
    if repository.total_rows() != rows_after_first_send:
        raise RuntimeError("duplicate payload created an additional CSV row")


def run_roundtrip_test(count: int) -> None:
    """Run client mock against an isolated TCP server and verify CSV row count."""
    with tempfile.TemporaryDirectory() as directory:
        repository = CsvSensorRepository(Path(directory) / "sensor_data.csv")
        with repository.path.open("r", newline="", encoding="utf-8") as file:
            if next(csv.reader(file), []) != CSV_FIELDS:
                raise RuntimeError("repository did not create an empty CSV with the expected header")
        server = SensorTcpServer("127.0.0.1", 0, repository)
        server.start_background()
        host, port = server.address
        try:
            command = [
                sys.executable, str(ROOT_DIR / "client" / "main.py"),
                "--mode", "mock", "--iterations", str(count), "--interval", "0",
                "--no-notify",
                "--server-addr", host, "--server-port", str(port),
            ]
            result = subprocess.run(command, cwd=ROOT_DIR, capture_output=True, text=True, timeout=max(20, count * 3))
            if result.returncode != 0:
                raise RuntimeError(f"client mock failed:\n{result.stderr or result.stdout}")
            if repository.total_rows() != count:
                raise RuntimeError(f"received {repository.total_rows()} rows, expected {count}")
            _verify_framing_and_deduplication(host, port, repository)
            logger.info("roundtrip passed: client sent and server saved %d payloads", count)
        finally:
            server.close()
