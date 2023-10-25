from flask import render_template
from . import dashboard_bp

@dashboard_bp.route('/home')
def home():
    return render_template("/layouts/dashboard_base.html")

@dashboard_bp.route('/profile')
def profile():
    return render_template("/home/profile.html")

from . import routes