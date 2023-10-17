#shift_scheduler/app/blueprints/auth/__init.py
from flask import Blueprint

# Create the blueprint object
auth_bp = Blueprint('auth', __name__)

# This is an important step: import the routes after the Blueprint object is defined 
# to avoid circular imports.
from . import routes
