# shift_scheduler/app/blueprints/auth/routes.py
from datetime import datetime, date
from sqlalchemy import or_, and_
from sqlalchemy.orm import joinedload, aliased

# Framework and extensions
from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required

# Internal Modules
from app.models.user import Location, Assignment, ShiftTemplate
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from . import schedule_bp


from app.utils import custom_requires_roles, is_dark_color


@schedule_bp.route('/daily', methods=['GET'])
@login_required
@custom_requires_roles('System Admin','Admin', 'Team Lead', 'Floor Lead')
def daily():
    # Create an alias for the Assignment table so you can apply filters directly
    assignment_alias1 = aliased(Assignment)

    # Get the current date
    current_date = date.today()

    locations_with_assignments = (Location.query
    .join(assignment_alias1, Location.id == assignment_alias1.location_id)
        .filter(
            or_(Location.valid_end == None, 
                and_(Location.valid_start <= current_date, Location.valid_end >= current_date)
            )
        )
        .filter(
            or_(assignment_alias1.valid_end == None, 
                and_(assignment_alias1.valid_start <= current_date, assignment_alias1.valid_end >= current_date)
            )
        )
    ).all()

    timeslots = ShiftTemplate.query.all()
    

    return render_template('schedule.html', locations_with_assignments = locations_with_assignments, 
                           timeslots = timeslots, is_dark_color = is_dark_color)