#shift_scheduler/app/utils/__init__.py
from functools import wraps
from flask import abort, redirect, url_for, flash
from flask_login import current_user
from config import ALLOWED_EXTENSIONS


def allowed_file(filename):
    """
    Check if the uploaded file has an allowed extension.

    :param filename: Name of the uploaded file.
    :return: True if the file has an allowed extension, otherwise False.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def is_dark_color(hex_color):
    """
    checks the hex color value and returns if the value is_dark or not (i.e.brightness less than 128)

    :param hex_color: the 6 chracter hex color
    """

    hex_color = hex_color.lstrip('#')

    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    #Calculate the luminance value
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    
    #return True if dark, else False
    return luminance < 0.5




def custom_requires_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.role.name not in roles:
                flash('Authorization required.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return wrapped
    return wrapper
