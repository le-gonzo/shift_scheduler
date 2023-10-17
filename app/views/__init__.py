from flask import render_template, request
from .. import app

@app.route('/schedule')
def display_schedule():
    # Here, we would typically get the schedule from the database
    # For now, let's use a dummy schedule
    schedule = {
    'date': '2023-10-10',
    'day_of_week': 'Tuesday',
    'blocks': [
        {
            'name': '_non-productive',
            'timeslots': ['0700', '1100', '1500', '1900', '2300', '0300'],
            'assignments': [
                {
                    'role': 'ANM',
                    'locker': '1',
                    'employee': 'nurse1'
                },
                {
                    'role': 'PCC',
                    'locker': '2',
                    'employee': 'nurse2'
                }
            ]
        },
        {
            'name': 'MICN',
            'timeslots': ['0700', '1100', '1500', '1900', '2300', '0300'],
            'assignments': [
                {
                    'role': 'MICN',
                    'locker': '41',
                    'employee': 'MICN1'
                }
            ]
        },
        {
            'name': 'Triage',
            'timeslots': ['0700', '1100', '1500', '1900', '2300', '0300'],
            'assignments': [
                {
                    'role': 'TCC',
                    'locker': '1',
                    'employee': 'TCC1'
                },
                {
                    'role': 'Triage RN 1',
                    'locker': '2',
                    'employee': 'Triage_RN1'
                },
                {
                    'role': 'Triage RN 2',
                    'locker': '8',
                    'employee': 'employee_name'
                },
                {
                    'role': 'TRN',
                    'locker': '9',
                    'employee': 'employee_name'
                },
                {
                    'role': 'RTS #1',
                    'locker': '9',
                    'employee': 'employee_name'
                },
                {
                    'role': 'RTS #2',
                    'locker': '9',
                    'employee': 'employee_name'
                },
                {
                    'role': 'Surveillance RN (1200)',
                    'locker': '9',
                    'employee': 'employee_name'
                },
                {
                    'role': 'Team DC RN (1300)',
                    'locker': '9',
                    'employee': 'employee_name'
                },
                {
                    'role': 'FastTrack',
                    'locker': '9',
                    'employee': 'employee_name'
                },
                {
                    'role': 'Triage Break RN',
                    'locker': '9',
                    'employee': 'employee_name'
                },
                {
                    'role': 'SHA',
                    'locker': '9',
                    'employee': 'employee_name'
                }

            ]
        },
        {
            'name': 'ED 1',
            'timeslots': ['0700', '1100', '1500', '1900', '2300', '0300'],
            'assignments': [
                {
                    'role': 'Trauma RN 1',
                    'locker': '10',
                    'employee': 'employee_name'
                },
                {
                    'role': 'Trauma RN 2',
                    'locker': '14',
                    'employee': 'employee_name'
                }
            ]
        },
        {
            'name': 'ED 2',
            'timeslots': ['0700', '1100', '1500', '1900', '2300', '0300'],
            'assignments': [
                {
                    'role': 'SIT',
                    'locker': '15',
                    'employee': 'employee_name'
                },
                {
                    'role': 'E,F,G,H',
                    'locker': '16',
                    'employee': 'employee_name'
                }
            ]
        }
        # ... Add more blocks as needed
    ],
    'sick_calls': 'John Doe, Jane Smith', # example sick calls
    'staffing_issues': 'Short-staffed for night shift' # example staffing issues
}
    return render_template('schedule.html', schedule=schedule)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part in the request.'

        file = request.files['file']

        if file.filename == '':
            return 'No selected file.'

        if file and allowed_file(file.filename):
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            return 'File uploaded successfully!'

        return 'Allowed file types are .xml'
    else:
        return render_template('upload.html')
    






