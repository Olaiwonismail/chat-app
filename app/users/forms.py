from flask_wtf import csrf,FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField,TextAreaField, PasswordField, SubmitField, BooleanField,EmailField,DateField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from app.models import User



class RegistrationForm(FlaskForm):
    username = StringField('Username',
                                validators = [DataRequired(),Length(min=2,max =20)])
    
    email = EmailField('Email',
                                validators = [DataRequired()])
    password = PasswordField('Password' ,validators = [DataRequired()] )
    confirm_password = PasswordField('Confirm Password',validators = [DataRequired(),EqualTo('password')] )
    date_of_birth = DateField(
        "Enter your date of birth",
        format="%Y-%m-%d",  # Accepts YYYY-MM-DD
        validators=[DataRequired(message="Please enter your date of birth.")]
    )
    gender = SelectField(
        "Select Your Gender",
        choices=[
            ("male", "Male"),
            ("female", "Female"),
            ("other", "Other"),
        ],
        validators=[DataRequired(message="Please select your gender.")],
    )
    submit = SubmitField('Sign Up')

    def validate_username(self,username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('This user name has been taken Please choose another')

    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email has been taken Please choose another')

class BioForm(FlaskForm):
    bio = TextAreaField(
        "Enter Your Bio",
        validators=[
            DataRequired(message="Please write something about yourself."),
            Length(max=200, message="Your bio must not exceed 200 characters.")
        ],
        render_kw={"rows": 5}  # Sets the height of the text area
    )
    submit = SubmitField("Submit")

class LoginForm(FlaskForm):

    email = EmailField('Email',
                                validators = [DataRequired()])
    password = PasswordField('Password' ,validators = [DataRequired()] )

    remember = BooleanField('Keep me logged in',default ='checked')
    submit = SubmitField('Login')




# class UpdateAccountForm(FlaskForm):
#     firstname = StringField('First Name',
#                                 validators = [DataRequired(),Length(min=2,max =20)])
#     lastname = StringField('Last Name',
#                                 validators = [DataRequired(),Length(min=2,max =20)])
#     email = EmailField('Email',
#                                 validators = [DataRequired()])
#     picture = FileField('Update Profile Picture',validators = [FileAllowed(['jpg','png'])])
#     bio = TextAreaField(
#         "Enter Your Bio",
#         validators=[
#             DataRequired(message="Please write something about yourself."),
#             Length(max=200, message="Your bio must not exceed 200 characters.")
#         ],
#         render_kw={"rows": 5}  # Sets the height of the text area
#     )
#     submit = SubmitField('Update')

#     def validate_username(self,username):
#         if username.data != current_user.username:

#             user = User.query.filter_by(username=username.data).first()
#             if user:
#                 raise ValidationError('This user name has been taken Please choose another')


#     def validate_email(self,email):
#         if email.data != current_user.email:
#             user = User.query.filter_by(email=email.data).first()
#             if user:
#                 raise ValidationError('This email has been taken Please choose another')

class RequestResetForm(FlaskForm):
    email = EmailField('Email',
                                validators = [DataRequired()])
    submit = SubmitField('Submit')
    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('Email doesn exist')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password' ,validators = [DataRequired()] )
    confirm_password = PasswordField('Confirm Password',validators = [DataRequired(),EqualTo('password')] )
    submit = SubmitField('Reset')




class UpdateAccountForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[DataRequired(), Length(min=2, max=20)],
    )
    email = EmailField(
        'Email',
        validators=[DataRequired(), Email()],
    )
    picture = FileField(
        'Update Profile Picture',
        validators=[FileAllowed(['jpg', 'png','jfif'])],
    )
    bio = TextAreaField(
        "Update your Bio",
        validators=[
            DataRequired(message="Please write something about yourself."),
            Length(max=200, message="Your bio must not exceed 200 characters.")
        ],
        render_kw={"rows": 5}  # Sets the height of the text area
    )
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:  # Allow unchanged username
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('This username has been taken. Please choose another.')

    def validate_email(self, email):
        if email.data != current_user.email:  # Allow unchanged email
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('This email has been taken. Please choose another.')
