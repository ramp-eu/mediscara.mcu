"""Module for the custom command'measure_pcb'"""
import logging
from mcu.models.command import Command
from mcu.config import add_tcp_server, add_serial_server, clear_errors, report_error
from mcu.protocols import Message

class CustomCommand(Command):
    """Class to implement the custom command"""
    def __init__(self) -> None:
        super().__init__(keyword='measure_pcb')
        self.__serial = add_serial_server('COM8')
        self.__serial.register_callback(
            error=self.serial_error,
            )

        self.__tcp = add_tcp_server('localhost', 65432)
        self.__tcp.register_callbacks(received=self.tcp_received,
                                      connected=self.tcp_connected,
                                      lost=self.tcp_disconnected,
                                      )

        self.__tcp_connected = False


    def tcp_received(self, msg: bytes):
        """Gets called when TCP Server receives data"""
        message = Message.parse(msg)

        if message.type == Message.TYPE.IAC:
            self.__serial.send(message.data)

    def tcp_connected(self, _: str):
        """Gets called when the TCP Server connects to a client"""
        self.__tcp_connected = True

    def tcp_disconnected(self):
        """Gets called when a client disconnects from the tcp server"""
        self.__tcp_connected = False

    def serial_error(self, _: Exception):
        """Gets called when a serial error occurs"""
        report_error("Serial exception")

    def target(self, *args):

        if not self.__tcp_connected:
            self._command_result = "ERROR Robot not connected"
            report_error("Robot not connected")
            return

        try:
            for arg in args:
                if isinstance(arg, dict):
                    # get program name to load
                    pg_name = arg['prog']

                    if pg_name is not None:
                        logging.info("Sending program name %s to robot..", pg_name)
                        self.__tcp.send(f'RUN|{pg_name}|\n')

            # send the command itself
            self.__tcp.send("IAC|MEASURE_PCB|\n")

        except Exception as error: # pylint: disable=broad-except
            logging.info("Unable to execute command: %s", str(error))
            self._command_result = f"ERROR {error.__class__.__name__}"

        else:
            self._command_result = 'OK'
            clear_errors()
