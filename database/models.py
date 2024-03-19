import datetime

from utils.extensions import db


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_user = db.Column(db.String(64), nullable=False)
    content = db.Column(db.LargeBinary, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
