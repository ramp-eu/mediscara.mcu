# Master Control Unit
[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg?style=flat)](https://github.com/RichardLitt/standard-readme)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
![codeql](https://github.com/ppuska/mediscara.mcu/actions/workflows/codeql.yml/badge.svg)
[![Known Vulnerabilities](https://snyk.io/test/github/ppuska/mediscara.mcu/badge.svg)](https://snyk.io/test/github/ppuska/mediscara.mcu)

This component serves as a proxy layer sending and receiving messages to and from a [FIWARE IoT Agent (JSON Payload)](https://github.com/FIWARE/tutorials.IoT-Agent-JSON/tree/131931b2e0460efbacd598c4c16b39872afa8042).
The Master Control Unit (MCU) can be used to achieve communication to embedded devices which do not support the HTTP transport protocol or the [NGSI-v2](https://fiware-tutorials.readthedocs.io/en/stable/getting-started/index.html) data model.

## Background

The IoT Agent is designed to relay north and southbound messages to and from IoT Devices.
It achieves this by relying on the HTTP protocol. This means that a very large part of devices are excluded from the communication.
To solve this problem, the MCU can process and relay southbound messages from the IoT Agent and use other communication protocols to connect devices to the Agent.

The MCU was tested on multiple shop floor machines:
- Kawasaki DuAro 2 using TCP socket communication
- GoDex label printer using serial communication

## Installation

> ### Pre-requisites
> 
> Download and install [Python](python.org). That's it!

To install the package and all of its dependencies, run
```
    pip install .
```


## Configuration

The package behavior can be customized with the `.env` file in the root of the project.
The following environment variables can be set:
- `HOST`: the host of the web api (set it to `0.0.0.0` to allow external communication)
- `PORT`: the port of the web api
- `API_KEY`: the application key defined in the IoT Agent
- `FIWARE_SERVICE`: the fiware-service header defined in the IoT Agent
- `FIWARE_SERVICEPATH`: the fiwre-servicepath header defined in the IoT Agent
- `MCU_ID`: the id of the MCU in the IoT Agent's devices
- `IOTA_URL`: the url of the IoT Agent
- `IOTA_PATH`: the path of the IoT Agent (default is /iot/json)

> The `HOST` and `PORT` environment variables **must be set**

## Custom commands

The IoT Agent sends commands downstream. These commands arrive as Http POST requests to the */api* endpoint.
In order to give more flexibility to the end user, there are predefined classes and helper methods to make customization easier.

### Issuing a custom command:

To issue a new custom command create a new python file in the external package (src/mcu/external).
The name can be anything, however it is advised to be the same as the command name for clarity and code readability.
In this new command file create a class that has the parent class `Command`. This is what the file should look like now:
```python
from mcu.models.command import Command

class ExampleCommand(Command):
    """Class for the custom command"""
    def __init__(self):
        super().__init__(keywords="measure_label")
```
The `super().__init__()` method requires an argument named `keywords`. This argument is either a list of strings or a string. 
When the southbound POST request contains the one of the keywords as a key, the command's `target` method will be executed. 

> Note:
>
> The `__init__()` method should not take any arguments besides `self` and `keywords`

> If these requirements are not met, the command **will not be used in the program**.

The command class should also override the `target` method from its parent. This method gets called when the command gets executed. To achieve the correct functionality, the child class must also set
the `result` attribute in this method. This value will be set as the command info attribute in the OCB.

```py
    def target(self, *args, keyword: str):
        # Execute the command logic
        self.result = 'OK'
```

This example would set the `measure_label_info` attribute to `OK`.
This attribute is used with subscriptions to notify the command's sender of the result.
The `keyword` parameter is used to inform the command class which of its keywords are being invoked.

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

## Custom services

The user can define services to interact with incoming data. Unlike the commands, the services do
not have a keyword and thus, do not get called.
Instead, use services to process incoming data. The data can be from TCP or Serial communication.

### Usage

To define a custom service, create a new python file in the external package (*src/mcu/external*).
In this file, create a class that inherits from the `Service` class.

Use the `__init__()` method to define the necessary communication protocols.

```python
from mcu.models.user_defined import Service
from mcu.config import add_tcp_server

class CustomService(Service):
    def __init__(self):
        self.__tcp = add_tcp_server('localhost', 65432)
        self.__tcp.register_callback(received=self.tcp_received)

    def tcp_received(self, message: bytes):
        """Process the incoming message"""
```

In this example a tcp server is registered, listening at port 65432. A callback is registered to
intercept incoming messages.

> If other commands have added the same tcp server then their communication messages will call the `tcp_received` method.

> NOTE: the `__init__(self)` method not take any arguments besides `self`

## Skipping modules

If the user defined additional command or service classes that they do not wish to include in the
program the `SkipMixin` class can be used to mark the given class.
This way the class will not be used.

```python
from mcu.models.user_defined import Service
from mcu.models.mixins import SkipMixin
from mcu.config import add_tcp_server

class CustomService(Service, SkipMixin):
    def __init__(self):
        self.__tcp = add_tcp_server('localhost', 65432)
        self.__tcp.register_callback(received=self.tcp_received)

    def tcp_received(self, message: bytes):
        """Process the incoming message"""
```

---

## Communication protocol guidelines

A minimal communication protocol between the MCU and the IoT device is necessary.
In the MediSCARA project, the following guidelines were implemented for communication with embedded devices.

Messages:
- `IAC`
- `RUN`
- `RESULT`
- `STATUS`

Responses:
- `OK`
- `ERROR`
- `BUSY`

### Message descriptions
---
### `IAC` message
Interpret As Command. This message tells the other side to execute the data in the message.

> Syntax: `IAC|<command to be executed>\n`

### `RUN` message
This message is used to tell the device to execute a specific program stored in its memory.

> Syntax: `RUN|<job name>\n`

### `STATUS` message
This message is used to send status information about the devices.

> Syntax: `STATUS|<first attribute>|<second attribute>|...\n`

### `RESULT` message
This message is used to inform the other side that the requested program has finished with the following result.

> Syntax: `RESULT|SUCCESS or ERROR|<optional message>\n`

---
> All of the messages are ended with a `\n` terminator character.