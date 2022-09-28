import logging
from time import sleep
from mcu.models.user_defined import Command
from mcu.config import add_tcp_server
from mcu.protocols import Message


class HomeCommand(Command):
    def __init__(self) -> None:
        super().__init__(keywords="home")

        self.__tcp = add_tcp_server("0.0.0.0", 65432)
        self.__tcp.register_callbacks(received=self.tcp_received)

    def tcp_received(self, msg: bytes):
        message = Message.parse(msg)
        if message.type == Message.TYPE.OK:
            self.update_attribute(f"{self.current_keyword}_info", "OK")

        if message.type == Message.TYPE.ERROR:
            self.update_attribute(f"{self.current_keyword}_info", "ERROR")

    def target(self, *_, keyword: str):
        logging.info("Homing robot")
        self.__tcp.send("IAC|HOME\n")

        self.result = ""
