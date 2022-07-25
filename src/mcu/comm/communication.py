"""Module for the communication with API"""

import logging
import socket
from typing import Callable
from threading import Thread

class API:

    def __init__(self, received_callback: Callable[[str], None]) -> None:
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = True

    def connect(self, host: str, port: int, connected_callback: Callable[[bool], None], received_callback: Callable[[str], None]):
        self.connect.connected_callback = connected_callback
        self.connect.received_callback = received_callback
        Thread(target=self.__connect_internal, args={"host": host, "port": port, "connected_callback": connected_callback}, daemon=True).start()

    def __connected_callback_internal(self):
        if not hasattr(self.connect, "connected_callback"):
            raise AttributeError(f"Whoops, somebody forgot to add this attribute in the {self.connect.__name__} method")

        Thread(target=self.__main_loop, daemon=True)

    def __connect_internal(self, host: str, port: int, connected_callback: Callable[[bool], None]):
        try:
            self.__sock.connect((host, port))

        except TimeoutError:
            return False

        except InterruptedError:
            return False

    def __main_loop(self):
        while self.running:
            try:
                data = self.__sock.recv(1024)
            except Exception as e:
                logging.info("Got exception ", str(e))