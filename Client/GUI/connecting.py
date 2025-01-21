import tkinter as tk
from connection import TriviaClient
from GUI.Auth.authwindow import open_establish_name_window

class ConnectingWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Connecting")
        self.label = tk.Label(master, text="Connecting...")
        self.label.pack(pady=20)
        self.client = TriviaClient()

    def display_error(self, error_message):
        self.label.config(text=error_message)

    def connect_to_server(self):
        try:
            self.client.connect_to_server()
            message = self.client.receive_message()
            print("Received message:", message)
            if message == "GAME_ONGOING":
                self.display_error("Game is ongoing. Please try again later.")
                self.master.after(3000, self.master.destroy)
            elif message == "SERVER_FULL":
                self.display_error("Server is full. Please try again later.")
                self.master.after(3000, self.master.destroy)
            elif message == "CONNECTED":
                self.master.destroy()
                open_establish_name_window(self.client)
            else:
                self.display_error("Invalid message received.")
                self.master.after(3000, self.master.destroy)
        except Exception as e:
            self.display_error(str(e))

def open_connecting_window():
    root = tk.Tk()
    app = ConnectingWindow(root)
    root.after(100, app.connect_to_server)
    root.mainloop()
