
from mcu.protocols import Message

def test_parsing():
    data = 'test data'
    msg = f'{Message.TYPE.IAC.value}|{data}'

    msg_instance = Message.parse(msg)

    assert msg_instance.type == Message.TYPE.IAC
    assert msg_instance.data == data

    print(f'{msg_instance}')

if __name__ == '__main__':
    test_parsing()
