# Master Control Unit

This component serves as an IoT Device connected to a [FIWARE IoT Agent (JSON Payload)](https://github.com/FIWARE/tutorials.IoT-Agent-JSON/tree/131931b2e0460efbacd598c4c16b39872afa8042).
The Master Control Unit (MCU) can be used to achieve communication to embedded devices which do not support the [NGSI-v2](https://fiware-tutorials.readthedocs.io/en/stable/getting-started/index.html) data models.

## Configuration

The package behavior can be customized with the `.env` file in the root of the project.

> HOST: the host of the web api (set it to `0.0.0.0` to allow external communication)
>
> PORT: the port of the web api
>
> API_KEY: the application key defined in the IoT Agent
>
> FIWARE_SERVICE: the fiware-service header defined in the IoT Agent
>
> FIWARE_SERVICEPATH: the fiwre-servicepath header defined in the IoT Agent
>
> MCU_ID: the id of the MCU in the IoT Agent's devices
>
> IOTA_URL: the url of the IoT Agent
>
> IOTA_PATH: the path of the IoT Agent (default is /iot/json)

> The HOST and PORT environment variables **must be set**

## Custom commands

The IoT Agent sends commands downstream. These commands arrive as Http POST requests to the */api* endpoint.
In order to give more flexibility to the end user, there are predefined classes and helper methods to make customization easier.

### Issuing a custom command:

To issue a new custom command create a new python file in the external package (src/mcu/external).
The name can be anything, however it is advised to be the same as the command name for clarity and code readability.
In this new command file create a class named `CustomCommand` that has the parent class `Command`. This is what the file should look like now:
```python
from mcu.models.command import Command

class CustomCommand(Command):
    """Class for the custom command"""
    def __init__(self):
        super().__init__(keyword="measure_label")
```
The `super().__init__()` method requires a keyword argument. The command will be executed based on this keyword.

> Note:
>
> The `__init__()` method should not take any arguments besides `self`

> If these requirements are not met, the command **will not be used in the program**.

The command class should also override the `target` method from its parent. This method gets called when the command gets executed. To achieve the correct functionality, the child class must also set
the `_command_result` attribute in this method. This value will be set as the command info attribute in the OCB.

```py
    def target(self):
        # Execute the command logic
        self._command_result = 'OK'
```

This example would set the `measure_label_info` attribute to `OK`.
This attribute is used with subscriptions to notify the command's sender of the result.

The runtime also lets the user use communication protocols such as:
- TCP/IP (socket)
- Serial

These communication protocols are implemented in a way that they are non-blocking and use a callback-based communication.

---
### TCP Server

To create a new TCP Server, use the `add_tcp_server` method from the `mcu.config` module:

```py
from mcu.config import add_tcp_server

class CustomCommand(Command):
    """Class for the custom command"""
    def __init__(self):
        super().__init__(keyword="measure_label")
        self.__server = add_tcp_server(host='localhost', port=65432)
        self.__server.register_callbacks(received=self.tcp_received)

    def tcp_received(self, msg: str):
        # process the received message
```

In this example, the command uses a TCP server attached to `localhost` and listening at port `65432`.
The `register_callbacks` method is used to register callbacks to events related to the server (data reception in this example). These events can be:
- a new client has connected
- a connection was lost
- a message was received

---
### Socket server

To create a new Socket Server, use the `add_socket_server` method from the `mcu.config` module:

```py
from mcu.config import add_serial_server

class CustomCommand(Command):
    """Class to implement the custom command"""
    def __init__(self) -> None:
        super().__init__(keyword='measure_pcb')
        self.__serial = add_serial_server('COM7')
        self.__serial.register_callback(self.serial_received)

    def serial_received(self, msg: str):
        # process the received message
```

In this example the command uses a Serial Server using the 'COM8' port.
The `register_callback` method is used to register a callback. This callback method gets called whenever new data is incoming from the serial port.

> If the port value is omitted, the server connects to the `loop://` url. This is a serial loopback url,
and it echoes back all traffic. This can be useful for debugging.

---

### Notes on the servers

These server instances are not exclusive to the command instances. This means that more than one
command can use the same server for communication. To avoid unvanted results the user should implement
some form of logic to elliminate errors that could occur when a command's response is received by
another command.


## Communication protocol

A minimal communication protocol between the MCU and the IoT device is necessary.
In this protocol, the MCU is the master and the IoT device is the slave.

Messages:
- `IAC`
- `RUN`
- `RESULT`

Responses:
- `OK`
- `ERROR`
- `BUSY`

### Message descriptions
---
### `IAC` message
Interpret As Command. This message tells the other side to execute the data in the message.

> Syntax: `IAC|<command to be executed>`
>
> Response is **required**.

### `RUN` message
This message is used to tell the device to execute a specific program stored in its memory.

> Syntax: `RUN|<job name>`
>
> Response is **required**.

### `RESULT` message
This message is used to inform the other side that the requested program has finished with the following result.

> Syntax: `RESULT|SUCCESS or ERROR|<optional message>`
>
> Response is **not required**.
