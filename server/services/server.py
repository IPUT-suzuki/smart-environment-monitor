import logging
import socket
import threading

logger = logging.getLogger(__name__)


def handle_client(conn):
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            logger.info("received data: %s", data)
    finally:
        conn.close()


def start_server(server_addr, server_port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((server_addr, server_port))
        server.listen()
        logger.info("server listening on %s:%s", server_addr, server_port)
        while True:
            conn, addr = server.accept()
            logger.info("connected: %s", addr)
            t = threading.Thread(
                target=handle_client,
                args=(conn,),
                daemon=True,
            )
            t.start()
    except socket.error as e:
        logger.error("socket error: %s", e)
        server.close()
