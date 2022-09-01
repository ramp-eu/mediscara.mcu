"""Module for the custom command 'measure_label'"""
from mcu.models.user_defined import Command
from mcu.config import add_tcp_server, clear_errors, report_error


class MeasureLabelCommand(Command):
    """Class for the custom command"""

    def __init__(self):
        super().__init__(keyword="measure_label")
        self.__server = add_tcp_server(host="0.0.0.0", port=65432)
        self.__server.register_callbacks(
            connected=self.__tcp_connected,
            lost=self.__tcp_disconnected,
            received=self.__tcp_received,
        )

        self.__server_connected = False

    def __tcp_connected(self, _: str):
        self.__server_connected = True

    def __tcp_disconnected(self):
        self.__server_connected = False

    def __tcp_received(self, msg: bytes):
        pass

    def target(self, *args):

        if not self.__server_connected:
            self.result = "ERROR Robot not connected"
            report_error("Robot not connected")
            return

        try:
            for arg in args:
                if isinstance(arg, dict):
                    pg_name = arg["prog"]

                    if pg_name is not None:
                        self.__server.send(f"RUN|{pg_name}|\n")

            # send the measure command
            self.__server.send("IAC|MEASURE_LABEL|\n")

        except Exception as error:  # pylint: disable=broad-except
            self.result = f"ERROR {error.__class__.__name__}"

        else:
            self.result = "OK"
            clear_errors()
