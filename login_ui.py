import os
import tkinter as tk
from tkinter import filedialog

from typing import Tuple, Optional

from Crypto.PublicKey import RSA

import challenge_nonce
from account import *
from utils.account import parse_account_file, export_account_file


class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Secure Chat Login")
        self.geometry("300x200")
        self.account: Optional[Tuple[str, RSA.RsaKey, RSA.RsaKey]] = None

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
            login(self.account[0], self.account[1], challenge_nonce.nonce, preferred_ip=os.environ.get('BIND_IP'))
            # if the server does not raise an exception login was successful
            # exit login window thread
            self.quit()
        except BaseException as e:
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

        self.register_button = tk.Button(self, text="Register", command=self.do_register)
        self.register_button.pack()

        self.cancel_button = tk.Button(self, text="Cancel", command=self.destroy)
        self.cancel_button.pack()

    def do_register(self):
        username = self.username_entry.get()

        print("Register with username:", username)
        try:
            self.account = register(username)
            # assume registration success if no exception
            print("Registered successfully")
            # save the account file to the default place
            f = open('account', 'w')
            f.write(export_account_file(*self.account))
            import main
            main.account = self.account
            login(self.account[0], self.account[1], challenge_nonce.nonce, preferred_ip=os.environ.get('BIND_IP'))
        except BaseException as e:
            # there was some error in registration
            print("Failed to register, perhaps try a different username")

        self.quit()


if __name__ == "__main__":
    login_window = LoginWindow()
    login_window.mainloop()
