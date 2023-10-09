from flask import Flask, render_template

app = Flask(__name__, template_folder='./templates')

@app.route('/')
def home():
    return "Hello, Flask!"

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
                    'locker': '1'
                },
                {
                    'role': 'PCC',
                    'locker': '2'
                }
            ]
        },
        {
            'name': 'Triage',
            'timeslots': ['0700', '1100', '1500', '1900', '2300', '0300'],
            'assignments': [
                {
                    'role': 'MICN',
                    'locker': '1'
                },
                {
                    'role': 'Triage RN',
                    'locker': '2'
                },
                {
                    'role': 'Triage RN 2',
                    'locker': '8'
                },
                {
                    'role': 'IRN',
                    'locker': '9'
                }
            ]
        },
        {
            'name': 'ED 1',
            'timeslots': ['0700', '1100', '1500', '1900', '2300', '0300'],
            'assignments': [
                {
                    'role': 'Trauma RN 1',
                    'locker': '10'
                },
                {
                    'role': 'Trauma RN 2',
                    'locker': '14'
                }
            ]
        },
        {
            'name': 'ED 2',
            'timeslots': ['0700', '1100', '1500', '1900', '2300', '0300'],
            'assignments': [
                {
                    'role': 'SIT',
                    'locker': '15'
                },
                {
                    'role': 'E,F,G,H',
                    'locker': '16'
                }
            ]
        }
        # ... Add more blocks as needed
    ],
    'sick_calls': 'John Doe, Jane Smith', # example sick calls
    'staffing_issues': 'Short-staffed for night shift' # example staffing issues
}
    return render_template('schedule.html', schedule=schedule)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
