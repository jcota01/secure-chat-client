import datetime

from utils.extensions import db


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_user = db.Column(db.String(64), nullable=False)
    content = db.Column(db.LargeBinary, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class KnownUser(db.Model):
    username = db.Column(db.String(64), primary_key=True, nullable=False)
    chat_public_key = db.Column(db.LargeBinary, nullable=False)
    last_known_address = db.Column(db.Integer, nullable=False)
