import socket

def main():
    try:
        file = open('log.txt', 'w', encoding='utf-8')

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        client.connect(('localhost', 9105))
        print('Robot connected')
        server.bind(('localhost', 9106))
        server.listen()
        conn, addr = server.accept()
        print("Kide connected")

        client_is_next = True
        client_message = ''
        server_message = ''

        with conn:
            client.setblocking(False)
            conn.setblocking(False)
            while True:
                if client_is_next:
                    client_is_next = False
                    try:
                        client_sent = client.recv(1024)
                        for byte in client_sent:
                            char = chr(byte)
                            if char.isascii():
                                client_message += char

                                if char == '>':
                                    file.write(f'R: {client_message}')
                                    client_message = ''

                            else:
                                client_message += hex(byte)

                        conn.sendall(client_sent)

                    except BlockingIOError:
                        continue

                else:
                    client_is_next = True
                    # server sends data
                    try:
                        server_sent = conn.recv(1024)
                        file.write(f'{server_sent}')
                        for byte in server_sent:
                            char = chr(byte)
                            if char.isascii():
                                server_message += char

                                if char == '\n':
                                    file.write(f'K: {server_message}')
                                    server_message = ''

                            else:
                                server_message += hex(byte)

                        client.sendall(server_sent)

                    except BlockingIOError:
                        continue

    except KeyboardInterrupt:
        file.close()


if __name__ == '__main__':
    main()