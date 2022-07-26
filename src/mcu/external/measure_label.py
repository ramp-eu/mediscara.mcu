"""Module for the custom command 'measure_label'"""
import logging
from time import sleep
from mcu.models.command import Command


class CustomCommand(Command):
    """Class for the custom command"""
    def __init__(self):
        super().__init__(keyword="measure_label")

    def target(self):
        logging.info("Measuring label")
        sleep(5)
        self._command_result = "OK"
