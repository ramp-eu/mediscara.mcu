"""This module tests the command and service loading"""

import logging
from mcu.models.user_defined import load

def test_load():
    commands, services = load()
    logging.info("Got commands: %s", commands)
    logging.info("Got services: %s", services)


if __name__ == '__main__':
    test_load()
    pass