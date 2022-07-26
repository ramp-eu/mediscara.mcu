"""Module for the custom command 'measure_label'"""
import logging
from time import sleep
from mcu.models.command import Command
from mcu.config import add_tcp_server

class CustomCommand(Command):
    """Class for the custom command"""
    def __init__(self):
        super().__init__(keyword="measure_label")
        self.__server = add_tcp_server(host='localhost', port=65432)
        self.__server.register_callbacks(received=self.tcp_received)

    def tcp_received(self, msg: str):
        print("measure_label got:", msg)

    def target(self):
        logging.info("Measuring label")
        sleep(5)
        self._command_result = "OK"
