import tkinter as tk
from tkinter import messagebox
import threading
import time

class GameWindow:
    def __init__(self, master, client, geometry=None):
        self.master = master
        self.client = client
        self.master.title("Trivia Game")
        if geometry:
            self.master.geometry(geometry)
        self.selected_answer = None

        # Question area
        self.question_label = tk.Label(master, text="", wraplength=400, justify=tk.LEFT)
        self.question_label.pack(pady=20)

        # Timer
        self.timer_label = tk.Label(master, text="", font=("Helvetica", 16))
        self.timer_label.pack(pady=10)

        # Answer buttons
        self.answer_buttons = {}
        for i in range(4):
            btn = tk.Button(master, text=f"Answer {chr(65+i)}", command=lambda i=i: self.select_answer(chr(65+i)))
            btn.pack(fill=tk.X, padx=20, pady=5)
            self.answer_buttons[chr(65+i)] = btn

        # Leaderboard
        self.leaderboard_frame = tk.Frame(master)
        self.leaderboard_frame.pack(side=tk.RIGHT, padx=20, pady=20)
        self.leaderboard_labels = []

        # Start thread to receive questions
        self.receive_thread = threading.Thread(target=self.receive_questions)
        self.receive_thread.start()

    def select_answer(self, answer):
        if self.selected_answer is None:
            self.selected_answer = answer
            self.answer_buttons[answer].config(bg="green")
            self.client.send_message(f"ANSWER:{answer}")

    def receive_questions(self):
        while True:
            message = self.client.receive_message()
            if message.startswith("QUESTION:"):
                self.question_label.config(text=message.split("QUESTION:")[1])
            elif message.startswith("ANSWER_"):
                answer_key = message.split(":")[0].split("_")[1]
                answer_text = message.split(":")[1]
                self.answer_buttons[answer_key].config(text=answer_text)
            elif message.startswith("TIMER:"):
                self.timer_label.config(text=message.split("TIMER:")[1])
            elif message.startswith("LEADERBOARD:"):
                leaderboard_data = message.split("LEADERBOARD:")[1].split(",")
                self.update_leaderboard(leaderboard_data)
            elif message.startswith("END_GAME:"):
                winner_message = message.split("END_GAME:")[1]
                messagebox.showinfo("Game Over", winner_message)
                geometry = self.master.winfo_geometry()
                self.master.destroy()
                from .lobby import open_lobby_window
                open_lobby_window(self.client, geometry)

    def update_leaderboard(self, data):
        for widget in self.leaderboard_frame.winfo_children():
            widget.destroy()
        for entry in data:
            username, score = entry.split(":")
            label = tk.Label(self.leaderboard_frame, text=f"{username}\nScore: {score}")
            label.pack(pady=5)
            self.leaderboard_labels.append(label)

def open_game_window(client, geometry=None):
    root = tk.Tk()
    app = GameWindow(root, client, geometry)
    root.mainloop()
