import tkinter as tk
from tkinter import messagebox
import threading
import time

class GameWindow:
    def __init__(self, master, client):
        print("Initializing GameWindow...")
        self.master = master
        self.client = client
        self.master.title("Trivia Game")
        self.master.geometry("600x800")
        self.selected_answer = None

        # Question area
        self.question_label = tk.Label(master, text="Ready?", wraplength=400, justify=tk.LEFT)
        self.question_label.pack(pady=20)

        # Timer
        self.timer_label = tk.Label(master, text="", font=("Helvetica", 16))
        self.timer_label.pack(pady=10)

        # Answer buttons
        self.answer_buttons = {}
        self.answer_frame = tk.Frame(master)
        self.answer_frame.pack(pady=20)

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
            print(f"Received message: {message}")
            if message.startswith("QUESTION:"):
                self.question_label.config(text=message.split("QUESTION:")[1])
                self.reset_answers()
            elif "ANSWER_" in message:
                parts = message.split("ANSWER_")
                for part in parts[1:]:
                    if "TIMER:" in part:
                        answer_key, answer_text = part.split("TIMER:")[0].split(":", 1)
                        self.update_answer_button(int(answer_key), answer_text)
                        timer_value = part.split("TIMER:")[1]
                        self.timer_label.config(text=timer_value)
                    else:
                        answer_key, answer_text = part.split(":", 1)
                        self.update_answer_button(int(answer_key), answer_text)
            elif message.startswith("TIMER:"):
                self.timer_label.config(text=message.split("TIMER:")[1])
            elif message.startswith("LEADERBOARD:"):
                leaderboard_data = message.split("LEADERBOARD:")[1].split(",")
                self.update_leaderboard(leaderboard_data)
            elif message.startswith("END_GAME:"):
                winner_message = message.split("END_GAME:")[1]
                messagebox.showinfo("Game Over", winner_message)
                self.master.destroy()
                from .lobby import open_lobby_window
                print("Returning to lobby...")
                open_lobby_window(self.client)
            elif message.startswith("CORRECT_ANSWER:"):
                correct_answer = message.split("CORRECT_ANSWER:")[1]
                self.highlight_correct_answer(correct_answer)
            elif message.startswith("INCORRECT_ANSWER_"):
                parts = message.split("INCORRECT_ANSWER_")
                for part in parts[1:]:
                    answer_key, answer_text = part.split(":", 1)
                    self.highlight_incorrect_answer(int(answer_key), answer_text)

    def highlight_correct_answer(self, correct_answer):
        for key, btn in self.answer_buttons.items():
            if btn.cget("text") == correct_answer:
                btn.config(bg="green")

    def highlight_incorrect_answer(self, key, incorrect_answer):
        if self.selected_answer == key:
            self.answer_buttons[key].config(bg="red")

    def update_answer_button(self, key, text):
        if key not in self.answer_buttons:
            btn = tk.Button(self.answer_frame, text=f"Answer {key}", command=lambda k=key: self.select_answer(k))
            btn.pack(fill=tk.X, padx=20, pady=5)
            self.answer_buttons[key] = btn
        self.answer_buttons[key].config(text=text, bg="SystemButtonFace")

    def reset_answers(self):
        self.selected_answer = None
        for btn in self.answer_buttons.values():
            btn.destroy()
        self.answer_buttons.clear()

    def update_leaderboard(self, data):
        print("Updating leaderboard...")
        for widget in self.leaderboard_frame.winfo_children():
            widget.destroy()
        for entry in data:
            username, score = entry.split(":")
            label = tk.Label(self.leaderboard_frame, text=f"{username}\nScore: {score}")
            label.pack(pady=5)
            self.leaderboard_labels.append(label)

def open_game_window(client):
    print("Creating game window...")
    root = tk.Tk()
    app = GameWindow(root, client)
    root.mainloop()
