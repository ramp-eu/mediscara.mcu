"""Module for the serial communication used with the IoT Devices"""
from __future__ import annotations
import logging
from threading import Thread
from time import sleep
from typing import Callable, List
from serial import Serial, serial_for_url, SerialException

class SerialServer:
    """Class to implement communication over a serial connection"""

    def __new__(cls: type[SerialServer], port: str, *args, **kwargs) -> SerialServer:
        if not hasattr(cls, 'instances'):
            cls.instances: List[SerialServer] = []

        for instance in cls.instances:
            if instance.port == port:
                # trying to open a serial connection on an existing port
                return instance

        logging.info("Creating new Serial server instance to %s", port)
        new_instance = super().__new__(cls)
        new_instance.__initialized = False
        cls.instances.append(new_instance)

        return new_instance


    def __init__(self, port: str = None, baudrate: int = 9600, refresh_rate: int = 1) -> None:
        # check if the instance has been initialized before
        # pylint: disable=access-member-before-definition
        if self.__initialized:
            return
        self.__initialized = True

        self.__running = False
        self.__refresh_rate = refresh_rate
        self.__received_callbacks: List[Callable[[str], None]] = []
        self.__error_callbacks: List[Callable[[Exception], None]] = []
        self.__thread = Thread(target=self._target, daemon=True)

        if port is None:
            logging.warning("Connecting to the serial loopback interface")
            self.__serial = serial_for_url('loop://')

        else:
            self.__serial = Serial(baudrate=baudrate)
            self.__serial.port = port


    def start(self):
        """Starts listening on the given port"""
        self.__running = True

        try:
            self.__serial.open()
            self.__thread.start()

        except SerialException as err:
            _ = [callback(err) for callback in self.__error_callbacks]

    def stop(self):
        """Stops listening to the port"""
        self.__running = False

    def send(self, msg: str) -> bool:
        """Sends the data

        Args:
            msg (str): The message to be sent

        Returns:
            (bool): True if the operation was successful, False if an error occurred
        """
        try:
            self.__serial.write(msg.encode('ascii'))
            return True

        except SerialException:
            return False

    def register_callback(self,
                          received: Callable[[str], None] = None,
                          error: Callable[[Exception], None] = None) -> None:
        """Register callback methods for error handling and receiving messages"""
        if received is not None:
            self.__received_callbacks.append(received)

        if error is not None:
            self.__error_callbacks.append(error)

    def _target(self):
        while self.__running:
            try:
                if self.__serial.in_waiting:
                    data = self.__serial.read_all().decode()
                    _ = [callback(data) for callback in self.__received_callbacks]

                sleep(self.__refresh_rate)

            except SerialException as e:
                _ = [callback(e) for callback in self.__error_callbacks]

    @property
    def port(self):
        """Returns the port associated with this server instance"""
        return self.__serial

    @property
    def running(self):
        """Return wether the server is listening or not"""
        return self.__thread.is_alive()
