from time import sleep
from mcu.connectors.tcp import TCPServer

def test_tcp():
    def connected(peer: str):
        print(f"Connected to: {peer}")

    def received(msg: str):
        print(f"Received: {msg}")
    try:
        TCPServer(connection_made_callback=connected,
                  data_received_callback=received,
                  ).start()
        while True:
            sleep(2)
            print("running")

    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    test_tcp()