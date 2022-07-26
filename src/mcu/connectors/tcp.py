"""Module for the implementation of an asynchronous TCP Server"""
import asyncio
from asyncio import transports
from threading import Thread
from typing import Callable


class TCPServerProtocol(asyncio.Protocol):
    """Protocol class for tcp server implementation"""

    def __init__(self,
                 connection_made_callback: Callable[[str], None],
                 connection_lost_callback: Callable[[], None],
                 data_received_callback: Callable[[str], None]
                 ) -> None:
        super().__init__()
        self.__connected_callback = connection_made_callback
        self.__connection_lost_callback = connection_lost_callback
        self.__received_callback = data_received_callback
        self.transport = None

    def connection_made(self, transport: transports.Transport) -> None:
        peername = transport.get_extra_info('peername')
        self.transport = transport
        self.__connected_callback(peername)

    def connection_lost(self, exc: Exception | None) -> None:
        if exc is not None:
            print(f"Connection closed with exception: {exc}")
        else:
            print("Connection closed")
        self.transport.close()
        self.__connection_lost_callback()

    def data_received(self, data: bytes) -> None:
        message = data.decode()
        if message in ('\r', '\n', '\r\n'):
            return

        self.__received_callback(message)


class TCPServer:
    """Class to run a TCP Server Protocol in a separate thread"""

    def __init__(self,
                 connection_made_callback: Callable[[str], None],
                 connection_lost_callback: Callable[[], None],
                 data_received_callback: Callable[[str], None],
                 host: str = 'localhost',
                 port: int = 65432,
                 ) -> None:
        self.__connected_callback = connection_made_callback
        self.__connection_lost_callback = connection_lost_callback
        self.__received_callback = data_received_callback
        self.__host = host
        self.__port = port
        self.__thread = Thread(target=self._start_async, daemon=True)

    def start(self):
        """Starts the TCP server in a separate thread"""
        self.__thread.start()

    def _start_async(self):
        asyncio.run(self._target())

    async def _target(self):
        loop = asyncio.get_event_loop()

        server = await loop.create_server(
            lambda: TCPServerProtocol(connection_made_callback=self.__connected_callback,
                                      connection_lost_callback=self.__connection_lost_callback,
                                      data_received_callback=self.__received_callback,
                                      ),
            self.__host,
            self.__port,
        )

        async with server:
            await server.serve_forever()

        loop.close()
