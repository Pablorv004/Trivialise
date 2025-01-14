import tkinter as tk
from tkinter import messagebox
from connection import TriviaClient
from hashlib import sha256

class EstablishNameWindow:
    def __init__(self, master, client):
        self.master = master
        self.client = client
        self.master.title("Establish Name")

        self.label = tk.Label(master, text="Welcome! Please register or login.")
        self.label.pack(pady=20)

        self.register_button = tk.Button(master, text="Register", command=self.open_register)
        self.register_button.pack(pady=10)

        self.login_button = tk.Button(master, text="Login", command=self.open_login)
        self.login_button.pack(pady=10)

    def open_register(self):
        self.clear_window()
        self.label.config(text="Register")

        self.username_entry = tk.Entry(self.master, placeholder="Username")
        self.username_entry.pack(pady=5)

        self.password_entry = tk.Entry(self.master, show="*", placeholder="Password")
        self.password_entry.pack(pady=5)

        self.confirm_password_entry = tk.Entry(self.master, show="*", placeholder="Confirm Password")
        self.confirm_password_entry.pack(pady=5)

        self.register_submit_button = tk.Button(self.master, text="Submit", command=self.register_user)
        self.register_submit_button.pack(pady=10)

    def open_login(self):
        self.clear_window()
        self.label.config(text="Login")

        self.username_entry = tk.Entry(self.master, placeholder="Username")
        self.username_entry.pack(pady=5)

        self.password_entry = tk.Entry(self.master, show="*", placeholder="Password")
        self.password_entry.pack(pady=5)

        self.login_submit_button = tk.Button(self.master, text="Submit", command=self.login_user)
        self.login_submit_button.pack(pady=10)

    def register_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match.")
            return

        self.client.send_message(f"REGISTER:{username}:{password}")
        response = self.client.receive_message()
        if response == "REGISTER_SUCCESS":
            messagebox.showinfo("Success", "Registration successful. Please login.")
            self.open_login()
        elif response == "REGISTER_FAIL":
            messagebox.showerror("Error", "Username is already taken.")

    def login_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        self.client.send_message(f"LOGIN:{username}:{password}")
        response = self.client.receive_message()
        if response == "LOGIN_SUCCESS":
            messagebox.showinfo("Success", "Login successful.")
            self.master.destroy()
            # ...code to open the lobby window with the user data...
        elif response == "LOGIN_FAIL":
            messagebox.showerror("Error", "Invalid username or password.")

    def clear_window(self):
        for widget in self.master.winfo_children():
            widget.destroy()

def open_establish_name_window(client):
    root = tk.Tk()
    app = EstablishNameWindow(root, client)
    root.mainloop()
