# Master Control Unit

This component serves as an IoT Device connected to a [FIWARE IoT Agent (JSON Payload)](https://github.com/FIWARE/tutorials.IoT-Agent-JSON/tree/131931b2e0460efbacd598c4c16b39872afa8042)

## Communication protocol

A minimal communication protocol between the MCU and the IoT device is necessary.
In this protocol, the MCU is the master and the IoT device is the slave.

Master messages:
- `DO`
- `DO_JOB`

Slave messages:
- `JOB_RESULT`

Responses:
- `OK`
- `ERROR`
- `BUSY`

### Message descriptions
---
### `DO` message
This command is used to tell the device to execute a single command

> Syntax: `DO|<command to be executed>`
>
> Response is **required**.

### `DO_JOB` message
This command is used to tell the device to execute a specific program stored in its memory.

> Syntax: `DO_JOB|<job name>`
>
> Response is **required**.

### `JOB_RESULT` message
This message is used to inform the MCU that the requested program has finished with the following result.

> Syntax: `JOB_RESULT|SUCCESS or ERROR|<optional message>`
>
> Response is **not required**.
