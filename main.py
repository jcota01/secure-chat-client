import os
import sys
import threading
from typing import Tuple, Optional

import flask
from sqlalchemy import desc
from Crypto.PublicKey import RSA

import ClientServerComms_pb2_grpc
from database.models import KnownUser, Message
from login_ui import LoginWindow
from chat_ui import ChatWindow
from utils.account import parse_account_file
from account import *
from utils.extensions import db


def create_app():
    app = flask.Flask(__name__)
    app.config['SECRET_KEY'] = 'secret!'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    app.db = db

    with app.app_context():
        db.create_all()

    return app


def run_app(app: flask.Flask):
    app.run(host='0.0.0.0', port=6500)


def main(app):
    account: Optional[Tuple[str, RSA.RsaKey, RSA.RsaKey]] = None

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
        chat_window = ChatWindow(app)
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
