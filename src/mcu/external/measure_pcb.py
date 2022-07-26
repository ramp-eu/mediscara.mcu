"""Module for the custom command'measure_pcb'"""
from time import sleep
from mcu.models.command import Command
from mcu.config import add_tcp_server, add_serial_server

LABEL = """^XA

^FX Top section with logo, name and address.
^CF0,60
^FO50,50^GB100,100,100^FS
^FO75,75^FR^GB100,100,100^FS
^FO93,93^GB40,40,40^FS
^FO220,50^FDIntershipping, Inc.^FS
^CF0,30
^FO220,115^FD1000 Shipping Lane^FS
^FO220,155^FDShelbyville TN 38102^FS
^FO220,195^FDUnited States (USA)^FS
^FO50,250^GB700,3,3^FS

^XZ"""


class CustomCommand(Command):
    """Class to implement the custom command"""
    def __init__(self) -> None:
        super().__init__(keyword='measure_pcb')
        self.__server = add_tcp_server(host='localhost', port=65432)
        self.__server.register_callbacks(received=self.tcp_received)
        self.__serial = add_serial_server('COM7')
        self.__serial.register_callback(self.serial_received)

    def tcp_received(self, msg: str):
        print("measure_pcb got:", msg)

    def serial_received(self, msg: str):
        print("serial got", msg)

    def target(self):
        print("Measuring pcb")
        self.__serial.send(LABEL)

        sleep(5)
        self._command_result = 'OK'
