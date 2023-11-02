# shift_scheduler/app/blueprints/auth/routes.py

# Standard Libraries
import os
from datetime import datetime, date

# External Libraries
from flask import request, render_template, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required
from sqlalchemy import or_, and_
from sqlalchemy.orm import joinedload, aliased
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# Internal Modules
from app.models.user import Location, Assignment, ShiftTemplate
from . import schedule_bp
from .utils.xml_parser import XMLParser
from app.utils import custom_requires_roles, is_dark_color, allowed_file

# Configuration
from config import UPLOAD_FOLDER


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
    

    return render_template('schedule.html.j2', locations_with_assignments = locations_with_assignments, 
                           timeslots = timeslots, is_dark_color = is_dark_color)


@schedule_bp.route('/upload',methods =['GET','POST'])
@custom_requires_roles('System Admin','Admin', 'Team Lead', 'Floor Lead')
@login_required
def upload():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(url_for('schedule.uploader_window'))

        file = request.files['file']

        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(url_for('schedule.uploader_window'))
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)

            try:
                file.save(file_path)
            except Exception as e:
                flash(f'Error importing file: {str(e)}')
                return redirect(url_for('schedule.uploader_window'))
            try:
                #Begin parsing file
                parser = XMLParser(file_path)
                parser.parse_xml()
                df = parser.to_dataframe()
                parser.to_database(df)
                flash('File uploaded to server, processing file...')
            except Exception as e:
                flash(f'Error processing XML: {str(e)}')
                current_app.logger.error(f"Error processing XML: {str(e)}", exc_info=True)  # XML Errors
                return redirect(url_for('schedule.uploader_window'))

            return redirect(url_for('schedule.uploader_window'))

        else:
            flash('Allowed file types are .xml')
            return redirect(url_for('schedule.uploader_window'))
    
    return render_template("/upload.html.j2")

@schedule_bp.route('/upload_file',methods =['GET'])
@custom_requires_roles('System Admin','Admin', 'Team Lead', 'Floor Lead')
@login_required
def uploader_window():     
    return render_template("/upload.html.j2")