from flask import render_template, request, Blueprint,session,redirect,url_for
import random
from datetime import datetime
from flask_login import login_user, current_user, logout_user, login_required
from string import ascii_letters
from flask_socketio import SocketIO, join_room, leave_room, send
from app import db
from app.models import FriendRequest, User,Room,Message
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
messages = []

def generate_room_code(length: int, existing_codes: list[str]) -> str:
    while True:
        code_chars = [random.choice(ascii_letters) for _ in range(length)]
        code = ''.join(code_chars)
        if code not in existing_codes:
            return code
@main.route('/', methods=["GET", "POST"])

def home():
    if current_user.is_authenticated:
        return redirect(url_for('main.room'))
    return render_template('landing.html')

@main.route('/room')
@login_required
def room():
    

    room_code = request.args.get('room_id')
    session['room_code'] = room_code
    chats = Room.query.filter(
        or_(
            Room.member_1 == current_user.id,
            Room.member_2 == current_user.id
        )
    ).all()
    name = current_user.username
    
    # Get the current room by room_code (edit the logic as needed)
    room = ''
    receiver_name = ''
    if room_code:
        room = Room.query.filter_by(room_code=room_code).first()
        if current_user.id == room.member_1:
            receiver_name=room.user_2.username
        else: 
            receiver_name=room.user_1.username
    
    # Get messages for this room (edit as needed)
    old_messages = Message.query.filter_by(room_id=room_code).all()
    today = datetime.now()
    if room_code:
        room_exists = True
    else:
        room_exists = False    
       
    return render_template('room.html',today=today, room=room,
                            user=name,
                            receiver_name= receiver_name,
                            old_messages=old_messages, 
                            chats=chats,
                            room_exists=room_exists)
@socketio.on('connect')
@login_required
def handle_connect():
    name = current_user.username
    
    if room:
        join_room(session.get('room_code'))
    
    # if room not in rooms:
    #     leave_room(room)
   
    # send({
    #     "sender": "",
    #     "message": f"{name} has entered the chat"
    # }, to=room)

@socketio.on('message')
def handle_message(payload):
    print('hiii')
    name = current_user.username
    room_code = session.get('room_code')
    room = Room.query.filter_by(room_code=room_code).first()
    # print(room_code)
    if room:
        if current_user.id == room.member_1:
            receiver_id=room.user_2.id
            print(room.user_2.image)
        else: 
            receiver_id=room.user_1.id
            print(room.user_1.image)
        print(receiver_id)              
    # if room not in rooms:
    #     return
    
    new_message = Message(sender_id =  current_user.id, receiver_id=receiver_id,message= payload["message"],room_id= room_code)
    db.session.add(new_message)  
    print(new_message)
    # print(new_message.receiver_id) 
    db.session.commit()
    message = {
        "sender": current_user.username,
        "message": payload["message"],
        "created_at": new_message.created_at.strftime('%H:%M'),
        # "with_image":new_message.is_image,

    }
    print(message)
    messages.append(message)
    send(message, to=room_code)


@socketio.on('disconnect')
def handle_disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)
    # if room in rooms:
    #     rooms[room]["members"] -= 1
    #     if rooms[room]["members"] <= 0:
    #         del rooms[room]
    #     send({
    #     "message": f"{name} has left the chat",
    #     "sender": ""
    # }, to=room)
