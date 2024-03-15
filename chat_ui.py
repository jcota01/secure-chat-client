import tkinter as tk
from tkinter import scrolledtext

class ChatWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Secure Chat")
        self.geometry("600x500")  # Set the window size

        # Frame for connected users with a scrollbar
        self.users_frame = tk.Frame(self, bg='lightgrey', width=150)
        self.users_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        self.users_label = tk.Label(self.users_frame, text="Connected user:", bg='lightgrey')
        self.users_label.pack()

        self.users_scrollbar = tk.Scrollbar(self.users_frame, orient=tk.VERTICAL)
        self.users_listbox = tk.Listbox(self.users_frame, activestyle="dotbox", bg='lightgrey',
                                        yscrollcommand=self.users_scrollbar.set)
        self.users_scrollbar.config(command=self.users_listbox.yview)
        self.users_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.users_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Here you would have a method to update this list with users from the server
        
        # Main chat display area
        self.chat_display = scrolledtext.ScrolledText(self, state='disabled')
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
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

    def send_message(self):
        # Logic to send a message
        message = self.message_input.get()
        # Add message to chat display
        self.chat_display.configure(state='normal')
        self.chat_display.insert(tk.END, message + '\n')
        self.chat_display.configure(state='disabled')
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

if __name__ == "__main__":
    app = ChatWindow()
    # For demonstration, simulate receiving a list of users from the server
    app.update_users_list(["User1", "User2", "User3", "...", "UserN"])
    app.mainloop()
