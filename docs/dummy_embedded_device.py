"""This is an example module for a simulated communication with an embedded device"""
import socket
import time

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 2000  # The port used by the server

try:

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        connected = False
        while not connected:
            try:
                s.connect((HOST, PORT))
                connected = True

            except ConnectionError:
                time.sleep(1)

        print("Connected")
        # start listening for incoming commands

        laser_start_time = None

        while True:
            try:
                msg = s.recv(1024)
            except ConnectionError:
                print("Connection closed")
                break

            if msg == b'HOME\n':
                print("Started homing")
                # emulate the delay of homing
                time.sleep(2)

                # send back the result of the homing
                s.sendall(b'OK\n')

            elif msg == b'START_LASER_CUT\n':
                print("Started laser cutting")
                s.sendall(b"STARTED\n")
                laser_start_time = time.time()

            elif msg == b'STOP_LASER_CUT\n':
                print("Stopping laser cutting")

                if laser_start_time is not None:
                    s.sendall(
                        b'DURATION|' + str(time.time() -
                                           laser_start_time).encode('ascii')
                    )
                    laser_start_time = None

                else:
                    s.sendall(b'ERROR|Laser has not been turned on.\n')

except KeyboardInterrupt:
    pass
