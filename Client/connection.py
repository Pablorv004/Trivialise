import socket

class TriviaClient:
    def __init__(self, host='127.0.0.1', port=12345):
        self.server_host = host
        self.server_port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect_to_server(self):
        try:
            self.client_socket.connect((self.server_host, self.server_port))
            print(f"Connected to server at {self.server_host}:{self.server_port}")
        except ConnectionRefusedError:
            print("Failed to connect to the server. Is it running?")

    def send_message(self, message):
        try:
            self.client_socket.sendall(message.encode('utf-8'))
        except BrokenPipeError:
            print("Failed to send message. Connection might be closed.")

    def receive_message(self):
        try:
            return self.client_socket.recv(1024).decode('utf-8')
        except ConnectionResetError:
            print("Connection closed by the server.")
            return None

    def close_connection(self):
        self.client_socket.close()
        print("Connection closed.")
