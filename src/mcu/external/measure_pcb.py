"""Module for the custom command'measure_pcb'"""
from time import sleep
from mcu.models.command import Command


class CustomCommand(Command):
    """Class to implement the custom command"""
    def __init__(self) -> None:
        super().__init__(keyword='measure_pcb')

    def target(self):
        print("Measuring pcb")
        sleep(5)
        self._command_result = 'OK'
