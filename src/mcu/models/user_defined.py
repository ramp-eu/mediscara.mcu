"""Module for abstract base classes to be overridden and used as commands"""
from __future__ import annotations
from abc import ABC, abstractmethod
import importlib
from inspect import isabstract, isclass
import logging
import os
import pkgutil
from threading import Thread
from typing import List, Tuple

import requests

from mcu import external
from .mixins import SkipMixin


# get environment variables
API_KEY = os.getenv("API_KEY")
FIWARE_SERVICE = os.getenv("FIWARE_SERVICE")
FIWARE_SERVICEPATH = os.getenv("FIWARE_SERVICEPATH")
MCU_ID = os.getenv("MCU_ID")
IOTA_URL = os.getenv("IOTA_URL")
IOTA_PATH = os.getenv("IOTA_PATH")


class Service(ABC):
    """Base class for defining services"""

    @staticmethod
    def update_attribute(attribute: str, info: str | int | float | bool):
        """Send a post request updating the given attribute"""
        try:
            response = requests.post(
                f"{IOTA_URL}/{IOTA_PATH}",
                headers={
                    "fiware-service": FIWARE_SERVICE,
                    "fiware-servicepath": FIWARE_SERVICEPATH,
                    "Content-Type": "application/json",
                },
                params={"k": API_KEY, "i": MCU_ID},
                json={attribute: info},
                timeout=1,
            )

            if response.status_code != 200:
                logging.warning(
                    "Could not update attribute '%s': (%s) %s",
                    attribute,
                    response.status_code,
                    response.content.decode("utf-8"),
                )
        except requests.ConnectionError:
            logging.warning("Unable to reach server")

    @staticmethod
    def update_attributes(attributes: dict):
        """Updates attributes

        Args:
            attributes (dict): the attributes in a key-value format
        """

        for attribute, info in attributes.items():

            if not isinstance(attribute, str):
                logging.warning(
                    "Attribute name should be string, instead it is %s", type(attribute)
                )
                continue

            if not isinstance(info, str | int | float | bool):
                logging.warning(
                    "Attribute value should be one of the following: str, float, int, bool, instead: %s",
                    type(info),
                )
                continue

            Command.update_attribute(attribute, info)


class Command(Service):
    """Base class for defining commands that conform to the IoT Agent JSON's scheme"""

    def __init__(self, keyword: str) -> None:
        super().__init__()
        self.__thread = None
        self.__keyword = keyword

        self.result = None

    def execute(self, payload):
        """Executes the service in a separate background thread"""
        self.result = None
        self.__thread = Thread(target=self._target_inner, args=[payload], daemon=True)
        self.__thread.start()

    def _target_inner(self, payload):
        try:
            self.target(payload)

        except Exception as error:  # pylint: disable=broad-except
            logging.info(
                "An exception occurred while executing command: %s", str(error)
            )

        self._on_finished()

    def _on_finished(self):
        if self.result is None:
            logging.warning(
                "The class should set the _result attribute before the end of the '%s' method",
                self.target.__name__,
            )
            return

        self.update_attribute(
            attribute=f"{self.__keyword}_info",
            info=self.result,
        )

    @property
    def running(self):
        """Returns wether or not the command is currently running"""
        if self.__thread is None:
            return False

        return self.__thread.is_alive()

    @abstractmethod
    def target(self, *args):
        """The target function of the thread running the command

        The child class must override this method

        NOTE: The child class should set the _command_result attribute
        before the method finishes execution
        """

    @property
    def keyword(self):
        """Returns the keyword of this command"""
        return self.__keyword


def load() -> Tuple[List[Command], List[Service]]:
    """Loads command and service classes from the 'external' directory"""
    # get the path of the external package
    pkg_path = os.path.dirname(external.__file__)
    # get a list of modules in the package
    external_modules = [name for _, name, _ in pkgutil.iter_modules([pkg_path])]

    external_command_instances: List[Command] = []
    external_service_instances: List[Command] = []

    # iterate through the modules
    for module in external_modules:
        imported = importlib.import_module(f"mcu.external.{module}")

        # get the properties and methods of the module (strings)
        props = dir(imported)

        # only check the class if it is not marked for skipping
        if SkipMixin.__name__ not in props:
            # get the class
            for prop in props:
                # check if the attribute is a class
                attr = getattr(imported, prop)

                if isclass(attr):
                    # check if the class is not abstract
                    if not isabstract(attr):
                        try:
                            # only get service or command subclasses
                            # command has to come first, because a command is a subclass of service
                            if issubclass(attr, Command):
                                instance = attr()
                                external_command_instances.append(instance)
                                continue

                            elif issubclass(attr, Service):
                                instance = attr()
                                external_service_instances.append(instance)
                                continue

                        # if the __init__ method requires arguments, a TypeError is raised
                        except TypeError as err:
                            logging.warning(err.args)
                            logging.warning(
                                "'%s' should not have arguments.", attr.__name__
                            )

    return external_command_instances, external_service_instances
