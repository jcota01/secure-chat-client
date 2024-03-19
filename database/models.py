import datetime

from utils.extensions import db

class Message(db.Model):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.Integer, nullable=False)
    to_user_id = db.Column(db.Integer, nullable=False)
    text = db.Column(db.String(500), nullable=False)
    # nonce = db.Column(db.LargeBinary)
    # auth_tag = db.Column(db.LargeBinary)
    # encrypted_pub_key = db.Column(db.LargeBinary)
    nonce = db.Column(db.Text)
    auth_tag = db.Column(db.Text)
    encrypted_pub_key = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)