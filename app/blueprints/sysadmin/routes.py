#shift_scheduler/app/blueprints/sysadmin/routes.py

# Framework and extensions
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required

# Internal Modules
from app.models.user import User, Role
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from . import sysadmin_bp
from app.utils import custom_requires_roles


@sysadmin_bp.route('/user_overview', methods=['GET'])
@login_required
@custom_requires_roles('Admin', 'System Admin')
def user_overview():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)  # default to 20, can be changed by the user
    pagination = User.query.paginate(page=page, per_page=per_page, error_out=False)
    users = pagination.items

    return render_template('user_overview.html', users=users, pagination=pagination)


@sysadmin_bp.route('/manage_roles', methods=['GET'])
@login_required
@custom_requires_roles('System Admin')
def manage_roles():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)  # default to 20, can be changed by the user
    
    pagination = Role.query.paginate(page=page, per_page=per_page, error_out=False)
    roles = pagination.items

    return render_template('manage_roles.html', Roles=roles, pagination=pagination)

