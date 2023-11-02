# shift_scheduler/app/blueprints/auth/routes.py
from datetime import datetime


# Framework and extensions
from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required

# Internal Modules
from app.models.user import User, LDAPUserData
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from . import auth_bp
from .forms import RegistrationForm, LoginForm
from .utils import generate_confirmation_token, confirm_token, send_confirmation_email, assign_role_based_on_ldap_data

from app.utils.ldap_utils import UCILDAPLookup


@auth_bp.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        # Check that email exists and password is correct
        if not user:
            flash('No account exists with that email. Register first.', 'danger')
            return redirect(url_for('auth.register'))
        elif not user.check_password(form.password.data):
            flash('Password is incorrect. Please try again.', 'danger')
        else:
            login_user(user)
            return redirect(url_for('dashboard.home'))

    return render_template('login.html', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))

@auth_bp.route('/protected')
@login_required
def protected_route():
    return "This is only for logged-in users!"

@auth_bp.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    searcher = UCILDAPLookup()


    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        
        #if the user already exists, no need to reregister, reroute to login page
        if existing_user:
            flash('Email already exists. Please log in instead.', 'info')
            return redirect(url_for('auth.login'))
        

        #If the user does not already exist, we create a new user
        user = User(email=form.email.data)
        user.username = form.email.data.split('@')[0]
        user.set_password(form.password.data)
        user.active = False

        # Adding the user to the database with error handling
        try:
            db.session.add(user)
            db.session.commit()
            current_app.logger.info(f"New user registered: {form.email.data}")  # Log the successful registration
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error registering user {form.email.data}: {e}")  # Log the error
            flash('An error occurred. Please try again.', 'danger')
            return render_template('register.html', form=form)
        

        #Lookup the newly registered user within the LDAP system to get more information.
        uiddf = searcher.uidlookup(user.username)
        
        # Check if the lookup was successful.
        if not uiddf.empty:
            # Convert the first row of the DataFrame to a dictionary.
            ldap_data_dict = uiddf.iloc[0].to_dict()

            # Instantiate the LDAPUserData model.
            ldap_user_data = LDAPUserData(**ldap_data_dict)

            # Add the LDAP user data to the database with error handling.
            try:
                db.session.add(ldap_user_data)
                db.session.commit()
                current_app.logger.info(f"LDAP data for user {user.email} saved successfully.")
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Error saving LDAP data for user {user.email}: {e}")

        
        # Sending Confirmation email with error handling
        try:
            token = generate_confirmation_token(user.email)
            current_app.logger.debug(f"confirmation token generated: {token}")

            send_confirmation_email(user,ldap_user_data, token)

            current_app.logger.debug(f"confirmation email sent to: {form.email.data}")
        except Exception as e:
            flash('Unable to send a confirmation email. Please try again.', 'danger')
            current_app.logger.error(f"Error emailing user {form.email.data}: {e}")

        return render_template('confirmation.html', user = user)

    return render_template('register.html', form=form)

@auth_bp.route('/confirm/<token>')
def confirm_email(token):
    email = confirm_token(token)
    if email is None:
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for('main.home'))
    
    user = User.query.filter_by(email=email).first()
    if user:
        user.active = True
        user.email_confirmed_at = datetime.utcnow()

        # Assign the user's role based on LDAP data.
        user.role_id = assign_role_based_on_ldap_data(user.ldap_user_data)

        db.session.commit()
        flash('Your email has been confirmed!', 'success')
    else:
        flash('User not found!', 'danger')

    
    return redirect(url_for('main.home'))
