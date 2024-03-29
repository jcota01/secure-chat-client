import base64
import json
import os
import random
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

import challenge_nonce
import current_account

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

    @app.post('/challenge/<int:nonce>')
    def ip_challenge(nonce: int):
        import current_account
        if nonce != challenge_nonce.nonce:
            challenge_nonce.nonce = random.randint(0, 2 ** 64)
            abort(403)
        challenge_nonce.nonce = random.randint(0, 2 ** 64)
        challenge = int.from_bytes(decrypt_ciphertext(flask.request.get_data(), current_account.account[1]), byteorder='little')
        response = challenge - 1
        response_signature: bytes = create_signature(response.to_bytes(64 // 8, byteorder='little'), current_account.account[1])
        return response_signature

    @app.post('/recv')
    def recv_message():
        import current_account
        if chat_window is None:
            # not ready to receive messages yet
            abort(503)
        encrypted_payload = flask.request.get_data()
        decrypted_payload = crypto.decrypt_ciphertext(encrypted_payload, current_account.account[2])
        payload = json.loads(decrypted_payload.decode('utf-8'))
        message = base64.b64decode(payload['message'].encode('utf-8'))
        from_username = payload['from']
        signature = base64.b64decode(payload['signature'].encode('utf-8'))
        known_user = KnownUser.query.get(from_username)
        if not known_user:
            with grpc_channel.create_channel() as channel:
                stub = ClientServerComms_pb2_grpc.ClientServerCommsStub(channel)
                sig = ClientServerComms_pb2.DigitalSignature(
                    username=current_account.account[0],
                    signature=crypto.create_signature(from_username.encode('utf-8'), current_account.account[1])
                )
                response: ClientServerComms_pb2.FindUserResponse = stub.FindUser(
                    ClientServerComms_pb2.FindUserRequest(
                        username=from_username,
                        digitalSignature=sig
                    ))
            if response.username == from_username:
                known_user = KnownUser()
                known_user.username = response.username
                known_user.last_known_address = response.address
                known_user.chat_public_key = response.publicKeyChat
                db.session.add(known_user)
                db.session.commit()
                db.session.refresh(known_user)
        if crypto.verify_signature(message, signature, crypto.open_key_from_bytes(known_user.chat_public_key)):
            # signature matches OK
            m = Message()
            m.content = message
            m.other_user = known_user.username
            m.timestamp = datetime.now()
            m.recipient_is_me = True
            db.session.add(m)
            db.session.commit()
            db.session.refresh(m)
            chat_window.incoming_message(m)
            return 'ok'
        else:
            # signature match failed
            abort(500, "Received message with bad signature!")

    return app


def run_app(app: flask.Flask):
    if 'BIND_IP' not in os.environ:
        os.environ['BIND_IP'] = get_local_ipv4_addresses()[0]
    app.run(host=os.environ.get('BIND_IP'), port=utils.ip.RECEIVE_MESSAGES_PORT)


def main(app):
    global chat_window
    import current_account
    # try to find login details in local storage
    if os.path.isfile('account'):
        try:
            f = open('account', 'r')
            current_account.account = parse_account_file(f.read())
            f.close()
            login(current_account.account[0], current_account.account[1], challenge_nonce.nonce, preferred_ip=os.environ.get('BIND_IP'))

            # if the server does not raise an exception login was successful
        except BaseException as e:
            # there was some error with login
            current_account.account = None

    if current_account.account is None:
        login_window = LoginWindow()
        login_window.mainloop()
        login_window.quit()
        current_account.account = login_window.account

    if current_account.account is not None:
        chat_window = ChatWindow(app, current_account.account)
        with app.app_context():
            users = KnownUser.query.join(Message, KnownUser.username == Message.other_user).group_by(
                KnownUser).order_by(desc(Message.timestamp)).all()
        chat_window.update_users_list(u.username for u in users)
        chat_window.mainloop()


if __name__ == "__main__":
    challenge_nonce.nonce = random.randint(0, 2 ** 64)
    app = create_app()
    t1 = threading.Thread(target=run_app, args=(app,))
    t1.daemon = True
    t1.start()
    main(app)
    sys.exit(0)
