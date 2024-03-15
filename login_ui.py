import tkinter as tk
from chat_ui import ChatWindow  # Import the ChatWindow we've defined earlier

class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Secure Chat Login")
        self.geometry("300x200")

        self.username_label = tk.Label(self, text="Username")
        self.username_label.pack()
        self.username_entry = tk.Entry(self)
        self.username_entry.pack()

        self.password_label = tk.Label(self, text="Password")
        self.password_label.pack()
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack()

        self.login_button = tk.Button(self, text="Login", command=self.login)
        self.login_button.pack()

        self.register_button = tk.Button(self, text="Register", command=self.open_register_window)
        self.register_button.pack()

    def login(self):
        # This is where you would handle the actual login logic with the backend
        username = self.username_entry.get()
        password = self.password_entry.get()
        # For now, we'll just open the chat window
        self.open_chat_window()

    def open_register_window(self):
        # Open the Register Window
        register_window = RegisterWindow()
        register_window.mainloop()

    def open_chat_window(self):
        # Open the Chat Window
        self.destroy()  # Close the login window
        chat_window = ChatWindow()
        chat_window.mainloop()

class RegisterWindow(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title("Secure Chat Register")
        self.geometry("300x250")

        self.username_label = tk.Label(self, text="Username")
        self.username_label.pack()
        self.username_entry = tk.Entry(self)
        self.username_entry.pack()

        self.password_label = tk.Label(self, text="Password")
        self.password_label.pack()
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack()

        self.confirm_password_label = tk.Label(self, text="Confirm Password")
        self.confirm_password_label.pack()
        self.confirm_password_entry = tk.Entry(self, show="*")
        self.confirm_password_entry.pack()

        self.register_button = tk.Button(self, text="Register", command=self.register)
        self.register_button.pack()

        self.cancel_button = tk.Button(self, text="Cancel", command=self.destroy)
        self.cancel_button.pack()

    def register(self):
        # This is where you would handle the actual registration logic with the backend
        username = self.username_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        # For now, let's just print these values
        print("Register with:", username, password, confirm_password)
        # Ideally, after registration, you'd go to the chat window or back to the login
        # self.destroy()  # Close the register window
        # chat_window = ChatWindow()  # Open the chat window
        # chat_window.mainloop()

if __name__ == "__main__":
    login_window = LoginWindow()
    login_window.mainloop()
