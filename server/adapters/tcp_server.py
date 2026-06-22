import json
import logging
import socket
import threading

from app.logging import log_debug_data
from domain.protocol import validate_payload
from repositories.csv_sensor_repository import CsvSensorRepository

logger = logging.getLogger(__name__)


class SensorTcpServer:
    def __init__(self, host: str, port: int, repository: CsvSensorRepository):
        self.host = host
        self.port = port
        self.repository = repository
        self._socket: socket.socket | None = None
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    @property
    def address(self) -> tuple[str, int]:
        if self._socket is None:
            raise RuntimeError("server is not started")
        host, port = self._socket.getsockname()[:2]
        return host, port

    def start(self) -> None:
        if self._socket is not None:
            return
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((self.host, self.port))
        listener.listen()
        listener.settimeout(0.5)
        self._socket = listener
        logger.info("server listening on %s:%s", *self.address)

    def serve_forever(self) -> None:
        self.start()
        try:
            while not self._stop.is_set():
                try:
                    connection, address = self._socket.accept()  # type: ignore[union-attr]
                except socket.timeout:
                    continue
                except OSError:
                    if self._stop.is_set():
                        break
                    raise
                threading.Thread(target=self._handle_connection, args=(connection, address), daemon=True).start()
        finally:
            self.close()

    def start_background(self) -> None:
        self.start()
        self._thread = threading.Thread(target=self.serve_forever, daemon=True)
        self._thread.start()

    def _handle_connection(self, connection: socket.socket, address: tuple[str, int]) -> None:
        log_debug_data(logger, "tcp connection accepted", {
            "source": {"host": address[0], "port": address[1]},
        })
        buffer = bytearray()
        with connection:
            connection.settimeout(10)
            try:
                while True:
                    chunk = connection.recv(4096)
                    if not chunk:
                        return
                    buffer.extend(chunk)
                    if len(buffer) > 1_048_576:
                        self._send_ack(connection, {"ok": False, "error": "request too large"})
                        return
                    while b"\n" in buffer:
                        raw_line, _, remainder = buffer.partition(b"\n")
                        buffer = bytearray(remainder)
                        self._process_line(connection, address, raw_line)
            except (OSError, socket.timeout) as error:
                logger.warning("connection %s failed: %s", address, error)

    def _process_line(self, connection: socket.socket, address: tuple[str, int], raw_line: bytes) -> None:
        try:
            payload = json.loads(raw_line.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            log_debug_data(logger, "invalid TCP payload", {
                "source": {"host": address[0], "port": address[1]},
                "error": "invalid JSON",
            })
            self._send_ack(connection, {"ok": False, "error": "invalid JSON"})
            return
        error = validate_payload(payload)
        if error:
            log_debug_data(logger, "rejected TCP payload", {
                "source": {"host": address[0], "port": address[1]},
                "error": error,
                "payload": payload,
            })
            self._send_ack(connection, {"ok": False, "error": error})
            return
        logger.info("sensor data received from %s:%d", *address)
        log_debug_data(logger, "sensor payload received", {
            "source": {"host": address[0], "port": address[1]},
            "payload": payload,
        })
        try:
            result = self.repository.save(payload)
        except OSError as error:
            logger.exception("failed to save payload")
            self._send_ack(connection, {"ok": False, "error": f"storage failure: {error}"})
            return
        if result.duplicate:
            logger.info(
                "duplicate payload acknowledged: client_id=%s sequence=%d received_count=%d",
                payload["client_id"], payload["sequence"], result.received_count,
            )
        else:
            logger.info(
                "sensor data saved: client_id=%s sequence=%d received_count=%d sensor_data=%s",
                payload["client_id"], payload["sequence"], result.received_count, payload["sensor_data"],
            )
        acknowledgement = {
            "ok": True,
            "session_id": payload["session_id"],
            "sequence": payload["sequence"],
            "received_count": result.received_count,
            "duplicate": result.duplicate,
        }
        log_debug_data(logger, "sensor payload save result", {
            "client_id": payload["client_id"],
            "session_id": payload["session_id"],
            "sequence": payload["sequence"],
            "saved": not result.duplicate,
            "received_count": result.received_count,
        })
        self._send_ack(connection, acknowledgement)

    @staticmethod
    def _send_ack(connection: socket.socket, acknowledgement: dict) -> None:
        log_debug_data(logger, "tcp acknowledgement sent", acknowledgement)
        connection.sendall((json.dumps(acknowledgement, separators=(",", ":")) + "\n").encode("utf-8"))

    def close(self) -> None:
        self._stop.set()
        if self._socket is not None:
            self._socket.close()
            self._socket = None
        if self._thread is not None and self._thread is not threading.current_thread():
            self._thread.join(timeout=2)
