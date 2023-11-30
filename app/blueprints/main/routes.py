from flask import render_template, redirect, url_for, flash
from flask_login import current_user, logout_user
from app.models.user import User
from . import main_bp

@main_bp.route('/')
def home():
    if current_user.is_authenticated:
        # Check if current user still exists in the database i.e. wasnt deleted while still logged in
        if not User.query.get(current_user.id):
            logout_user()
            flash('Your account no longer exists.', 'danger')
            return redirect(url_for('auth.login'))
        return redirect(url_for('dashboard.home'))
    return render_template("index.html")

@main_bp.errorhandler(403)
def forbidden(e):
    return render_template("page-403.html")

@main_bp.errorhandler(404)
def forbidden(e):
    return render_template("page-404.html")

@main_bp.errorhandler(500)
def forbidden(e):
    return render_template("page-500.html")