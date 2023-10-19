#shift_scheduler/app/blueprints/auth/forms.py
import os
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASSWORDS_FILE_PATH = os.path.join(BASE_DIR, 'static', 'password_blacklist.txt')


with open(PASSWORDS_FILE_PATH, 'r') as file:
    password_blacklist = [line.strip() for line in file]


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    
    def validate_email(self, field):
        if not field.data.endswith('@hs.uci.edu'):
            raise ValidationError('Only emails ending with @hs.uci.edu are allowed.')
        
    def validate_password(self, field):
        if len(field.data) < 6:
            raise ValidationError('Password must be at least 6 characters long.')
        if field.data in password_blacklist:
            raise ValidationError("No. Try a little harder... or I'll demand uppercase, numbers AND symbols!")

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
