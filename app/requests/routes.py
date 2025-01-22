from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
import uuid
from app import db

from app.models import FriendRequest, User,Room
from flask import render_template, request, Blueprint,session,redirect,url_for


requests = Blueprint('requests',__name__)
@requests.route('/send_friend_request/<int:receiver_id>', methods=['POST','GET'])

@login_required
def send_friend_request(receiver_id):
    receiver = User.query.get_or_404(receiver_id)
    
    if receiver.id == current_user.id:
        flash("You cannot send a friend request to yourself.", category='danger')
        return redirect(url_for('users.profile', user_id=current_user.id))
    
    # Check if there's already a pending request
    existing_request = FriendRequest.query.filter(
        (FriendRequest.sender_id == current_user.id) & (FriendRequest.receiver_id == receiver.id) |
        (FriendRequest.sender_id == receiver.id) & (FriendRequest.receiver_id == current_user.id)
    ).first()
    
    if existing_request:
        flash("A friend request is already pending or has been responded to.", category='danger')
        return redirect(url_for('users.profile', user_id=current_user.id))
    
    # Create the friend request
    new_request = FriendRequest(sender_id=current_user.id, receiver_id=receiver.id)
    db.session.add(new_request)
    db.session.commit()

    flash(f"Friend request sent to {receiver.username}!", category='success')
    return redirect(url_for('users.profile', user_id=receiver.id))

@requests.route('/accept_friend_request/<int:request_id>', methods=['POST','GET'])

@login_required
def accept_friend_request(request_id):
    friend_request = FriendRequest.query.get_or_404(request_id)

    # Ensure that the current user is the receiver of the request
    if friend_request.receiver_id != current_user.id:
        flash("You cannot accept this request.", category='danger')
        return redirect(url_for('users.profile', user_id=current_user.id))

    # Update the status to 'accepted'
    friend_request.status = 'accepted'
    room_code=(str(uuid.uuid4()))
    new_room = Room(room_code = room_code,member_1 = friend_request.receiver_id,member_2 = friend_request.sender_id)
    db.session.add(new_room)
    db.session.commit()

    flash("Friend request accepted!", category='success')
    return redirect(url_for('users.profile', user_id=current_user.id))

@requests.route('/reject_friend_request/<int:request_id>', methods=['POST','GET'])
@login_required
def reject_friend_request(request_id):
    friend_request = FriendRequest.query.get_or_404(request_id)

    # Ensure that the current user is the receiver of the request
    if friend_request.receiver_id != current_user.id:
        flash("You cannot reject this request.", category='danger')
        return redirect(url_for('users.profile', user_id=current_user.id))

    # Update the status to 'rejected'
    friend_request.status = 'rejected'
    db.session.delete(friend_request)
    db.session.commit()

    flash("Friend request rejected.", category='danger')
    return redirect(url_for('users.profile', user_id=current_user.id))


