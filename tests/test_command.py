"""Test module for the custom commands"""
from time import sleep
from mcu.models.command import Command



def test_execute_command():
    """Tests command execution"""
    def dummy_callback(attr: str, info: str):
        print(f"{attr=}, {info=}")

    commands = Command.load_commands()

    for command in commands:
        command.execute(update_attribute_callback=dummy_callback)

    sleep(6)

if __name__ == '__main__':
    test_execute_command()
