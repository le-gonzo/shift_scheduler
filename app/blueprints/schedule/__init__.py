#shift_scheduler/app/blueprints/schedule/__init__.py
from flask import Blueprint
import os

current_directory = os.path.dirname(os.path.realpath(__file__))
template_directory = os.path.join(current_directory, 'templates')
static_directory = os.path.join(current_directory, 'static')

# Create the blueprint object
schedule_bp = Blueprint('schedule', 
                         __name__, 
                         template_folder=template_directory, 
                         static_folder=static_directory
                         )

# This is an important step: import the routes after the Blueprint object is defined 
# to avoid circular imports.
from . import routes