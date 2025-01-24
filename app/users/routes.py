import random
from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt
from app.models import FriendRequest, User,Room
from app.models import User
from app.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,BioForm,
                                   RequestResetForm, ResetPasswordForm)
from app.users.utils import save_pic #, send_reset_emai
users= Blueprint('users',__name__)

@users.route('/signup',methods = ['POST','GET'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        dob = form.date_of_birth.data
        formatted_dob = dob.strftime('%B %d, %Y')
        user = User(username=form.username.data,email=form.email.data,password=hashed_password,dob = formatted_dob,gender=form.gender.data)

        db.session.add(user)
        db.session.commit()
        flash(f'Welcome {form.username.data}',category='success')
        login_user(user)
        return redirect(url_for('users.bio'))
        # return redirect(url_for('users.login'))
    return render_template('signup.html', title = 'Register',form = form)

@users.route("/bio", methods=["GET", "POST"])
@login_required
def bio():
    form = BioForm()
    if form.validate_on_submit():
        user_bio = form.bio.data
        current_user.bio =  user_bio
        db.session.commit()
        # flash(f"Your bio has been saved: '{user_bio}'", "success")
        return redirect(url_for('main.room'))

    return render_template("bio.html", form=form)

@users.route('/login',methods = ['POST','GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    # print('hiiii')
    if form.validate_on_submit():
        # print('nnnnnnnnnnnnn')
        user = User.query.filter_by(email = form.email.data).first()
        if user:
            if bcrypt.check_password_hash(user.password,form.password.data):
                login_user(user,remember = form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('main.room'))
            else:
                flash('Password Incorrect',category='danger')
        else:
            flash('User not found',category='danger')

    # print('dddddddddd')
    return render_template('login.html', title = 'Login',form = form)

@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('users.login'))

@users.route('/edit_profile',methods = ['POST','GET'])
@login_required
def edit_profile():
    form = UpdateAccountForm()
    if form.picture.data:
        picture_file = save_pic(form.picture.data)
        current_user.image = picture_file
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.email = form.email.data
        db.session.commit()
        flash('your account has been updated')
        return redirect(url_for('users.profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.bio.data = current_user.bio
    image_file = url_for('static',filename='profile_pics/' + current_user.image)
    return render_template('edit_profile.html',title='Account',
                                        image_file = image_file,form = form)

# def get_random_users(n=5, current_user_id=None):
#     # Ensure `current_user_id` is passed or replace with current user's ID from session
#     current_user_id = current_user_id or current_user.id
    
#     # Find users who are not the current user
#     query = User.query.filter(User.id != current_user_id)  
    
#     # Exclude users who are part of the same room as current_user (i.e., avoid member_1 and member_2 in rooms the current user is in)
#     # Assuming you have a `Room` model with `member_1` and `member_2`
#     # Create an alias for the `Room` table to check memberships
    
    
#     # Filter rooms where the current user is a member (either as member_1 or member_2)
#     query = query.filter(~User.id.in_(
#         db.session.query(Room.member_1)
#         .filter(Room.member_1 != current_user_id)
#         .union(
#             db.session.query(Room.member_2)
#             .filter(Room.member_2 != current_user_id)
#         )
#     ))
    
#     # Exclude users who already have pending friend requests from the current user
#     query = query.filter(
#         ~User.id.in_(
#             db.session.query(FriendRequest.receiver_id)
#             .filter(FriendRequest.sender_id == current_user_id, FriendRequest.status == 'pending')
#         )
#     ).filter(
#         ~User.id.in_(
#             db.session.query(FriendRequest.sender_id)
#             .filter(FriendRequest.receiver_id == current_user_id, FriendRequest.status == 'pending')
#         )
#     )
    
#     # Retrieve random users (limit to `n`, with a fallback if less than `n` users are available)
#     users = query.all()
#     random_users = random.sample(users, min(n, len(users)))
    
#     return random_users

from sqlalchemy.sql.expression import func

def get_random_users(n=5, current_user_id=None):
    current_user_id = current_user_id or current_user.id

    # Subquery: Users to exclude from rooms where the current user is a member
    rooms_subquery = db.session.query(Room.member_1).filter(Room.member_2 == current_user_id).union(
        db.session.query(Room.member_2).filter(Room.member_1 == current_user_id)
    ).subquery()

    # Subquery: Users to exclude due to pending friend requests
    pending_requests_subquery = db.session.query(FriendRequest.receiver_id).filter(
        FriendRequest.sender_id == current_user_id, FriendRequest.status == 'pending'
    ).union(
        db.session.query(FriendRequest.sender_id).filter(
            FriendRequest.receiver_id == current_user_id, FriendRequest.status == 'pending'
        )
    ).subquery()

    # Filter users and randomize selection on the database level
    query = User.query.filter(
        User.id != current_user_id,  # Exclude current user
        ~User.id.in_(rooms_subquery),  # Exclude users in the same rooms
        ~User.id.in_(pending_requests_subquery)  # Exclude users with pending requests
    ).order_by(func.random()).limit(n)  # Randomize and limit results on the database

    return query.all()


@users.route('/profile')
@login_required
def profile():
    user_id = current_user.id
    user = User.query.get_or_404(user_id)

    # Fetch pending friend requests for the current user
    pending_requests = FriendRequest.query.filter_by(receiver_id=user_id, status='pending').all()

    # Fetch random users (potential friends)
    random_users = get_random_users(5)

    # Render the profile page
    return render_template(
        'profile.html',
        user=user,
        pending_requests=pending_requests,
        friends=random_users
    )

def get_friend_status(other_user_id):
    """
    Check the friendship/request status between current_user and another user.
    Returns one of:
    - 'self': If current_user is checking their own profile.
    - 'friends': If the users are already friends.
    - 'sent_request': If current_user has sent a friend request to the other user.
    - 'received_request': If current_user has received a friend request from the other user.
    - 'no_relation': If no friend relationship or request exists.
    """
    if current_user.id == other_user_id:
        return 'self'
    
    # Check if the users are friends (an accepted friend request exists)
    is_friend = Room.query.filter(
        ((Room.member_1 == current_user.id) & (Room.member_2 == other_user_id)) |
        ((Room.member_1 == other_user_id) & (Room.member_2 == current_user.id))
    ).first()
    if is_friend:
        return 'friends'

    # Check if current_user has sent a friend request
    sent_request = FriendRequest.query.filter_by(
        sender_id=current_user.id,
        receiver_id=other_user_id,
        status='pending'
    ).first()
    if sent_request:
        return 'sent_request'

    # Check if current_user has received a friend request
    received_request = FriendRequest.query.filter_by(
        sender_id=other_user_id,
        receiver_id=current_user.id,
        status='pending'
    ).first()
    if received_request:
        return 'received_request'

    return 'no_relation'


@users.route('/my_profile/<int:id>')

def my_profile(id):
    if current_user.is_authenticated:
        info = get_friend_status(id)
    info = None
    user = User.query.get_or_404(id)
    return render_template('_profile.html', user=user,info = info)

# @users.route('/account',methods = ['POST','GET'])
# @login_required
# def account():
#     form = UpdateAccountForm()
#     if form.picture.data:
#         print(current_user.image_file)
#         picture_file = save_pic(form.picture.data)
#         current_user.image_file = picture_file
#     if form.validate_on_submit():
#         current_user.firstname = form.firstname.data
#         current_user.lastname = form.lastname.data
#         current_user.email = form.email.data
#         db.session.commit()
#         flash('your account has been updated')
#         return redirect(url_for('users.account'))
#     elif request.method == 'GET':
#         form.firstname.data = current_user.firstname
#         form.lastname.data = current_user.lastname
#         form.email.data = current_user.email
#     image_file = url_for('static',filename='profile_pics/' + current_user.image_file)
#     print(image_file)
#     return render_template('users/account.html',title='Account',
#                                         image_file = image_file,form = form)

# @users.route("/user/<username>")
# # @login_required
# def user_posts(username):
#     page = request.args.get('page',1,type = int)
#     user = User.query.filter_by(username=username).first_or_404()
#     # posts = Post.query.paginate(page=page ,per_page = 10)
#     posts = Post.query.filter_by(author=user)\
#         .order_by(Post.date_posted.desc())\
#         .paginate(page=page ,per_page = 3)

#     return render_template('user_posts.html',posts=posts,user=user)

#
#
# @users.route("/reset_request",methods=['GET', 'POST'])
# def reset_request():
#     if current_user.is_authenticated:
#         return redirect(url_for('main.home'))
#     form = RequestResetForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(email=form.email.data).first()
#         send_reset_email(user)
#
#         flash('An email has been sent to reset your password')
#         return redirect(url_for('users.login'))
#     return render_template('reset_request.html', title='Reset Password', form=form)
#
# @users.route('/reset_password/<token>',methods=['GET', 'POST'])
# def reset_token(token):
#
#     if current_user.is_authenticated:
#         return redirect(url_for('main.home'))
#     user = User.verify_reset_token(token)
#     if user is None :
#         flash('Token hsa expired','warning')
#         return redirect(url_for('users.reset_request'))
#     form = ResetPasswordForm()
#     if form.validate_on_submit():
#         hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
#         user.password=hashed_password
#         db.session.commit()
#         flash(f'Your pass word has been updated')
#         return redirect(url_for('users.login'))
#     return render_template('reset_token.html', title='Reset Password', form=form)
