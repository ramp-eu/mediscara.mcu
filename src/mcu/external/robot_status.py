
from mcu.models.user_defined import Service


class RobotStatusService(Service):
    """Service class for processing robot status messages"""

    def target(self, payload):
        self.result = "OK"