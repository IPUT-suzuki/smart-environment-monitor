import json
import socket
import tempfile
import threading
import unittest
import uuid
from pathlib import Path

from server.adapters.tcp_server import SensorTcpServer
from server.repositories.csv_sensor_repository import CsvSensorRepository


def tcp_payload(client_id: str, sequence: int):
    return {
        "client_id": client_id,
        "region": "test",
        "datetime": "2026-07-29 10:00:00",
        "session_id": f"session-{client_id}",
        "sequence": sequence,
        "sensor_data": {"temperature": 25.0, "humidity": 50.0, "pressure": 1000.0, "co2": 500},
    }


def send_payload(host, port, payload, acknowledgements):
    with socket.create_connection((host, port), timeout=3) as connection:
        connection.sendall((json.dumps(payload) + "\n").encode("utf-8"))
        response = bytearray()
        while b"\n" not in response:
            response.extend(connection.recv(4096))
    acknowledgements.append(json.loads(response.split(b"\n", 1)[0].decode("utf-8")))


class SensorTcpServerTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repository = CsvSensorRepository(Path(self.temp_dir.name) / "sensor_data.csv")
        self.server = SensorTcpServer("127.0.0.1", 0, self.repository)
        self.server.start_background()

    def tearDown(self):
        self.server.close()
        self.temp_dir.cleanup()

    def test_concurrent_clients_receive_matching_acknowledgements(self):
        host, port = self.server.address
        acknowledgements = []
        payloads = [tcp_payload(f"client-{index}", 1) for index in range(5)]
        threads = [threading.Thread(target=send_payload, args=(host, port, payload, acknowledgements)) for payload in payloads]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(5)
            self.assertFalse(thread.is_alive())

        self.assertEqual(self.repository.total_rows(), 5)
        self.assertEqual(len(acknowledgements), 5)
        self.assertTrue(all(ack["ok"] and ack["sequence"] == 1 for ack in acknowledgements))
        self.assertEqual({ack["session_id"] for ack in acknowledgements}, {payload["session_id"] for payload in payloads})

    def test_invalid_connection_does_not_stop_following_valid_client(self):
        host, port = self.server.address
        with socket.create_connection((host, port), timeout=3) as connection:
            connection.sendall(b"not-json\n")
            response = json.loads(connection.recv(4096).decode("utf-8").strip())
        self.assertFalse(response["ok"])

        acknowledgements = []
        payload = tcp_payload(f"valid-{uuid.uuid4()}", 1)
        send_payload(host, port, payload, acknowledgements)
        self.assertTrue(acknowledgements[0]["ok"])
