import datetime

from utils.extensions import db


class KnownUser(db.Model):
    __tablename__ = 'knownuser'
    username = db.Column(db.String(64), primary_key=True, nullable=False)
    chat_public_key = db.Column(db.LargeBinary, nullable=False)
    last_known_address = db.Column(db.Integer, nullable=False)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    other_user = db.Column(db.String(64), db.ForeignKey('knownuser.username'), nullable=False)
    recipient_is_me = db.Column(db.Boolean, nullable=False)
    content = db.Column(db.LargeBinary, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
