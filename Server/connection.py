import socket
import threading

class TriviaServer:
    # ...existing code...

    def start_server(self, host='0.0.0.0', port=12345):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host, port))
        server_socket.listen(5)
        print(f"Server started on {host}:{port}")

        def handle_client(client_socket):
            while True:
                try:
                    message = client_socket.recv(1024).decode('utf-8')
                    if not message:
                        break
                    print(f"Received message: {message}")
                    # ...handle the message...
                except ConnectionResetError:
                    break
            client_socket.close()

        while True:
            client_socket, addr = server_socket.accept()
            print(f"Connection from {addr}")
            client_handler = threading.Thread(target=handle_client, args=(client_socket,))
            client_handler.start()
    