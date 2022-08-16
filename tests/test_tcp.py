
from mcu.config import add_tcp_server

def main():
    print(add_tcp_server('localhost', 65432))

if __name__ == "__main__":
    main()