
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

        self._rp = False
        self._rr = False
        self._rw = False
        self._re = False

        initial_attributes = {
            self.ROBOT_POWER: self._rp,
            self.ROBOT_RUNNING: self._rr,
            self.ROBOT_WAITING: self._rw,
            self.ROBOT_ERROR: self._re,
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

            rp = msg.data[0] == "TRUE"
            rr = msg.data[1] == "TRUE"
            rw = msg.data[2] == "TRUE"
            re = msg.data[3] == "TRUE"

            if rp != self._rp or rr != self._rr or rw != self._rw or re != self._re:

                self._rp = rp
                self._rr = rr
                self._rw = rw
                self._re = re

                try:
                    attributes = {
                        self.ROBOT_POWER: self._rp,
                        self.ROBOT_RUNNING: self._rr,
                        self.ROBOT_WAITING: self._rw,
                        self.ROBOT_ERROR: self._re,
                    }

                    logging.info("Updating attributes to: %s", attributes)

                except IndexError:
                    logging.warning("Invalid status message: %s", msg)
                    return

                Command.update_attributes(attributes)
