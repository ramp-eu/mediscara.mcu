"""Module for handling communication with the laser controller"""
import logging
from mcu.models.user_defined import Command
from mcu.protocols import Message
from mcu.config import add_serial_server, add_tcp_server

KEY_PWM = "pwm"
KEY_DUTY = "duty"
KEY_SHUTTER = "shutter"


class LaserControl(Command):
    """Custom command class to implement laser cutter control"""

    def __init__(self) -> None:
        super().__init__(keyword="start_laser_cut")
        self.__serial = add_serial_server("/dev/ttyUSB0")
        self.__serial.register_callback(self.serial_received)

        self.__tcp = add_tcp_server("0.0.0.0", 65432)
        self.__tcp.register_callbacks(received=self.tcp_received)

    def tcp_received(self, msg: bytes):
        """Gets called when a tcp message is received"""
        message = Message.parse(msg)

        if message.type == Message.TYPE.IAC:
            if message.data[0] == "LASER_POWER":
                # set the laser power
                logging.debug("Setting duty cycle to %s", message.data[1])
                self.__serial.send(f"duty|{message.data[1]}|\n")

            elif message.data[0] == "START_LASER":
                logging.info("Starting laser")
                self.__serial.send("pwm|on|\n")

            elif message.data[0] == "STOP_LASER":
                logging.info("Stopping laser")
                self.__serial.send("pwm|off|\n")

        elif message.is_response:
            logging.info("Robot job: %s", message.type)

            self.update_attribute(f"{self.keyword}_info", message.type.value)

    def serial_received(self, msg: str):
        """Gets called when serial communication is received"""
        logging.info("Arduino msg: %s", msg)

    def target(self, *_):
        self.__tcp.send("RUN|prog1\n")
        self.result = ""
