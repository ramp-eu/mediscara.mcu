"""This is an example module for a simulated communication with an embedded device"""
import socket
import time

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 2000  # The port used by the server

try:

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print("Connected")
        while True:
            msg = s.recv(1024)
            if msg == b'HOME\n':
                # emulate the delay of homing
                time.sleep(2)
                s.sendall(b'OK')

except KeyboardInterrupt:
    pass
