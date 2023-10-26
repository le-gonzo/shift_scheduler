from flask import render_template
from flask_login import login_required


#from app.utils import roles_required

from . import dashboard_bp

@dashboard_bp.route('/home')
@login_required
def home():
    return render_template("/layouts/dashboard_base.html")

@dashboard_bp.route('/profile')
@login_required
def profile():
    return render_template("/home/profile.html")

from . import routes