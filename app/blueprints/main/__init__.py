#shift_scheduler/app/blueprints/main/__init__.py
from flask import Blueprint

# Create the blueprint object
main_bp = Blueprint('main', __name__)

# This is an important step: import the routes after the Blueprint object is defined 
# to avoid circular imports.
from . import routes