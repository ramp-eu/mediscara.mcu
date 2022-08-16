"""Module to configure the connections"""
import logging
from typing import List

from mcu.connectors.serial_connection import SerialServer
from mcu.models.command import Command
from .connectors.tcp_connection import TCPCLient, TCPServer

TCP_CONNECTIONS: List[TCPServer|TCPCLient] = []
SERIAL_CONNECTIONS: List[SerialServer] = []

def add_tcp_server(host: str, port: int) -> TCPServer:
    """Use this method to add a TCP Server which will be started at runtime"""
    instance = TCPServer(host, port)
    if instance not in TCP_CONNECTIONS:
        TCP_CONNECTIONS.append(instance)

    return instance

def add_tcp_client(host: str, port: int) -> TCPCLient:
    """Use this method to add a TCP Client which will be started at runtime"""
    instance = TCPCLient(host, port)
    if instance not in TCP_CONNECTIONS:
        TCP_CONNECTIONS.append(instance)

    return instance

def add_serial_server(port: str = None, baudrate: int = 9600) -> SerialServer:
    """Use this method to add a Serial Server which will be started at runtime"""
    instance = SerialServer(port, baudrate)
    if instance not in SERIAL_CONNECTIONS:
        SERIAL_CONNECTIONS.append(instance)

    return instance

def report_error(error_msg: str):
    """This method can be used to report errors to the runtime"""
    logging.info('Got error: %s', error_msg)
    Command.update_attribute(attribute="e", info=error_msg)

def clear_errors():
    """This method can be used to clear previously set errors"""
    Command.update_attribute(attribute="e", info="")
