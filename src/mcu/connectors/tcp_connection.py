"""Module for the implementation of an asynchronous TCP Server"""
from __future__ import annotations
from ast import List
import asyncio
from asyncio import transports
import logging
from threading import Thread
from typing import Callable


class TCPServerProtocol(asyncio.Protocol):
    """Protocol class for tcp server implementation"""

    def __init__(self) -> None:
        super().__init__()
        self.__connected_callbacks: List[Callable[[str], None]] = []
        self.__connection_lost_callbacks: List[Callable[[str], None]] = []
        self.__received_callbacks: List[Callable[[str], None]] = []
        self.transport = None

    def connection_made(self, transport: transports.Transport) -> None:
        peername = transport.get_extra_info('peername')
        self.transport = transport
        _ = [callback(peername) for callback in self.__connected_callbacks]

    def connection_lost(self, exc: Exception | None) -> None:
        if exc is not None:
            print(f"Connection closed with exception: {exc}")
        else:
            print("Connection closed")
        self.transport.close()
        _ = [callback() for callback in self.__connection_lost_callbacks]

    def data_received(self, data: bytes) -> None:
        message = data.decode()
        if message in ('\r', '\n', '\r\n'):
            return

        print("sending data to callbacks", self.__received_callbacks)

        _ = [callback(message) for callback in self.__received_callbacks]

    def register_callback(self,
                          connected: Callable[[str], None] = None,
                          lost: Callable[[], None] = None,
                          received: Callable[[str], None] = None
                          ) -> None:
        """Register callback methods for the server events

        Args:
            connected (Callable[[str], None], optional): Gets called when a new device connects. Defaults to None.
            lost (Callable[[], None], optional): Gets called when a connection is lost. Defaults to None.
            received (Callable[[str], None], optional): Gets called when a new message is received. Defaults to None.
        """
        if connected is not None:
            self.__connected_callbacks.append(connected)

        if lost is not None:
            self.__connection_lost_callbacks.append(lost)

        if received is not None:
            self.__received_callbacks.append(received)

    def send(self, msg: str) -> None:
        """Sends data to the TCP Buffer

        Args:
            msg (str): The string message to be sent
        """
        # Every object that can call the send method is on the main thread
        # This means that a race condition cannot occur
        self.transport.write(msg.encode('ascii'))

class TCPServer:
    """Class to run a TCP Server Protocol in a separate thread"""

    def __new__(cls: type[TCPServer], host: str = 'localhost', port: int = 65432) -> TCPServer:
        if not hasattr(cls, 'instances'):
            cls.instances: List[TCPServer] = []

        for instance in cls.instances:
            if instance.host == host and instance.port == port:
                return instance

        logging.info("Creating new TCP server instance to %s:%d", host, port)
        new_instance = super().__new__(cls)
        new_instance.__initialized = False
        cls.instances.append(new_instance)

        return new_instance

    # pylint: disable=too-many-arguments
    def __init__(self,
                 host: str,
                 port: int,
                 ) -> None:

        # check if the instance has been initialized before
        # pylint: disable=access-member-before-definition
        if self.__initialized:
            return
        self.__initialized = True

        # initialize the object
        self.__host = host
        self.__port = port
        self.__thread = Thread(target=self._start_async, daemon=True)
        self.__protocol = TCPServerProtocol()

    def start(self):
        """Starts the TCP server in a separate thread"""
        self.__thread.start()

    def send(self, msg: str):
        """Sends data to the TCP Buffer via the protocol

        Args:
            msg (str): The string message to be sent
        """
        self.__protocol.send(msg)

    def register_callbacks(self,
                           connected: Callable[[str], None] = None,
                           lost: Callable[[], None] = None,
                           received: Callable[[str], None] = None
                           ) -> None:
        """Register callback methods for the server events

        Args:
            connected (Callable[[str], None], optional): Gets called when a new device connects. Defaults to None.
            lost (Callable[[], None], optional): Gets called when a connection is lost. Defaults to None.
            received (Callable[[str], None], optional): Gets called when a new message is received. Defaults to None.
        """
        self.__protocol.register_callback(connected=connected,
                                          lost=lost,
                                          received=received
                                          )

    def _start_async(self):
        asyncio.run(self._target())

    async def _target(self):
        loop = asyncio.get_event_loop()

        server = await loop.create_server(
            lambda: self.__protocol,
            self.__host,
            self.__port,
        )

        async with server:
            await server.serve_forever()

        loop.close()

    @property
    def host(self):
        """The host of the server"""
        return self.__host

    @property
    def port(self):
        """The port the server is listening on"""
        return self.__port