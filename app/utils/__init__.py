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
