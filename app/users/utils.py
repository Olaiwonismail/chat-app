
import os
import secrets
from PIL import Image
from flask import url_for, current_app
# from flask_mail import Message
# from app import mail
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
api_secret = os.getenv('cloudinary')
# Configuration       
cloudinary.config( 
    cloud_name = "dyb2ffz6x", 
    api_key = "552119589124264", 
    api_secret = api_secret,
    secure=True
)

def get_image():
# Upload an image
    upload_result = cloudinary.uploader.upload("https://res.cloudinary.com/demo/image/upload/getting-started/shoes.jpg",
                                           public_id="shoes")
# print(upload_result["secure_url"])
def save_pic(form_picture):
    random_hex = secrets.token_hex(8)
    _,f_ext = os.path.splitext(form_picture.filename)
    picture_filename = random_hex + f_ext
    upload_result = cloudinary.uploader.upload(form_picture,
                                           public_id=picture_filename)
    picture_path = os.path.join(current_app.root_path,'static/profile_pics',picture_filename)
    form_picture.save(picture_path)
    # return picture_filename
    return upload_result["secure_url"]

# def send_reset_email(user):
#
#     token=user.get_reset_token()
#     msg = Message('Password Reset Request',sender='olaiwonismail@gmail.com',
#             recipients = ['olaiwonoladayo@gmail.com'])
#     msg.body = f'''To reset your password ,visit the following link:
#         {url_for('reset_token',token=token,_external=True)}
#         If you didnt make this request simply ignore this email
#     '''
#     mail.send(msg)
