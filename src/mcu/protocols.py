"""Module for the communication protocol between the IoT Device and the MCU"""

from dataclasses import dataclass, field
from enum import Enum
from typing import ClassVar


@dataclass
class Message:
    """A representation of the messages in the protocol"""
    class TYPE(Enum):
        """Message types"""
        IAC = 'IAC'
        RUN = 'RUN'

        RESULT = 'RESULT'

        OK = 'OK'
        BUSY = 'BUSY'
        ERROR = 'ERROR'

    SUCCESS: ClassVar[str] = 'SUCCESS'
    ERROR: ClassVar[str] = 'ERROR'

    type: TYPE = field(default=None)
    data: str = field(default=None)
    additional: str = field(default=None)

    def __str__(self):
        if self.additional is not None:
            return f'{self.type}|{self.additional}|{self.data}'

        return f'{self.type}|{self.data}'

    @classmethod
    def parse(cls, message: str | bytes):
        """Parses the message string and converts it the a Message object"""
        if isinstance(message, bytes):
            message = message.decode()

        instance = cls()

        for type_ in Message.TYPE:
            if message.startswith(type_.value):
                instance.type = type_
                break

        if not instance.is_response:
            instance.data = message.split('|')[-1]

            if instance.type == Message.TYPE.RESULT:
                # get the SUCCESS or ERROR
                instance.additional = message.split('|')[1]

        return instance

    @property
    def is_response(self):
        """Returns wether the message is a response"""
        return self.type in (Message.TYPE.OK, Message.TYPE.BUSY, Message.TYPE.ERROR)
