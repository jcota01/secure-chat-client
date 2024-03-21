import base64
import json
import os
import sys
import threading
from datetime import datetime
from typing import Tuple, Optional

import flask
from werkzeug.exceptions import abort
from sqlalchemy import desc
from Crypto.PublicKey import RSA

import ClientServerComms_pb2_grpc
import utils.ip
from database.models import KnownUser, Message
from login_ui import LoginWindow
from chat_ui import ChatWindow
from utils import crypto
from utils.account import parse_account_file
from account import *
from utils.extensions import db

account: Optional[Tuple[str, RSA.RsaKey, RSA.RsaKey]] = None
chat_window: Optional[ChatWindow] = None


def create_app():
    app = flask.Flask(__name__)
    app.config['SECRET_KEY'] = 'secret!'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    app.db = db

    with app.app_context():
        db.create_all()

    @app.post('/recv')
    def recv_message():
        if chat_window is None:
            # not ready to receive messages yet
            abort(503)
        encrypted_payload = flask.request.get_data()
        decrypted_payload = crypto.decrypt_ciphertext(encrypted_payload, account[2])
        payload = json.loads(decrypted_payload.decode('utf-8'))
        message = base64.b64decode(payload['message'].encode('utf-8'))
        from_username = base64.b64decode(payload['from'].encode('utf-8'))
        signature = base64.b64decode(payload['signature'].encode('utf-8'))
        known_user = KnownUser.query.get(from_username)
        if not known_user:
            with grpc_channel.create_channel() as channel:
                stub = ClientServerComms_pb2_grpc.ClientServerCommsStub(channel)
                response: ClientServerComms_pb2.FindUserResponse = stub.FindUser(
                    ClientServerComms_pb2.FindUserRequest(
                        username=from_username.decode('utf-8'),
                        digitalSignature=crypto.create_signature(from_username, account[1])
                    ))
            if response.username == from_username:
                known_user = KnownUser()
                known_user.username = response.username
                known_user.last_known_address = response.address
                known_user.chat_id = response.publicKeyChat
                db.session.add(known_user)
                db.session.commit()
                db.session.refresh(known_user)
        if crypto.verify_signature(message, signature, crypto.open_key_from_bytes(known_user.chat_public_key)):
            # signature matches OK
            m = Message()
            m.content = message
            m.other_user = known_user
            m.timestamp = datetime.now()
            m.recipient_is_me = True
            db.session.add(m)
            db.session.commit()
            db.session.refresh(m)
            chat_window.incoming_message(m)
            pass
        else:
            # signature match failed
            print("Received message with bad signature!")

    return app


def run_app(app: flask.Flask):
    app.run(host=get_local_ipv4_addresses()[0], port=utils.ip.RECEIVE_MESSAGES_PORT)


def main(app):
    global account
    global chat_window
    # try to find login details in local storage
    if os.path.isfile('account'):
        try:
            f = open('account', 'r')
            account = parse_account_file(f.read())
            f.close()
            login(account[0], account[1])

            # if the server does not raise an exception login was successful
        except BaseException as e:
            # there was some error with login
            account = None

    if account is None:
        login_window = LoginWindow()
        login_window.mainloop()
        login_window.quit()
        account = login_window.account

    if account is not None:
        chat_window = ChatWindow(app, account)
        with app.app_context():
            users = KnownUser.query.join(Message, KnownUser.username == Message.other_user).group_by(
                KnownUser).order_by(desc(Message.timestamp)).all()
        chat_window.update_users_list(u.username for u in users)
        chat_window.mainloop()


if __name__ == "__main__":
    app = create_app()
    t1 = threading.Thread(target=run_app, args=(app,))
    t1.daemon = True
    t1.start()
    main(app)
    sys.exit(0)
