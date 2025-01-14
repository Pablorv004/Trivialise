from GUI.connecting import open_connecting_window
from GUI.lobby import open_lobby_window
from connection import TriviaClient

def start_client(server_ip):
    client = TriviaClient(host=server_ip)
    open_connecting_window()

if __name__ == "__main__":
    server_ip = input("Enter the server IP address: ").strip()
    start_client(server_ip)
