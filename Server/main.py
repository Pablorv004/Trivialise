import threading
from connection import TriviaServer

def start_server():
    server = TriviaServer()
    server_thread = threading.Thread(target=server.start_server)
    server_thread.start()
    return server

if __name__ == "__main__":
    server = start_server()
    print()
    while True:
        user_input = input("Type 'exit' to stop the server: ").strip().lower()
        if user_input == 'exit':
            print("Stopping the server...")
            for client in server.clients:
                client.close()
            server.game_ongoing = False
            break
        else:
            print("Invalid input. Please type 'exit'.")
    print("Server stopped.")
    exit()
