import tkinter as tk
from connection import TriviaClient
from Client.GUI.Auth.authwindow import open_establish_name_window

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
            self.master.destroy()  # Close the connecting window
            open_establish_name_window(self.client)
        except Exception as e:
            self.display_error(str(e))

def open_connecting_window():
    root = tk.Tk()
    app = ConnectingWindow(root)
    root.after(100, app.connect_to_server)  # Attempt to connect after 100ms
    root.mainloop()
