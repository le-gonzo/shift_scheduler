from flask import render_template
from . import dashboard_bp

@dashboard_bp.route('/home')
def home():
    return render_template("/layouts/dashboard_base.html")

from . import routes