#shift_scheduler/app/blueprints/auth/routes.py
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_user
from app.forms import RegistrationForm, LoginForm
from app.models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('main.home'))
    return render_template('login.html', form=form)

@auth_bp.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Hash the user's password
        hashed_password = generate_password_hash(form.password.data)
        user = User(email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)