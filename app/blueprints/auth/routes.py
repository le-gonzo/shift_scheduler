# shift_scheduler/app/blueprints/auth/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user
from app.models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from . import auth_bp
from .forms import RegistrationForm, LoginForm

@auth_bp.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        # Check that email exists
        if not user:
            flash('No account exists with that email. Register first.', 'danger')
            return redirect(url_for('auth.register'))

        # Check that password is correct
        if user and not user.check_password(form.password.data):
            flash('Password is incorrect. Please try again.', 'danger')
            return render_template('login.html', form=form)

        # Login user
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('main.home'))

    return render_template('login.html', form=form)

@auth_bp.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        
        if existing_user:
            flash('Email already exists. Please log in instead.', 'info')
            return redirect(url_for('auth.login'))

        user = User(email=form.email.data)
        user.set_password(form.password.data)

        # Adding the user to the database with error handling
        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            # You can log the error 'e' for debugging purposes if needed
            flash('An error occurred. Please try again.', 'danger')
            return render_template('register.html', form=form)

        return redirect(url_for('auth.login'))

    return render_template('register.html', form=form)
