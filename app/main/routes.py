from flask import render_template, request, Blueprint,session,redirect,url_for
import random
from flask_login import login_user, current_user, logout_user, login_required
from string import ascii_letters
from flask_socketio import SocketIO, join_room, leave_room, send
from app import db
from app.models import FriendRequest, User,Room
from app import socketio,db
from sqlalchemy.orm import aliased
from sqlalchemy import or_
# from flask_login import login_required
main = Blueprint('main',__name__)

# rooms = Room.query.filter(
#     or_(
#         Room.member_1 == current_user.id,
#         Room.member_2 == current_user.id
#     )
#     ).all()
rooms = {}

def generate_room_code(length: int, existing_codes: list[str]) -> str:
    while True:
        code_chars = [random.choice(ascii_letters) for _ in range(length)]
        code = ''.join(code_chars)
        if code not in existing_codes:
            return code
@main.route('/', methods=["GET", "POST"])
@login_required
def home():
    return redirect(url_for('main.room'))

@main.route('/room')
@login_required

def room():
    chats = Room.query.filter(
    or_(
        Room.member_1 == current_user.id,
        Room.member_2 == current_user.id
    )
    ).all()
    name = current_user.username
    messages=''
  
    print(chats)
    return render_template('room.html', room=room, user=name, messages=messages,chats = chats)

@socketio.on('connect')
@login_required
def handle_connect():
    name = current_user.username
    room = session.get('room')
    if name is None or room is None:
        return
    if room not in rooms:
        leave_room(room)
    join_room(room)
    send({
        "sender": "",
        "message": f"{name} has entered the chat"
    }, to=room)

@socketio.on('message')
def handle_message(payload):
    room = session.get('room')
    name = session.get('name')
    if room not in rooms:
        return
    message = {
        "sender": name,
        "message": payload["message"]
    }
    send(message, to=room)
    rooms[room]["messages"].append(message)
    
@socketio.on('disconnect')
def handle_disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)
    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]
        send({
        "message": f"{name} has left the chat",
        "sender": ""
    }, to=room)
