from datetime import datetime
from app import db,login_manager
from flask_login import UserMixin
from flask import url_for, current_app
# from itsdangerous import URLSafeTimedSerializer as Serializer
from sqlalchemy import Column,Text,ForeignKey,DateTime,Boolean

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



# User Model
class User(db.Model,UserMixin):
    tablename = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, unique=True, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    def repr(self):
        return f"<User(username={self.username})>"

# Message Model
class Message(db.Model):
    tablename = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)  # db.Boolean for read status
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    

    def repr(self):
        return f"<Message(sender_id={self.sender_id}, receiver_id={self.receiver_id})>"
    