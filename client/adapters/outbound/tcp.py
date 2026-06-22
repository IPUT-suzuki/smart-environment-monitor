import json
import logging
import socket

from config.settings import SERVER_ADDR, SERVER_PORT, TCP_TIMEOUT_SECONDS
from app.logging import log_debug_data
from domain.models import ServerSendData

logger = logging.getLogger(__name__)


class ServerAcknowledgementError(OSError):
    pass


def send_to_server(
    data: ServerSendData,
    server_addr: str | None = None,
    server_port: int | None = None,
    timeout: float | None = None,
) -> int:
    """Send one JSON Lines payload and return the server's saved-row count."""
    address = server_addr or SERVER_ADDR
    port = server_port or SERVER_PORT
    request_timeout = TCP_TIMEOUT_SECONDS if timeout is None else timeout
    payload = (json.dumps(data, separators=(",", ":")) + "\n").encode("utf-8")
    log_debug_data(logger, "tcp send request", {
        "destination": f"{address}:{port}",
        "bytes": len(payload),
        "payload": data,
    })
    with socket.create_connection((address, port), timeout=request_timeout) as sock:
        sock.settimeout(request_timeout)
        sock.sendall(payload)
        response = bytearray()
        while b"\n" not in response:
            chunk = sock.recv(4096)
            if not chunk:
                raise ServerAcknowledgementError("server closed connection before acknowledgement")
            response.extend(chunk)
            if len(response) > 65536:
                raise ServerAcknowledgementError("server acknowledgement is too large")
    try:
        acknowledgement = json.loads(response.split(b"\n", 1)[0].decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ServerAcknowledgementError("server acknowledgement is not valid JSON") from error
    log_debug_data(logger, "tcp acknowledgement received", {
        "destination": f"{address}:{port}",
        "acknowledgement": acknowledgement,
    })
    if not acknowledgement.get("ok"):
        raise ServerAcknowledgementError(acknowledgement.get("error", "server rejected payload"))
    if acknowledgement.get("session_id") != data["session_id"] or acknowledgement.get("sequence") != data["sequence"]:
        raise ServerAcknowledgementError("server acknowledgement does not match sent payload")
    received_count = acknowledgement.get("received_count")
    if not isinstance(received_count, int) or isinstance(received_count, bool) or received_count < 0:
        raise ServerAcknowledgementError("server acknowledgement has invalid received_count")
    return received_count
