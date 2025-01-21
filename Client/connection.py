import socket
import json
import select

class TriviaClient:
    def __init__(self, host='158.179.218.47', port=12346):
        self.server_host = host
        self.server_port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.username = None

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
            self.close_connection()

    def receive_message(self):
        try:
            message = self.client_socket.recv(1024).decode('utf-8')
            if message == "READY_ACK":
                print("Ready acknowledged by server.")
            return message
        except ConnectionResetError:
            print("Connection closed by the server.")
            self.close_connection()
            return None

    def receive_message_non_blocking(self):
        try:
            ready = select.select([self.client_socket], [], [], 0.1)
            if ready[0]:
                return self.client_socket.recv(1024).decode('utf-8')
            return None
        except ConnectionResetError:
            print("Connection closed by the server.")
            self.close_connection()
            return None

    def close_connection(self):
        self.client_socket.close()
        print("Connection closed.")
        exit()
