from flask import render_template, redirect, url_for
from flask_login import current_user
from . import main_bp

@main_bp.route('/')
def home():
    if current_user.is_authenticated:
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