"""This is an example module demonstrating the usage of the MMCU"""


# import the command class
from mcu.models.user_defined import Command

# import the necessary methods for registering embedded communication protocols
from mcu.config import add_serial_server, add_tcp_server


class ExampleCommand(Command):
    """This is the example command class that is run by the MCU

    It should always inherit from the Command class imported above

    This class sends a message via TCP socket and serial communication whenever the incoming command
    contains the 'exampleKeyword' key. 
    The command is sent from an IoT Agent and it uses the JSON protocol as its payload.
    """

    # The init method should not take any parameters except self
    def __init__(self) -> None:
        # register the superclass with the keyword
        # whenever a new FIWARE command comes in and matches with the given keyword, the class' 'target' method will be executed
        super().__init__(keywords=['exampleKeyword'])

        # request a serial server instance from the MCU runtime
        self.serial = add_serial_server('COM8', baudrate=9600)

        # register a callback for incoming serial messages
        self.serial.register_callback(received=self.on_serial_received)

        # request a tcp socket server from the runtime
        self.tcp = add_tcp_server('localhost', 6900)

        # register callback methods for the events regarding the server
        self.tcp.register_callbacks(connected=self.on_tcp_connected,
                                    lost=self.on_tcp_connection_lost,
                                    received=self.on_tcp_received
                                    )

    def target(self, *args, keyword: str):
        """This method is executed whenever one of the registered keywords match the incoming request"""
        message = "Hello from the MCU 🖐"

        # send a message via socket
        self.tcp.send(message)

        # send a message via serial
        self.serial.send(message)

        # report back to the runtime
        # this message will be sent to the Orion Contect Broker via the IoT Agent (JSON)
        self.result = "OK"

    def on_serial_received(self, msg: bytes):
        """This method gets called whenever a new serial message comes in"""
        print(f"New serial message: {msg.decode()}")

    def on_tcp_connected(self, client: str):
        """This method is called when a new socket client is connected to the server"""
        print(f"New connection from {client}")

    def on_tcp_connection_lost(self):
        """This method is called when a socket client is disconnected from the server"""
        print("A client has disconnected")

    def on_tcp_received(self, msg: bytes):
        """This method is called when data is received from a socket client"""
        print("Incoming message: ", msg.decode())
