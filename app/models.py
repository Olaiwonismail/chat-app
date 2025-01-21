from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
from sqlalchemy import Column, Text, ForeignKey, DateTime, Boolean

# User Loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# User Model
class User(db.Model, UserMixin):
    __tablename__ = 'users'  # Correctly specify table name
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, unique=True, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<User(username={self.username})>"
    
   

# Message Model
class Message(db.Model):
    __tablename__ = 'messages'  # Correctly specify table name
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)  # Boolean for read status
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=True)  # Add room_id to reference Room
    room = db.relationship('Room', back_populates='messages')  # Create a relationship with Room

    # Relationships to easily access the sender and receiver User objects
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')
   
    def __repr__(self):
        return f"<Message(sender_id={self.sender_id}, receiver_id={self.receiver_id})>"

class FriendRequest(db.Model):
    __tablename__ = 'friend_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # Can be 'pending', 'accepted', or 'rejected'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_requests')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_requests')

    def __repr__(self):
        return f"<FriendRequest(sender_id={self.sender_id}, receiver_id={self.receiver_id}, status={self.status})>"
    
class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_code =  db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    member_1 = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    member_2 = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user_1 = db.relationship('User', foreign_keys=[member_1], backref='rooms_as_member_1')
    user_2 = db.relationship('User', foreign_keys=[member_2], backref='rooms_as_member_2')

    messages = db.relationship('Message', back_populates='room', cascade='all, delete-orphan')  # Bidirectional relationship with Message

    def __repr__(self):
        return f"<Room(id={self.id}, room_code={self.room_code})>"
