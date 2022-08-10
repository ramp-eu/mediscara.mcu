import logging
from mcu.models.command import Command
from mcu.config import add_serial_server

KEY_PWM = "pwm"
KEY_DUTY = "duty"
KEY_SHUTTER = "shutter"

class CustomCommand(Command):
    """Custom command class to implement laser cutter control
    """
    def __init__(self) -> None:
        super().__init__(keyword="laser_control")
        self.__serial = add_serial_server('COM10')
        self.__serial.register_callback(self.serial_received)

    def serial_received(self, msg: str):
        logging.info("Arduino msg: %s", msg)

    def target(self, *args):
        for arg in args:
            if isinstance(arg, dict):
                match = False

                keys = arg.keys()
                if KEY_PWM in keys:
                    if arg[KEY_PWM]:
                        self.__serial.send('pwm|on|\n')  # turn on the pwm

                    else:
                        self.__serial.send('pwm|off|\n')  # turn off the pwm

                    match = True

                if KEY_DUTY in keys:
                    duty = arg[KEY_DUTY]

                    if not isinstance(duty, (int, float)):
                        self._command_result = "Invalid command"

                    else:
                        self.__serial.send(f'duty|{arg[KEY_DUTY]}|\n') # set the power

                    match = True

                if KEY_SHUTTER in keys:
                    if arg[KEY_SHUTTER]:
                        self.__serial.send('shutter|on|\n')  # turn on the shutter

                    else:
                        self.__serial.send('shutter|off|\n')  # turn off the shutter

                    match = True

                if not match:
                    self._command_result = 'Invalid command'
                    return

                self._command_result = "OK"
                return

        self._command_result = "Invalid command"
