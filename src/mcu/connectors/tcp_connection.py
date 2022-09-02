"""Module for the implementation of an asynchronous TCP Server"""
from __future__ import annotations
from ast import List
import asyncio
from asyncio import Future, transports
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
        peername = transport.get_extra_info("peername")
        self.transport = transport
        _ = [callback(peername) for callback in self.__connected_callbacks]

    def connection_lost(self, exc: Exception | None) -> None:
        if exc is not None:
            print(f"Connection closed with exception: {exc}")

        self.transport.close()
        _ = [callback() for callback in self.__connection_lost_callbacks]

    def data_received(self, data: bytes) -> None:
        # filter out empty messages
        if data in (b"\r", b"\n", b"\r\n"):
            return

        messages = data.split(b"\n")  # split if there are multiple messages
        for message in messages:
            _ = [callback(message) for callback in self.__received_callbacks]

    def register_callback(
        self,
        connected: Callable[[str], None] = None,
        lost: Callable[[], None] = None,
        received: Callable[[bytes], None] = None,
    ) -> None:
        """Register callback methods for the server events

        Args:
            connected (Callable[[str], None], optional): Gets called when a new device connects. Defaults to None.
            lost (Callable[[], None], optional): Gets called when a connection is lost. Defaults to None.
            received (Callable[[bytes], None], optional): Gets called when a new message is received. Defaults to None.
        """
        if connected is not None:
            self.__connected_callbacks.append(connected)

        if lost is not None:
            self.__connection_lost_callbacks.append(lost)

        if received is not None:
            self.__received_callbacks.append(received)

    def send(self, msg: str | bytes) -> None:
        """Sends data to the TCP Buffer

        Args:
            msg (str): The string message to be sent
        """
        # Every object that can call the send method is on the main thread
        # This means that a race condition cannot occur
        if isinstance(msg, str):
            msg = msg.encode("ascii")

        if self.transport is not None:
            self.transport.write(msg)


class TCPServer:
    """Class to run a TCP Server Protocol in a separate thread"""

    def __new__(
        cls: type[TCPServer], host: str = "localhost", port: int = 65432
    ) -> TCPServer:
        if not hasattr(cls, "instances"):
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
    def __init__(
        self,
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

    def send(self, msg: str | bytes):
        """Sends data to the TCP Buffer via the protocol

        Args:
            msg (str): The string message to be sent
        """
        self.__protocol.send(msg)

    def register_callbacks(
        self,
        connected: Callable[[str], None] = None,
        lost: Callable[[], None] = None,
        received: Callable[[bytes], None] = None,
    ) -> None:
        """Register callback methods for the server events

        Args:
            connected (Callable[[str], None], optional): Gets called when a new device connects. Defaults to None.
            lost (Callable[[], None], optional): Gets called when a connection is lost. Defaults to None.
            received (Callable[[bytes], None], optional): Gets called when a new message is received. Defaults to None.
        """
        self.__protocol.register_callback(
            connected=connected, lost=lost, received=received
        )

    def _start_async(self):
        asyncio.run(self._target())

    async def _target(self):
        loop = asyncio.get_event_loop()

        try:
            server = await loop.create_server(
                lambda: self.__protocol,
                self.__host,
                self.__port,
            )

            async with server:
                await server.serve_forever()

        except (ConnectionRefusedError, OSError) as err:
            logging.warning("TCP Error: %s", str(err))

        finally:
            if not loop.is_running:
                loop.close()

    @property
    def host(self):
        """The host of the server"""
        return self.__host

    @property
    def port(self):
        """The port the server is listening on"""
        return self.__port


class TCPClientProtocol(asyncio.Protocol):
    """Protocol class for tcp server implementation"""

    def __init__(self) -> None:
        super().__init__()
        self.connected_callbacks: List[Callable[[str], None]] = []
        self.lost_callbacks: List[Callable[[], None]] = []
        self.received_callbacks: List[Callable[[str | bytes], None]] = []
        self.transport = None
        self.__on_conn_lost = None

    def connection_made(self, transport: transports.Transport) -> None:
        self.transport = transport
        peername = transport.get_extra_info("peername")
        # call the callbacks
        _ = [callback(peername) for callback in self.connected_callbacks]

    def connection_lost(self, exc: Exception | None) -> None:
        if exc is not None:
            logging.warning("Connection lost: %s", str(exc))

        _ = [callback() for callback in self.lost_callbacks]
        if self.__on_conn_lost is not None:
            self.__on_conn_lost.set_result(True)

    def data_received(self, data: bytes) -> None:
        if data in (b"\r", b"\n", b"\r\n"):
            return

        messages = data.split(b"\n")  # split if there are multiple messages
        for message in messages:
            _ = [callback(message) for callback in self.received_callbacks]

    @property
    def on_connection_lost(self):
        return self.__on_conn_lost

    @on_connection_lost.setter
    def on_connection_lost(self, value: Future):
        self.__on_conn_lost = value


class TCPCLient:
    """Class to run a TCP Client in a separate protocol"""

    def __new__(
        cls: type[TCPCLient], host: str = "localhost", port: int = 65432
    ) -> TCPServer:
        if not hasattr(cls, "instances"):
            cls.instances: List[TCPCLient] = []

        for instance in cls.instances:
            if instance.host == host and instance.port == port:
                return instance

        logging.info("Creating new TCP client instance to %s:%d", host, port)
        new_instance = super().__new__(cls)
        new_instance.__initialized = False
        cls.instances.append(new_instance)

        return new_instance

    # pylint: disable=too-many-arguments
    def __init__(
        self,
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
        self.__protocol = TCPClientProtocol()

    def start(self):
        """Starts the TCP Client"""
        self.__thread.start()

    def send(self, msg: str | bytes):
        """Sends data via the client"""
        if isinstance(msg, str):
            msg = msg.encode("ascii")

        self.__protocol.transport.write(msg)

    def register_callbacks(
        self,
        connected: Callable[[str], None] = None,
        lost: Callable[[], None] = None,
        received: Callable[[bytes], None] = None,
    ) -> None:
        """Register callback methods for the server events

        Args:
            connected (Callable[[str], None], optional): Gets called when a new device connects. Defaults to None.
            lost (Callable[[], None], optional): Gets called when a connection is lost. Defaults to None.
            received (Callable[[bytes], None], optional): Gets called when a new message is received. Defaults to None.
        """
        if connected is not None:
            self.__protocol.connected_callbacks.append(connected)

        if lost is not None:
            self.__protocol.lost_callbacks.append(lost)

        if received is not None:
            self.__protocol.received_callbacks.append(received)

    def _start_async(self):
        asyncio.run(self._target())

    async def _target(self):
        loop = asyncio.get_event_loop()

        on_connection_lost = loop.create_future()
        self.__protocol.on_connection_lost = on_connection_lost

        try:
            transport, _ = await loop.create_connection(
                lambda: self.__protocol,
                host=self.__host,
                port=self.__port,
            )

        except ConnectionRefusedError as err:
            logging.warning("TCP Client error: %s", str(err))

        try:
            await on_connection_lost

        finally:
            transport.close()
