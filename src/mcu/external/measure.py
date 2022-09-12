"""Module for the measurement commands"""

import logging
from mcu.models.user_defined import Command
from mcu.config import add_tcp_server


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

    def tcp_connected(self, connected: str):
        """Gets called when a new tcp connection is made"""
        logging.info("Connected to %s", connected)

    def tcp_disconnected(self):
        """Gets called when a device disconnects"""
        logging.info("Device disconnected")

    def tcp_received(self):
        """Gets called when a new TCP message comes in"""

    def target(self, *args, keyword: str):
        if keyword == self.MEASURE_PCB:
            logging.info(self.MEASURE_PCB)

        elif keyword == self.MEASURE_LABEL:
            logging.info(self.MEASURE_LABEL)

        elif keyword == self.MEASURE_ASSEMBLY:
            logging.info(self.MEASURE_ASSEMBLY)
