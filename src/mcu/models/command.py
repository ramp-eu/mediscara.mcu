"""Module for abstract base classes to be overridden and used as commands"""
from __future__ import annotations
from abc import ABC, abstractmethod
import importlib
import logging
import os
import pkgutil
from threading import Thread
from typing import List

import requests

from mcu import external

CLASS_NAME = "CustomCommand"

# get environment variables
API_KEY = os.getenv('API_KEY')
FIWARE_SERVICE = os.getenv('FIWARE_SERVICE')
FIWARE_SERVICEPATH = os.getenv("FIWARE_SERVICEPATH")
MCU_ID = os.getenv('MCU_ID')
IOTA_URL = os.getenv('IOTA_URL')
IOTA_PATH = os.getenv('IOTA_PATH')

class Command(ABC):
    """Base class for defining commands that conform to the IoT Agent JSON's scheme
    """
    def __init__(self, keyword: str) -> None:
        self.__keyword = keyword
        self.__thread = None
        self._command_result = None

    def execute(self, payload):
        """Executes the command in a separate thread in the background
        """
        self._command_result = None
        self.__thread = Thread(target=self.__target_inner, args=[payload], daemon=True)
        self.__thread.start()

    def __target_inner(self, payload):
        try:
            self.target(payload)

        except Exception as error: # pylint: disable=broad-except
            logging.info("An exception occurred while executing command: %s", str(error))

        self.__on_finished()

    @abstractmethod
    def target(self, *args):
        """The target function of the thread running the command

        The child class must override this method

        NOTE: The child class should set the _command_result attribute
        before the method finishes execution
        """

    def __on_finished(self):
        if self._command_result is None:
            logging.warning(
                "The class should set the _command_result attribute before finishing the command",
                )
            return

        self.update_attribute(
            attribute=f'{self.__keyword}_info',
            info=self._command_result,
            )

    @property
    def keyword(self):
        """Returns the keyword of this command"""
        return self.__keyword

    @property
    def running(self):
        """Returns wether or not the command is currently running"""
        if self.__thread is None:
            return False

        return self.__thread.is_alive()

    @staticmethod
    def load_commands() -> List[Command]:
        """Loads command classes from the 'external' directory
        """
        pkg_path = os.path.dirname(external.__file__)
        external_modules = [name for _, name, _ in pkgutil.iter_modules([pkg_path])]

        external_command_instances: List[Command] = []

        for module in external_modules:
            imported = importlib.import_module(f"mcu.external.{module}")
            try:
                klass = getattr(imported, CLASS_NAME)
                instance = klass()
                if not isinstance(instance, Command):
                    logging.warning(
                        "Class %s in module %s should inherit the %s class",
                        instance.__name__,
                        imported,
                        Command.__name__
                        )
                    continue

                external_command_instances.append(instance)

            except AttributeError:
                logging.warning("Module %s should have a class named %s",
                                imported,
                                CLASS_NAME,
                                )

            except TypeError as error:
                # gets thrown when there is a missing argument
                logging.warning(
                    "%s class should not have positional arguments: %s",
                    klass.__name__,
                    str(error)
                    )

        return external_command_instances

    @staticmethod
    def update_attribute(attribute: str, info: str):
        """Send a post request updating the given attribute"""
        try:
            response = requests.post(f'{IOTA_URL}/{IOTA_PATH}',
                                    headers={
                                        'fiware-service': FIWARE_SERVICE,
                                        'fiware-servicepath': FIWARE_SERVICEPATH,
                                        'Content-Type': 'application/json',
                                    },
                                    params={
                                        'k': API_KEY,
                                        'i': MCU_ID
                                    },
                                    json={
                                        attribute: info
                                    })

            if response.status_code != 200:
                logging.warning(
                    "Could not update attribute '%s': (%s) %s",
                    attribute,
                    response.status_code,
                    response.content.decode('utf-8')
                    )
        except requests.ConnectionError:
            logging.warning("Unable to reach server")
