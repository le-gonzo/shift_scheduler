#shift_scheduler/app/blueprints/main/__init__.py
from flask import Blueprint
import os

current_directory = os.path.dirname(os.path.realpath(__file__))
template_directory = os.path.join(current_directory, 'templates')

# Create the blueprint object
main_bp = Blueprint('main', __name__, template_folder=template_directory)

# This is an important step: import the routes after the Blueprint object is defined 
# to avoid circular imports.
from . import routes