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

    def open_register(self):
        self.clear_window()
        RegisterWindow(self.master, self.client, self)

    def open_login(self):
        self.clear_window()
        LoginWindow(self.master, self.client, self)

    def clear_window(self):
        for widget in self.master.winfo_children():
            widget.destroy()

class RegisterWindow:
    def __init__(self, master, client, parent):
        self.master = master
        self.client = client
        self.parent = parent
        self.master.title("Register")
        self.master.geometry("300x250")

        self.label = tk.Label(master, text="Register")
        self.label.pack(pady=20)

        self.username_entry = tk.Entry(self.master, fg='grey')
        self.username_entry.pack(pady=5)
        self.add_placeholder(self.username_entry, "Email")

        self.password_entry = tk.Entry(self.master, show="*", fg='grey')
        self.password_entry.pack(pady=5)
        self.add_placeholder(self.password_entry, "Password")

        self.confirm_password_entry = tk.Entry(self.master, show="*", fg='grey')
        self.confirm_password_entry.pack(pady=5)
        self.add_placeholder(self.confirm_password_entry, "Confirm Password")

        self.register_submit_button = tk.Button(self.master, text="Submit", command=self.register_user)
        self.register_submit_button.pack(pady=10)

        self.return_button = tk.Button(self.master, text="Return", command=self.return_to_main)
        self.return_button.pack(pady=10)

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

    def register_user(self):
        email = self.username_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match.")
            return

        if not self.validate_email(email):
            messagebox.showerror("Error", "Invalid email format.")
            return

        hashed_password = sha256(password.encode()).hexdigest()
        self.client.send_message(f"REGISTER:{email}:{hashed_password}")
        response = self.client.receive_message()
        if response == "REGISTER_SUCCESS":
            messagebox.showinfo("Success", "Registration successful. Please login.")
            self.return_to_main()
        elif response == "REGISTER_FAIL":
            messagebox.showerror("Error", "Email is already taken.")

    def validate_email(self, email):
        import re
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(pattern, email) is not None

    def return_to_main(self):
        self.parent.clear_window()
        EstablishNameWindow(self.master, self.client)

class LoginWindow:
    def __init__(self, master, client, parent):
        self.master = master
        self.client = client
        self.parent = parent
        self.master.title("Login")
        self.master.geometry("300x230")

        self.label = tk.Label(master, text="Login")
        self.label.pack(pady=20)

        self.username_entry = tk.Entry(self.master, fg='grey')
        self.username_entry.pack(pady=5)
        self.add_placeholder(self.username_entry, "Email")

        self.password_entry = tk.Entry(self.master, show="*", fg='grey')
        self.password_entry.pack(pady=5)
        self.add_placeholder(self.password_entry, "Password")

        self.login_submit_button = tk.Button(self.master, text="Submit", command=self.login_user)
        self.login_submit_button.pack(pady=10)

        self.return_button = tk.Button(self.master, text="Return", command=self.return_to_main)
        self.return_button.pack(pady=10)

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

    def login_user(self):
        email = self.username_entry.get()
        password = self.password_entry.get()

        hashed_password = sha256(password.encode()).hexdigest()
        self.client.send_message(f"LOGIN:{email}:{hashed_password}")
        response = self.client.receive_message()
        print("Response:", response)
        if response == "LOGIN_SUCCESS":
            self.client.email = email
            self.master.destroy()
            open_lobby_window(self.client)
        elif response == "LOGIN_NN_SUCCESS":
            self.client.email = email
            self.master.destroy()
            open_nick_selector_window(self.client)
        elif response == "LOGIN_FAIL":
            messagebox.showerror("Error", "Invalid email or password.")

    def return_to_main(self):
        self.parent.clear_window()
        EstablishNameWindow(self.master, self.client)

class NickSelectorWindow:
    def __init__(self, master, client):
        self.master = master
        self.client = client
        self.master.title("Nick Selector")
        self.master.geometry("300x200")

        self.label = tk.Label(master, text="Select your Nickname")
        self.label.pack(pady=20)

        self.nickname_entry = tk.Entry(master)
        self.nickname_entry.pack(pady=10)

        self.submit_button = tk.Button(master, text="Submit", command=self.submit_nickname)
        self.submit_button.pack(pady=10)

    def submit_nickname(self):
        nickname = self.nickname_entry.get()
        self.client.send_message(f"NICK:{nickname}")
        response = self.client.receive_message()
        print("Response:", response)
        if response != "NICK_SUCCESS":
            response = self.client.receive_message()
        if response == "NICK_SUCCESS":
            self.client.username = nickname
            self.master.destroy()
            open_lobby_window(self.client)
        else:
            messagebox.showerror("Error", "Failed to set nickname.")

def open_nick_selector_window(client):
    root = tk.Tk()
    app = NickSelectorWindow(root, client)
    root.mainloop()

def open_establish_name_window(client):
    root = tk.Tk()
    app = EstablishNameWindow(root, client)
    root.mainloop()
