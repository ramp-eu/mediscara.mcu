
from mcu.config import add_tcp_server

def test_add_tcp():
    print(add_tcp_server('localhost', 65432))

if __name__ == "__main__":
    test_add_tcp()