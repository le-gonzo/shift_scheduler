#shift_scheduler/app/models/user.py
from app import db
from datetime import datetime

from sqlalchemy import PrimaryKeyConstraint

from werkzeug.security import generate_password_hash, check_password_hash
from flask_user import UserMixin



#######################################################################
# Core Models
#######################################################################

class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    email_confirmed_at = db.Column(db.DateTime())
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='0')
    # Add a foreign key for Role
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    
    # Change roles to role and remove the secondary argument
    role = db.relationship('Role', backref=db.backref('users', lazy='dynamic'))

    # One-to-one relationship with UserDetail
    user_detail = db.relationship('UserDetail', backref=db.backref('user', uselist=False), uselist=False, cascade="all, delete-orphan")

    @property
    def password(self):
        return self.password_hash

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class ShiftTemplate(db.Model):
    """
    This table defines a generic structure for shift templates. 
    Each record represents a distinct shift column in the scheduled where names are entered
    - id: primary key
    - name: name of the shift (e.g., "DAY 1", "DAY 2", "EVE 1")
    - display_name: How it is displayed in the generated schedule (e.g., "0700", "1100", "1500")
    - start_time: starting time of the shift
    - end_time: ending time of the shift
    """
    __tablename__ = 'shift_template'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True) #name of shift e.g. DAY 1, DAY 2, etc
    display_name = db.Column(db.String(50), unique=True) #How it will be displayed on the form e.g 0700, 1100
    start_time = db.Column(db.Time(timezone = False)) 
    end_time = db.Column(db.Time(timezone = False))

class Assignment(db.Model):
    """
    Represents specific roles or responsibilities assigned during shifts. as they appear on the daily
    """
    __tablename__ = 'assignment'

    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id')) # what location is the assignment associated with?
    name = db.Column(db.String(100)) # Name of the assignment e.g., "MICN", "Triage RN 1"
    valid_start = db.Column(db.Date) # when was this a valid assignment? oldest record from 4/6/2023
    valid_end = db.Column(db.Date) # Null means the assignment is still active
    display_color_overide = db.Column(db.String(6)) # label will inherit location color, but can overide with this value if available

    
class Location(db.Model):
    """
    Represents the physical location of an assignment.
    """
    __tablename__ = 'location'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100)) # e.g., "Triage", "ED1"
    assignments = db.relationship('Assignment', backref='location', lazy='dynamic')
    valid_start = db.Column(db.Date)
    valid_end = db.Column(db.Date)
    display_color =  db.Column(db.String(6)) # template colors for locations can be changed dynamically.
    display_location_label = db.Column(db.Boolean, default=True)
    

class DailyScheduleData(db.Model):
    """
    Represents the Daily Schedule data imported from xml files  
    """
    
    __tablename__ = 'daily_schedule_data'

    date = db.Column(db.Date, index = True)
    entity = db.Column(db.String(100))
    coverage_period = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(50))
    date_detail = db.Column(db.DateTime(timezone= True), default = datetime.utcnow)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(100))
    code = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Float)

    assignment = db.Column(db.String(100), server_default='unassigned')
    #metadata
    record_uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    record_uploaded_by = db.Column(db.String(60))

    __table_args__ = (
        PrimaryKeyConstraint('date', 'coverage_period', 'name', 'code'),
    )

#######################################################################
# LOOKUP TABLES
#######################################################################

# Define the Role model, roles are related to how 
class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)


class LicensesAndCerts(db.Model):
    """licenses and certs, expandable"""
    __tablename__ = 'licenses_and_certs'
    name = db.Column(db.String(100), unique=True, primary_key=True)

class EDStaff(db.Model):
    """ED staff records are updated fromt he API Report files linked to licenses and certs to inform business logic"""
    __tablename__ = 'ed_staff'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=True)

class EDStaffLicensesAndCerts(db.Model):
    """links licenses_and_certs to ed_staff many to many relationship, used to track employee certs and licenses and expiration dates
       for informing business logic"""
    __tablename__ = 'ed_staff_licenses_and_certs'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), db.ForeignKey('ed_staff.id', ondelete='CASCADE'))
    license_or_cert_name = db.Column(db.String(100), db.ForeignKey('licenses_and_certs.name', ondelete='CASCADE'))
    expiration_date = db.Column(db.Date)


# Define the group model
class Group(db.Model):
    """These are user groups for the webapp, Roles are general roles like system admins etc.. groups allow fine tuning
       for ad hoc groups... e.g. ED Physician group,  Unit Practice Council members, etc"""
    __tablename__ = 'group'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

class ShiftCodeRef(db.Model):
    """A running record of the shift codes as they appear in the API Report, includes metadata for business logic use
    """
    __tablename__ = 'shift_code_ref'
    code = db.Column(db.String(100), unique=True, primary_key=True)
    productive = db.Column(db.Boolean(), nullable=True)
    orientation = db.Column(db.Boolean(), nullable=True)
    shift_start = db.Column(db.Time, nullable=True)
    shift_end = db.Column(db.Time, nullable=True)


class ShiftRoleRef(db.Model):
    """ A running record of employee roles as they appear in the API Report"""
    __tablename__ = 'shift_role_ref'
    role = db.Column(db.String(100), unique=True, primary_key=True)


#######################################################################
# LDAP user data look up
#######################################################################

class LDAPUserData(db.Model):
    """LDAP user data saved from LDAP queries for faster retrieval"""
    __tablename__ = 'ldap_user_data'

    uciUCNetID = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(20), db.ForeignKey('user.username'))  # Foreign key to User table's username column
    uciCampusID = db.Column(db.String(12))
    displayName = db.Column(db.String(60))
    sn = db.Column(db.String(60))
    givenName = db.Column(db.String(60))
    middleName = db.Column(db.String(60))
    uciPublishedTitle1 = db.Column(db.String(60))
    uciAffiliation = db.Column(db.String(100))
    uciPrimaryDepartmentCode = db.Column(db.String(10))
    uciPrimaryDepartment = db.Column(db.String(30))
    uciLevel3DepartmentDescription = db.Column(db.String(30))
    ou = db.Column(db.String(60))
    uciMailDeliveryPoint = db.Column(db.String(60))
    uciPublishedOfficeAddress1 = db.Column(db.String(60))
    uciPublishedDepartment1 = db.Column(db.String(60))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('ldap_user_data', uselist=False))


#######################################################################
# Expanded User Info Model
#######################################################################

class UserDetail(db.Model):
    __tablename__ = 'user_detail'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    main_contact_number = db.Column(db.String(15))
    secondary_contact_number = db.Column(db.String(15), nullable=True)
    date_of_birth = db.Column(db.Date)
    emergency_contact_name = db.Column(db.String(100))
    emergency_contact_number = db.Column(db.String(15))
    position_title = db.Column(db.String(100))
    department = db.Column(db.String(100))
    hire_date = db.Column(db.Date)
    employee_id = db.Column(db.String(100), nullable=True)
    certifications = db.Column(db.Text, nullable=True)
    assigned_shift = db.Column(db.String(100), nullable=True)
    employment_status = db.Column(db.String(100), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

#######################################################################
# Relationship Models
#######################################################################


# Define the UserRoles relationship
class UserGroups(db.Model):
    __tablename__ = 'user_groups'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id', ondelete='CASCADE'))


