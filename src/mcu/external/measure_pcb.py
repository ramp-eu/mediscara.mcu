"""Module for the custom command'measure_pcb'"""
import logging
from mcu.models.user_defined import Command, Service
from mcu.config import add_tcp_server, clear_errors, report_error
from mcu.protocols import Message


class MeasurePCBCommand(Command):
    """Class to implement the custom command"""

    def __init__(self) -> None:
        super().__init__(keywords="measure_pcb")

        self.__tcp = add_tcp_server("0.0.0.0", 65432)
        self.__tcp.register_callbacks(
            received=self.tcp_received,
            connected=self.tcp_connected,
            lost=self.tcp_disconnected,
        )

        self.__tcp_connected = False
        self.__measuring = False

    def tcp_received(self, msg: bytes):
        """Gets called when TCP Server receives data"""
        message = Message.parse(msg)

        if message.type == Message.TYPE.KEY_VALUE and self.__measuring:
            logging.info("Measurement results: %s", str(message.data_kw))
            Service.update_attribute(f"{self.keywords}_info", str(message.data_kw))

    def tcp_connected(self, _: str):
        """Gets called when the TCP Server connects to a client"""
        self.__tcp_connected = True
        logging.info("Connected")

    def tcp_disconnected(self):
        """Gets called when a client disconnects from the tcp server"""
        self.__tcp_connected = False

    def serial_error(self, _: Exception):
        """Gets called when a serial error occurs"""
        report_error("Serial exception")

    def target(self, *args):

        if not self.__tcp_connected:
            self.result = "ERROR Robot not connected"
            report_error("Robot not connected")
            return

        try:
            for arg in args:
                if isinstance(arg, dict):
                    # get program name to load
                    pg_name = arg["prog"]

                    if pg_name is not None:
                        logging.info("Sending program name %s to robot..", pg_name)
                        self.__tcp.send(f"RUN|{pg_name}\n")

            # send the command itself
            self.__tcp.send("IAC|MEASURE_PCB\n")
            self.__measuring = True

        except Exception as error:  # pylint: disable=broad-except
            logging.info("Unable to execute command: %s", str(error))
            self.result = f"ERROR {error.__class__.__name__}"

        else:
            self.result = "OK"
            clear_errors()
