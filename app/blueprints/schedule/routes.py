# shift_scheduler/app/blueprints/auth/routes.py

# Standard Libraries
import os
from datetime import datetime, date

# External Libraries
from flask import request, render_template, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
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
        # Get the current username for logging purposes
        
        username = current_user.username
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(url_for('schedule.uploader_window'))

        file = request.files['file']

        # if user does not select file submit an empty part without filename and warn user
        if file.filename == '':
            flash('No selected file')
            return redirect(url_for('schedule.uploader_window'))
        
        # if a file is submitted, check to make sure it is an xml file and that it uses a secure file name
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
                #pass the username to the dataframe as well so we can record who uploaded it in the db
                df = parser.to_dataframe(username)
                
                
                #Check to see if an xml for that date hase previously been uploaded
                date_in_df = df['date'].iloc[0] # Since all records from the newly parsed xml have the same date, just look at the first one
                
                #if a previous xml for the date has been uploaded, confirm with the user that they want to overwrite
                if parser.check_date_exists(date_in_df):
                    flash(f"Records for the date {date_in_df} already exist. Do you want to overwrite?", "warning")
                    return render_template('/confirm_upload.html.j2', date=date_in_df, file_path = file_path)
                
                #if the date has not been previously submitted upload to database
                parser.to_database(df)
                flash('File uploaded to server successful.')

            except Exception as e:
                flash(f'Error processing XML: {str(e)}')
                current_app.logger.error(f"Error processing XML: {str(e)}", exc_info=True)  # XML Errors
                return redirect(url_for('schedule.uploader_window'))

            return redirect(url_for('schedule.uploader_window'))

        else:
            flash('Allowed file types are .xml')
            current_app.logger.warning(f"{username} attempted to upload non xml file: {filename}")
            return redirect(url_for('schedule.uploader_window'))
    
    return render_template("/upload.html.j2")

@schedule_bp.route('/confirm_upload', methods=['GET','POST'])
def confirm_upload():
    decision = request.form.get('decision')
    date_to_check = request.form.get('date')
    
    ### OVERRIGHT = YES
    if decision == "yes":

        username = current_user.username

        try:
                #Begin parsing the file again.  since we did it once, we dont need as much file checking.
                xml_path = request.form.get('file_path')
                current_app.logger.info(f"file_path name passed [{xml_path}]")

                parser = XMLParser(xml_path) #the file_path gets passed to the confirmation form from the upload form as a hidden attribute
                parser.parse_xml()
                #pass the username to the dataframe as well so we can record who uploaded it in the db
                df = parser.to_dataframe(username)

                #Delete old records with the given date
                try:
                    parser.delete_existing_db_records(date_to_check)
                    flash(f'Records from {date_to_check} successfully removed.')
                    current_app.logger.info(f"{username} deleted records from {date_to_check}")

                except Exception as e:
                    flash(f'Error deleting old records: {str(e)}', "warning")
                    current_app.logger.error(f"Error deleting old records: {str(e)}", exc_info=True)
                    return redirect(url_for('schedule.uploader_window'))

                #upload new data to the database
                parser.to_database(df)
                flash("Existing data overwritten successfully.", "success")

        except Exception as e:
            flash(f"Error processing XML: {str(e)}")
            current_app.logger.error(f"Error processing XML: {str(e)}", exc_info=True)
            return redirect(url_for('schedule.uploader_window'))


    ### OVERIGHT = NO
    else:
        flash("Data upload cancelled.", "info")
        
    return redirect(url_for('schedule.uploader_window'))




@schedule_bp.route('/upload_file',methods =['GET'])
@custom_requires_roles('System Admin','Admin', 'Team Lead', 'Floor Lead')
@login_required
def uploader_window():     
    return render_template("/upload.html.j2")