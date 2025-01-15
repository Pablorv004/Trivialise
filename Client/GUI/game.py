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
        self.master.geometry("600x350")
        self.selected_answer = None
        self.answers_locked = False

        # Main frame
        self.main_frame = tk.Frame(master)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Left frame for question, timer, and answers
        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Question area
        self.question_label = tk.Label(self.left_frame, text="Ready?", wraplength=400, justify=tk.LEFT)
        self.question_label.pack(pady=20)

        # Timer
        self.timer_label = tk.Label(self.left_frame, text="", font=("Helvetica", 16))
        self.timer_label.pack(pady=10)

        # Answer buttons
        self.answer_buttons = {}
        self.answer_frame = tk.Frame(self.left_frame)
        self.answer_frame.pack(pady=20)

        # Right frame for leaderboard
        self.leaderboard_frame = tk.Frame(self.main_frame)
        self.leaderboard_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=20, pady=20)
        self.leaderboard_labels = []
        self.update_leaderboard([])  # Initialize leaderboard

        # Start thread to receive questions
        self.receive_thread = threading.Thread(target=self.receive_questions)
        self.receive_thread.start()

        self.master.bind("<Button-1>", self.on_button_press)

    def select_answer(self, answer_key):
        if self.selected_answer is None and not self.answers_locked:
            self.selected_answer = answer_key
            self.answer_buttons[answer_key].config(bg="yellow")
            self.client.send_message(f"ANSWER:{self.answer_buttons[answer_key].cget('text')}")

    def receive_questions(self):
        while True:
            message = self.client.receive_message()
            print(f"Received message: {message}")
            try:
                if message.startswith("QUESTION:"):
                    self.question_label.config(text=message.split("QUESTION:")[1])
                    self.reset_answers()
                elif message.startswith("ANSWER_RESULT:"):
                    parts = message.split("ANSWER_RESULT:")[1].split(",")
                    correct_answer = parts[0].split(":")[1]
                    incorrect_answer = parts[1].split(":")[1]
                    self.highlight_answers(correct_answer, incorrect_answer)
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
                    if message.split("TIMER:")[1] == "0":
                        self.lock_answers()
                elif message.startswith("LEADERBOARD:"):
                    leaderboard_data = message.split("LEADERBOARD:")[1].split(",")
                    self.update_leaderboard(leaderboard_data)
                elif message.startswith("END_GAME:"):
                    winner_message = message.split("END_GAME:")[1]
                    messagebox.showinfo("Game Over", winner_message)
                elif message.startswith("RETURN_TO_LOBBY"):
                    time.sleep(5)
                    from .lobby import open_lobby_window
                    print("Returning to lobby...")
                    self.master.destroy()
                    self.master.quit()
                    open_lobby_window(self.client)
            except IndexError:
                print("Error processing message:", message)

    def lock_answers(self):
        self.answers_locked = True
        for btn in self.answer_buttons.values():
            btn.config(state=tk.DISABLED)

    def reset_answers(self):
        self.selected_answer = None
        self.answers_locked = False
        for btn in self.answer_buttons.values():
            btn.destroy()
        self.answer_buttons.clear()

    def highlight_answers(self, correct_answer, incorrect_answer):
        for key, btn in self.answer_buttons.items():
            if btn.cget("text") == correct_answer:
                btn.config(bg="green")
            if btn.cget("text") == incorrect_answer:
                btn.config(bg="red")

    def update_answer_button(self, key, text):
        if key not in self.answer_buttons:
            btn = tk.Button(self.answer_frame, text=f"Answer {key}", command=lambda k=key: self.select_answer(k))
            btn.pack(fill=tk.X, padx=20, pady=5)
            self.answer_buttons[key] = btn
        self.answer_buttons[key].config(text=text, bg="SystemButtonFace")

    def update_leaderboard(self, data):
        print("Updating leaderboard...")
        for widget in self.leaderboard_frame.winfo_children():
            widget.destroy()
        for entry in data:
            username, score = entry.split(":")
            label = tk.Label(self.leaderboard_frame, text=f"{username}\nScore: {score}")
            label.pack(pady=5)
            self.leaderboard_labels.append(label)

    def on_button_press(self, event):
        widget = event.widget
        for key, btn in self.answer_buttons.items():
            if widget == btn:
                self.select_answer(key)
                break

def open_game_window(client):
    print("Creating game window...")
    root = tk.Tk()
    app = GameWindow(root, client)
    root.mainloop()
