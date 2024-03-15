import tkinter as tk
from tkinter import filedialog

from typing import Tuple, Optional

from Crypto.PublicKey import RSA

import stubs
from stubs import parse_account_file, login, register


class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Secure Chat Login")
        self.geometry("300x200")
        self.account: Optional[Tuple[str, RSA.RsaKey]] = None

        self.file_picker = tk.Button(self, text="Login with Account File", command=self.pick_file)
        self.file_picker.pack()

        self.register_button = tk.Button(self, text="Register", command=self.open_register_window)
        self.register_button.pack()

    def pick_file(self):
        # Open a file picker dialog to choose the account file
        filename = filedialog.askopenfilename()

        try:
            f = open('account', 'r')
            self.account = parse_account_file(f.read())
            f.close()
            login(*self.account)
            # if the server does not raise an exception login was successful
            # exit login window thread
            self.quit()
        except BaseException:
            # there was some error with login
            print("Login error")

    def open_register_window(self):
        # Open the Register Window
        register_window = RegisterWindow()
        register_window.mainloop()
        if register_window.account is not None:
            # they registered ok
            self.account = register_window.account
            self.quit()


class RegisterWindow(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title("Secure Chat Register")
        self.geometry("300x200")
        self.account: Optional[Tuple[str, RSA.RsaKey]] = None

        self.username_label = tk.Label(self, text="Username")
        self.username_label.pack()
        self.username_entry = tk.Entry(self)
        self.username_entry.pack()

        self.register_button = tk.Button(self, text="Register", command=self.register)
        self.register_button.pack()

        self.cancel_button = tk.Button(self, text="Cancel", command=self.destroy)
        self.cancel_button.pack()

    def register(self):
        username = self.username_entry.get()

        print("Register with username:", username)
        try:
            self.account = register(username)
            # assume registration success if no exception
            print("Registered successfully")
            # save the account file to the default place
            f = open('account', 'w')
            f.write(stubs.export_account_file(*self.account))
        except BaseException:
            # there was some error in registration
            print("Failed to register, perhaps try a different username")

        self.quit()


if __name__ == "__main__":
    login_window = LoginWindow()
    login_window.mainloop()
