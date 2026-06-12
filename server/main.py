import socket
import threading

try:
    from config import *
except ValueError as e:
    print(e)
    exit(1)

def handle_client(conn):
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(data)
    finally:
        conn.close()


server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
try:
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
    server.bind((SERVER_ADDR,SERVER_PORT))
    server.listen()
    while True:
        conn,addr = server.accept()
        print("connected:", addr)
        t = threading.Thread(
            target=handle_client,
            args=(conn,),
            daemon=True
        )
        t.start()
except socket.error:
    server.close()

