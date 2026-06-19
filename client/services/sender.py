import json
import socket

from config import SERVER_ADDR, SERVER_PORT
from utils.data_class import ServerSendData


def send_to_server(data: ServerSendData, server_addr=None, server_port=None):
    server_addr = server_addr or SERVER_ADDR
    server_port = server_port or SERVER_PORT

    payload = json.dumps(data).encode("utf-8")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((server_addr, server_port))
        sock.sendall(payload)
