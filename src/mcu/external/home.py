import logging
from time import sleep
from mcu.models.user_defined import Command
from mcu.config import add_tcp_server


class HomeCommand(Command):
    def __init__(self) -> None:
        super().__init__(keywords="home")

        self.__tcp = add_tcp_server("0.0.0.0", 65432)

    def target(self, *_, keyword: str):
        logging.info("Homing robot")
        self.__tcp.send("IAC|HOME\n")

        sleep(3)

        self.result = "OK"
