from GUI.connecting import open_connecting_window
from connection import TriviaClient

def start_client():
    TriviaClient()
    open_connecting_window()

if __name__ == "__main__":
    start_client()
