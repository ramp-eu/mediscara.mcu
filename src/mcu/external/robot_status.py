
import logging
from mcu.models.user_defined import Command, Service
from mcu.config import add_tcp_server
from mcu.protocols import Message


class RobotStatusService(Service):
    """Service class for processing robot status messages"""

    ROBOT_POWER = 'robotPower'
    ROBOT_RUNNING = 'robotRunning'
    ROBOT_WAITING = 'robotWaiting'
    ROBOT_ERROR = 'robotError'

    def __init__(self) -> None:
        self.__tcp = add_tcp_server('0.0.0.0', 65432)
        self.__tcp.register_callbacks(received=self.__tcp_received)

        initial_attributes = {
            self.ROBOT_POWER: False,
            self.ROBOT_RUNNING: False,
            self.ROBOT_WAITING: False,
            self.ROBOT_ERROR: False,
        }

        Command.update_attributes(initial_attributes)

    def __tcp_received(self, message: bytes):
        msg = Message.parse(message=message)

        # process the status message
        # status message syntax:
        #   STATUS| TRUE  |  TRUE  |  TRUE  |  FALSE
        #           ^^^^     ^^^^     ^^^^     ^^^^^
        #          POWER   RUNNING   WAITING   ERROR

        if msg.type == Message.TYPE.STATUS:
            logging.info(msg)
            try:
                attributes = {
                    self.ROBOT_POWER: msg.data[0] == "TRUE",
                    self.ROBOT_RUNNING: msg.data[1] == "TRUE",
                    self.ROBOT_WAITING: msg.data[2] == "TRUE",
                    self.ROBOT_ERROR: msg.data[3] == "TRUE"
                }

                logging.info("Updating attributes to: %s", attributes)

            except IndexError:
                logging.warning("Invalid status message: %s", msg)
                return

            Command.update_attributes(attributes)