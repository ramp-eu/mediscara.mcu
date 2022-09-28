"""Custom command module for the pause command"""

from mcu.models.user_defined import Command
from mcu.config import add_tcp_server


class Pause(Command):
    """Custom command class for the pause command"""

    def __init__(self) -> None:
        super().__init__(keywords="pause")
        self.__tcp = add_tcp_server(host="0.0.0.0", port=65432)

        self.__tcp.register_callbacks(received=self.tcp_received)

        self.__paused = False

    def tcp_received(self, msg: bytes):
        """Gets called when a new tcpip message is received"""

    def target(self, *_, keyword: str):
        self.__tcp.send("IAC|PAUSE\n")  # send the pause signal

        self.__paused = not self.__paused

        self.result = "PAUSED" if self.__paused else "RESUMED"
