import tkinter as tk
from tkinter import messagebox
from hashlib import sha256
from GUI.lobby import open_lobby_window

class EstablishNameWindow:
    def __init__(self, master, client):
        self.master = master
        self.client = client
        self.master.title("Establish Name")
        self.master.geometry("300x200")

        self.label = tk.Label(master, text="Welcome! Please register or login.")
        self.label.pack(pady=20)

        self.register_button = tk.Button(master, text="Register", command=self.open_register)
        self.register_button.pack(pady=10)

        self.login_button = tk.Button(master, text="Login", command=self.open_login)
        self.login_button.pack(pady=10)

    def add_placeholder(self, entry, placeholder):
        entry.insert(0, placeholder)
        entry.bind("<FocusIn>", lambda event: self.clear_placeholder(event, placeholder))
        entry.bind("<FocusOut>", lambda event: self.set_placeholder(event, placeholder))

    def clear_placeholder(self, event, placeholder):
        if event.widget.get() == placeholder:
            event.widget.delete(0, tk.END)
            event.widget.config(fg='black')

    def set_placeholder(self, event, placeholder):
        if not event.widget.get():
            event.widget.insert(0, placeholder)
            event.widget.config(fg='grey')

    def open_register(self):
        self.clear_window()
        self.label = tk.Label(self.master, text="Register")
        self.label.pack(pady=20)

        self.username_entry = tk.Entry(self.master, fg='grey')
        self.username_entry.pack(pady=5)
        self.add_placeholder(self.username_entry, "Username")

        self.password_entry = tk.Entry(self.master, show="*", fg='grey')
        self.password_entry.pack(pady=5)
        self.add_placeholder(self.password_entry, "Password")

        self.confirm_password_entry = tk.Entry(self.master, show="*", fg='grey')
        self.confirm_password_entry.pack(pady=5)
        self.add_placeholder(self.confirm_password_entry, "Confirm Password")

        self.register_submit_button = tk.Button(self.master, text="Submit", command=self.register_user)
        self.register_submit_button.pack(pady=10)

    def open_login(self):
        self.clear_window()
        self.label = tk.Label(self.master, text="Login")
        self.label.pack(pady=20)

        self.username_entry = tk.Entry(self.master, fg='grey')
        self.username_entry.pack(pady=5)
        self.add_placeholder(self.username_entry, "Username")

        self.password_entry = tk.Entry(self.master, show="*", fg='grey')
        self.password_entry.pack(pady=5)
        self.add_placeholder(self.password_entry, "Password")

        self.login_submit_button = tk.Button(self.master, text="Submit", command=self.login_user)
        self.login_submit_button.pack(pady=10)

    def register_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match.")
            return

        hashed_password = sha256(password.encode()).hexdigest()
        self.client.send_message(f"REGISTER:{username}:{hashed_password}")
        response = self.client.receive_message()
        if response == "REGISTER_SUCCESS":
            messagebox.showinfo("Success", "Registration successful. Please login.")
            self.open_login()
        elif response == "REGISTER_FAIL":
            messagebox.showerror("Error", "Username is already taken.")

    def login_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        hashed_password = sha256(password.encode()).hexdigest()
        self.client.send_message(f"LOGIN:{username}:{hashed_password}")
        response = self.client.receive_message()
        if response == "LOGIN_SUCCESS":
            self.client.username = username
            self.master.destroy()
            open_lobby_window(self.client)
        elif response == "LOGIN_FAIL":
            messagebox.showerror("Error", "Invalid username or password.")

    def clear_window(self):
        for widget in self.master.winfo_children():
            widget.destroy()

def open_establish_name_window(client):
    root = tk.Tk()
    app = EstablishNameWindow(root, client)
    root.mainloop()
