"""Module for the communication protocol between the IoT Device and the MCU"""

from dataclasses import dataclass, field
from enum import Enum
from typing import ClassVar, List


@dataclass
class Message:
    """A representation of the messages in the protocol"""
    class TYPE(Enum):
        """Message types"""
        IAC = 'IAC'
        RUN = 'RUN'

        RESULT = 'RESULT'
        STATUS = 'STATUS'

        OK = 'OK'
        BUSY = 'BUSY'
        ERROR = 'ERROR'

    SUCCESS: ClassVar[str] = 'SUCCESS'
    ERROR: ClassVar[str] = 'ERROR'

    type: TYPE = field(default=None)
    data: List[str] = field(default=None)

    raw: str = field(default=None)

    def __str__(self):
        return f'{self.type.value}|{"|".join(self.data)}'

    @classmethod
    def parse(cls, message: str | bytes | bytearray):
        """Parses the message string and converts it the a Message object"""
        if isinstance(message, (bytes, bytearray)):
            message = message.decode()

        instance = cls()

        instance.raw = message

        tokens = message.split('|')

        key = tokens[0]  # the first element
        instance.data = tokens[1:]  # all the other elements

        for type_ in Message.TYPE:
            if key == type_.value:
                instance.type = type_
                break

        return instance

    @property
    def is_response(self):
        """Returns wether the message is a response"""
        return self.type in (Message.TYPE.OK, Message.TYPE.BUSY, Message.TYPE.ERROR)
