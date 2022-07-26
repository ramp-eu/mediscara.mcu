from time import sleep
from serial import serial_for_url


def main():
    port = serial_for_url('loop://')
    try:
        while True:
                if port.in_waiting:
                    data = port.read_all.decode()
                    print(data)

                sleep(0.1)
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()