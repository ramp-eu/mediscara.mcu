"""Module for the measurement commands"""

from enum import Enum, auto
import logging
from mcu.models.user_defined import Command
from mcu.config import add_tcp_server
from mcu.protocols import Message


class Measure(Command):
    """Custom command class for measurements"""

    MEASURE_PCB = "measure_pcb"
    MEASURE_LABEL = "measure_label"
    MEASURE_ASSEMBLY = "measure_assembly"

    def __init__(self) -> None:
        super().__init__(
            [
                Measure.MEASURE_ASSEMBLY,
                Measure.MEASURE_LABEL,
                Measure.MEASURE_PCB,
            ]
        )

        # register tcp server instance
        self.__tcp = add_tcp_server(host="0.0.0.0", port=65432)
        # add callbacks for tcp events
        self.__tcp.register_callbacks(
            connected=self.tcp_connected,
            lost=self.tcp_disconnected,
            received=self.tcp_received,
        )

        # state
        self.__measurement = ""

    def tcp_connected(self, connected: str):
        """Gets called when a new tcp connection is made"""
        logging.info("Connected to %s", connected)

    def tcp_disconnected(self):
        """Gets called when a device disconnects"""
        logging.info("Device disconnected")

    def tcp_received(self, msg: bytes):
        """Gets called when a new TCP message comes in"""

        message = Message.parse(msg)

        if message.type == Message.TYPE.KEY_VALUE:
            if "M1" in message.data_kw.keys():
                # process the measurement
                self.update_attribute(f"{self.current_keyword}_info", str(message))

    def target(self, *args, keyword: str):
        logging.info("Measuring: %s", keyword)
        if keyword == self.MEASURE_PCB:
            self.__tcp.send("IAC|MEASURE_PCB")
            self.__measurement = self.MEASURE_PCB


        elif keyword == self.MEASURE_LABEL:
            self.__tcp.send("IAC|MEASURE_LABEL")
            self.__measurement = self.MEASURE_LABEL

        elif keyword == self.MEASURE_ASSEMBLY:
            self.__tcp.send("IAC|MEASURE_ASSEMBLY")
            self.__measurement = self.MEASURE_ASSEMBLY

        self.result = '' # do not update result in OCB yet
