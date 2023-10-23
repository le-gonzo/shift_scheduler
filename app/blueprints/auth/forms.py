#shift_scheduler/app/blueprints/auth/forms.py
import os
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo

from flask import current_app

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
            current_app.logger.warning(f"Attempt to register with invalid email: {field.data}")  # Log the warning
            raise ValidationError('Only emails ending with @hs.uci.edu are allowed.')
        
    def validate_password(self, field):
        if len(field.data) < 6:
            current_app.logger.warning(f"Attempt to register with short password: {field.data}")  # Log the warning
            raise ValidationError('Password must be at least 6 characters long.')
        if field.data in password_blacklist:
            current_app.logger.warning(f"Attempt to register with blacklisted password: {field.data}")
            raise ValidationError("Look... We aren't deciding on nuclear launch codes here, but you do need to try a little harder. Don't make me bring uppercase, numbers AND symbols into this")

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
