import base64
import json
import tkinter as tk
from datetime import datetime
from tkinter import simpledialog, messagebox
from typing import Optional, Tuple

import flask
import requests
from sqlalchemy import asc
from Crypto.PublicKey import RSA

import ClientServerComms_pb2
import ClientServerComms_pb2_grpc
import grpc_channel
import utils.ip
from database.models import Message, KnownUser
from utils import crypto
from utils.crypto import create_signature


class ChatWindow(tk.Tk):
    def __on_user_select(self, event):
        w = event.widget
        c = w.curselection()
        if len(c) < 1:
            return
        index = int(c[0])
        value = w.get(index)
        self.switch_to_user(value)

    @staticmethod
    def __format_message(message: Message):
        return f"[{message.timestamp.strftime('%H:%M:%S')}][{message.other_user if message.recipient_is_me else 'You'}] {message.content.decode('utf-8')}"

    def switch_to_user(self, user: str):
        if self.selected_user == user:
            return

        self.chat_display.configure(state=tk.NORMAL)
        self.chat_display.delete(0, tk.END)
        self.message_input.delete(0, tk.END)
        self.message_input.insert(0, "Write your message here ....")
        self.selected_user = user

        # get past messages
        with self.app.app_context():
            messages = Message.query.filter_by(other_user=self.selected_user).order_by(asc(Message.timestamp)).limit(100).all()

        for message in messages:
            self.chat_display.insert(tk.END, ChatWindow.__format_message(message))

    def __init__(self, app: flask.Flask, account: Tuple[str, RSA.RsaKey, RSA.RsaKey]):
        super().__init__()
        self.title("Secure Chat")
        self.geometry("600x500")  # Set the window size
        self.account = account

        # Frame for connected users with a scrollbar
        self.users_frame = tk.Frame(self, bg='lightgrey', width=150)
        self.users_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        self.find_button = tk.Button(self.users_frame, text="+ New Conversation", bg='blue', fg='white', command=self.find_user)
        self.find_button.pack(fill=tk.BOTH)

        self.users_scrollbar = tk.Scrollbar(self.users_frame, orient=tk.VERTICAL)
        self.users_listbox = tk.Listbox(self.users_frame, activestyle="dotbox", bg='lightgrey',
                                        yscrollcommand=self.users_scrollbar.set)
        self.users_listbox.bind('<<ListboxSelect>>', self.__on_user_select)
        self.users_scrollbar.config(command=self.users_listbox.yview)
        self.users_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.users_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Here you would have a method to update this list with users from the server
        
        # Main chat display area
        self.chat_frame = tk.Frame(self)
        self.chat_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.chat_scrollbar = tk.Scrollbar(self.chat_frame, orient=tk.VERTICAL)
        self.chat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_display = tk.Listbox(self.chat_frame, state='disabled', yscrollcommand=self.chat_scrollbar.set)
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        self.chat_scrollbar.config(command=self.chat_display.yview)

        # Message input area
        self.message_frame = tk.Frame(self)
        self.message_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)
        
        self.message_input = tk.Entry(self.message_frame)
        self.message_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.message_input.insert(0, "Write your message here ....")
        self.message_input.bind("<FocusIn>", self.on_focus_in)
        self.message_input.bind("<FocusOut>", self.on_focus_out)
        self.placeholder_text = "Write your message here ...."
        
        # Send button
        self.send_button = tk.Button(self.message_frame, text="Send", bg='green', fg='white', command=self.send_message)
        self.send_button.pack(side=tk.RIGHT)
        
        self.protocol("WM_DELETE_WINDOW", self.on_close)  # Handle window closing
        self.app = app
        self.selected_user: Optional[str] = None

    def send_message(self):
        # add message to local db
        with self.app.app_context():
            message = Message()
            message.content = self.message_input.get().encode('utf-8')
            message.timestamp = datetime.now()
            message.recipient_is_me = False
            message.other_user = self.selected_user
            self.app.db.session.add(message)
            self.app.db.session.commit()
            self.app.db.session.refresh(message)
            user = KnownUser.query.get(self.selected_user)
        # send message to other user
        their_ip = utils.ip.fixed32_to_ipv4(user.last_known_address)

        # do crypto on the message
        signature = crypto.create_signature(message.content, self.account[2])
        payload = json.dumps({
            'message': base64.b64encode(message.content).decode('utf-8'),
            'from': self.account[0],
            'signature': base64.b64encode(signature).decode('utf-8')
        }).encode('utf-8')
        encrypted_payload = crypto.encrypt_plaintext(payload, crypto.open_key_from_bytes(user.chat_public_key))
        r = requests.post(f"http://{their_ip}:{utils.ip.RECEIVE_MESSAGES_PORT}/recv", data=encrypted_payload)
        if not r.ok:
            print("Error sending message")
        else:
            # Add message to chat display
            self.chat_display.insert(tk.END, ChatWindow.__format_message(message))
            # Clear input field
            self.message_input.delete(0, tk.END)

    def on_focus_in(self, event):
        if self.message_input.get() == self.placeholder_text:
            self.message_input.delete(0, tk.END)
            self.message_input.config(fg='black')
    
    def on_focus_out(self, event):
        if not self.message_input.get():
            self.message_input.insert(0, self.placeholder_text)
            self.message_input.config(fg='grey')

    def update_users_list(self, user_list):
        # Clear the current list of users
        self.users_listbox.delete(0, tk.END)
        # Insert the new list of users
        for user in user_list:
            self.users_listbox.insert(tk.END, user)

    def on_close(self):
        # Handle any cleanup here
        self.destroy()

    def incoming_message(self, message: Message):
        self.switch_to_user(message.other_user)

    def find_user(self):
        username = simpledialog.askstring("Enter Username", "Please enter the username of the person you want to talk "
                                                            "to", parent=self)
        with grpc_channel.create_channel() as channel:
            stub = ClientServerComms_pb2_grpc.ClientServerCommsStub(channel)
            digital_signature = create_signature(username.encode('utf-8'), self.account[1])
            sig = ClientServerComms_pb2.DigitalSignature(
                username=self.account[0],
                signature=digital_signature
            )
            try:
                response: ClientServerComms_pb2.FindUserResponse = stub.FindUser(ClientServerComms_pb2.FindUserRequest(
                    username=username,
                    digitalSignature=sig
                ))
            except BaseException as e:
                messagebox.showerror("Error", "Error finding the user. Do they exist?")
                return
        known_user = KnownUser()
        known_user.username = response.username
        known_user.chat_public_key = response.publicKeyChat
        known_user.last_known_address = response.address
        with self.app.app_context():
            self.app.db.session.add(known_user)
            self.app.db.session.commit()
            self.app.db.session.refresh(known_user)
        self.users_listbox.insert(0, response.username)
        self.switch_to_user(response.username)

if __name__ == "__main__":
    app = ChatWindow()
    # For demonstration, simulate receiving a list of users from the server
    app.update_users_list(["User1", "User2", "User3", "...", "UserN"])
    app.mainloop()
