# Secure Chat Application - Interface Integration Points

![alt text](https://github.com/abdullahomran9/SecureChat/blob/main/image.png)
![alt text](https://github.com/abdullahomran9/SecureChat/blob/main/image2.png)

## How to Run

1. Create a virtualenv and install the packages from `requirements.txt`. Activate the virtualenv.
2. *(Optional)* Export the enivronment variable BIND_IP with the IP address you want your client to have. This can be the IP address of any NIC, or any 127.x.y.z local loopback address. A sensible default will be chosen if not specified, but as each chat client **MUST** have a unique bind IP to operate correctly, this is useful for testing locally.
3. Run ./main.py using your virtualenv.
```bash
python3 -m venv .venv
export BIND_IP=127.0.0.100
python3 ./main.py
```
The client is hard-coded to use a server on `127.0.0.1` (localhost IPv4) for development reasons. If you want to use a different server address, you will need to update the code in `grpc_channel.py` and re-generate your TLS certificates for the new IP address or DNS name.

## Overview

The Secure Chat Application provides encrypted communication between users. The user interface is implemented in Tkinter, with placeholders for backend integration. Below is an overview of each Python file and the key points where backend services should be connected.

## Python Files Summary

- `chat_ui.py`: Contains the `ChatWindow` class responsible for the chat interface, displaying messages, and listing users.
- `login_ui.py`: Contains both the `LoginWindow` and `RegisterWindow` classes. `LoginWindow` manages user authentication, and `RegisterWindow` handles new user registrations.
- `main.py`: The entry point of the application. Initializes and displays the `LoginWindow`.

## Integration Points

### `chat_ui.py`

- **Users List Update**: The `update_users_list` method in `ChatWindow` should be called with a list of usernames to refresh the sidebar showing active users.
- **Message Reception**: Implement a method to append new messages to the `chat_display` text area. Ensure message formatting and proper scrolling behavior.
- **Message Sending**: The `send_message` method is triggered by the send button. Replace its content with a function that sends the typed message to the backend.

### `login_ui.py`

- **User Login**: The `login` method in `LoginWindow` should authenticate the user against the backend. On success, transition to `ChatWindow`.
- **User Registration**: The `register` method in `RegisterWindow` should send registration details to the backend. Upon successful registration, it may log in the user directly or redirect to the `LoginWindow`.

### `main.py`

- **Application Initialization**: `main.py` runs the login window and should eventually manage session persistence, if required, or handle command-line arguments for different startup modes.

## Instructions for Backend Developers

Backend integration is essential to bring the Secure Chat Application to full functionality. Focus on the following tasks:

1. **User Authentication**: Connect the `login` method in `LoginWindow` with your authentication API.
2. **Registration Handling**: Connect the `register` method in `RegisterWindow` with your user registration API.
3. **Message Routing**: Create functions that handle the sending and receiving of messages through your backend, connecting them to `send_message` in `ChatWindow`.
4. **Active User Fetching**: Periodically fetch the list of active users and populate the list in `ChatWindow` using `update_users_list`.

Implement callbacks or event listeners as necessary for receiving messages and updating the user list in real time. Use threading or asynchronous calls to keep the UI responsive.

### Security Note

Ensure all communications between the client and server are encrypted and follow best practices for user data handling and password management. 

### Testing and Documentation

Test each integration point thoroughly. Document your methods and their expected inputs and outputs, so that team members can understand and maintain the codebase effectively.

## Final Remarks

Each file is designed to be modular to facilitate collaboration. Review the placeholders in the UI files and integrate them with the backend logic you develop. Clear and consistent communication is crucial as you work on bringing the Secure Chat Application to life.
