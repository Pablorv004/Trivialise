import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
import threading
import time
from GUI.game import open_game_window

class LobbyWindow:
    def __init__(self, master, client, geometry=None):
        self.master = master
        self.client = client
        self.username = client.username
        self.master.title(f"Lobby - {self.username}")
        if geometry:
            self.master.geometry(geometry)
        self.settings = {"amount": 10, "difficulty": "Any Difficulty"}

        # Load and display logo
        logo = Image.open("resources/logo.png")
        logo = logo.resize((200, 100), Image.ANTIALIAS)
        self.logo_img = ImageTk.PhotoImage(logo)
        self.logo_label = tk.Label(master, image=self.logo_img)
        self.logo_label.pack(pady=20)

        # Player list
        self.player_frames = []
        for i in range(4):
            frame = tk.Frame(master, width=200, height=50, relief=tk.RAISED, borderwidth=2)
            frame.pack(pady=5)
            self.player_frames.append(frame)

        # Buttons
        self.settings_button = tk.Button(master, text="Settings", command=self.open_settings)
        self.settings_button.pack(side=tk.LEFT, padx=20)

        self.start_button = tk.Button(master, text="Start", command=self.start_game)
        self.start_button.pack(side=tk.LEFT, padx=20)

        self.leave_button = tk.Button(master, text="Leave", command=self.leave_lobby)
        self.leave_button.pack(side=tk.LEFT, padx=20)

        # Start thread to update player list
        self.update_thread = threading.Thread(target=self.update_player_list)
        self.update_thread.start()

    def open_settings(self):
        settings_dialog = tk.Toplevel(self.master)
        settings_dialog.title("Settings")

        tk.Label(settings_dialog, text="Amount of Questions:").pack(pady=5)
        amount_var = tk.IntVar(value=self.settings["amount"])
        amount_entry = tk.Entry(settings_dialog, textvariable=amount_var)
        amount_entry.pack(pady=5)

        tk.Label(settings_dialog, text="Difficulty:").pack(pady=5)
        difficulty_var = tk.StringVar(value=self.settings["difficulty"])
        difficulty_options = ["Any Difficulty", "Easy", "Normal", "Hard"]
        difficulty_menu = tk.OptionMenu(settings_dialog, difficulty_var, *difficulty_options)
        difficulty_menu.pack(pady=5)

        def apply_settings():
            amount = amount_var.get()
            if 5 <= amount <= 50:
                self.settings["amount"] = amount
            else:
                messagebox.showerror("Invalid Input", "Amount must be between 5 and 50.")
                return
            self.settings["difficulty"] = difficulty_var.get()
            settings_dialog.destroy()

        tk.Button(settings_dialog, text="Cancel", command=settings_dialog.destroy).pack(side=tk.LEFT, padx=20, pady=20)
        tk.Button(settings_dialog, text="Apply", command=apply_settings).pack(side=tk.RIGHT, padx=20, pady=20)

    def start_game(self):
        self.show_loading_spinner()
        self.client.send_message("START_GAME")
        response = self.client.receive_message()
        if response == "START_GAME_SUCCESS":
            geometry = self.master.winfo_geometry()
            self.master.destroy()
            from .game import open_game_window
            open_game_window(self.client, geometry)
        else:
            self.hide_loading_spinner()
            messagebox.showerror("Error", "Failed to start the game.")

    def leave_lobby(self):
        if messagebox.askokcancel("Leave Lobby", "Are you sure you want to leave the lobby?"):
            self.client.close_connection()
            self.master.destroy()

    def update_player_list(self):
        while True:
            # Simulate getting player list from server
            player_list = self.client.get_player_list()
            for i, frame in enumerate(self.player_frames):
                for widget in frame.winfo_children():
                    widget.destroy()
                if i < len(player_list):
                    player_label = tk.Label(frame, text=player_list[i])
                    player_label.pack()
                else:
                    spinner = tk.Label(frame, text="Loading...")
                    spinner.pack()
            time.sleep(1)

    def show_loading_spinner(self):
        self.loading_frame = tk.Frame(self.master, bg='black', opacity=0.5)
        self.loading_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.spinner_label = tk.Label(self.loading_frame, text="Loading...", fg='white', bg='black', font=("Helvetica", 16))
        self.spinner_label.pack(expand=True)

    def hide_loading_spinner(self):
        self.loading_frame.destroy()

def open_lobby_window(client, geometry=None):
    root = tk.Tk()
    app = LobbyWindow(root, client, geometry)
    root.mainloop()
