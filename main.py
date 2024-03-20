import base64
import json
import os
import sys
import threading
from typing import Tuple, Optional

import flask
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
        encrypted_payload = flask.request.get_data()
        decrypted_payload = crypto.decrypt_ciphertext(encrypted_payload, account[2])
        payload = json.loads(decrypted_payload.decode('utf-8'))
        message = base64.b64decode(payload['message'].encode('utf-8'))
        from_username = base64.b64decode(payload['from'].encode('utf-8'))
        signature = base64.b64decode(payload['signature'].encode('utf-8'))
        known_user = KnownUser.query.get(from_username)
        if not known_user:
            # TODO: get pubkey from server and store in DB
            raise NotImplemented
        if crypto.verify_signature(message, signature, crypto.open_key_from_bytes(known_user.chat_public_key)):
            # signature matches OK
            # TODO: pass message to the UI
            pass
        else:
            # signature match failed
            # TODO: raise error?
            pass

    pass

    return app


def run_app(app: flask.Flask):
    app.run(host=get_local_ipv4_addresses()[0], port=utils.ip.RECEIVE_MESSAGES_PORT)


def main(app):
    # try to find login details in local storage
    if os.path.isfile('account'):
        try:
            f = open('account', 'r')
            account = parse_account_file(f.read())
            f.close()
            login(account[0], account[1])

            # if the server does not raise an exception login was successful
        except BaseException:
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
            users = KnownUser.query.join(Message, KnownUser.username == Message.other_user).group_by(KnownUser).order_by(desc(Message.timestamp)).all()
        chat_window.update_users_list(u.username for u in users)
        chat_window.mainloop()


if __name__ == "__main__":
    app = create_app()
    t1 = threading.Thread(target=run_app, args=(app,))
    t1.daemon = True
    t1.start()
    main(app)
    sys.exit(0)
