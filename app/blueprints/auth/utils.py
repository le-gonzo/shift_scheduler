#shift_scheduler/app/blueprints/auth/utils.py
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature, BadTimeSignature
from flask_mail import Message
from flask import url_for, current_app, render_template
from app import mail, db

from app.models.user import User

# ========================================
# TOKEN UTILITIES
# ========================================
def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=current_app.config['SECURITY_PASSWORD_SALT'])

def confirm_token(token):
    """
    Confirms the token is valid and returns the email associated with it.
    `expiration` defines the maximum age of the token in seconds (default is 1 hour).
    """
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    expiration = current_app.config['TOKEN_EXPIRATION']

    try:
        email = serializer.loads(
            token,
            salt=current_app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except SignatureExpired:
        current_app.logger.warning("Valid token has expired.")
        _remove_unconfirmed_user(email)
        return None  # valid token, but expired
    except BadSignature:
        current_app.logger.warning("Invalid token has been provided.")
        return None  # invalid token
    
    return email

def _remove_unconfirmed_user(email):
    """
    Remove unconfirmed user by email.
    This function should be implemented based on the specific database setup.
    """
    # Fetch the user by email
    user = User.query.filter_by(email=email).first()
    
    # If the user exists and is not confirmed, delete them
    if user and user.email_confirmed_at is None:
         db.session.delete(user)
         db.session.commit()


# ========================================
# EMAIL UTILITIES
# ========================================
def send_confirmation_email(user,ldap_user_data, token):
    """
    Send a confirmation email to the specified user.

    Parameters:
    - user: The user instance to whom the email should be sent.
    - token: The token generated for the user.
    """
    
    # Define the email parameters
    subject = "Confirm your email address"
    sender = current_app.config['MAIL_DEFAULT_SENDER']
    recipients = [user.email]
    confirm_email_link = url_for('auth.confirm_email', token=token, _external=True)
    ldap_user_data = ldap_user_data
    
    # Load the email content from the template and render it
    html_body = render_template('flask_user/emails/confirm_email_message.html',
                                user=user,
                                ldap_user_data = ldap_user_data, 
                                confirm_email_link=confirm_email_link)
    
    # Create message and send email
    message = Message(subject, recipients=recipients, html=html_body, sender=sender)
    mail.send(message)

# ========================================
# Business Logic
# ========================================
#Constants for Role IDs

ROLE_ADMINISTRATOR = 2
ROLE_TEAM_LEAD = 3
ROLE_ED_STAFF = 5
ROLE_GUEST = 6

def assign_role_based_on_ldap_data(ldap_data):
    """
    Assign a role based on the given LDAP data.
    
    Parameters
    ----------
    ldap_data : object
        The LDAP data object containing user details. It's expected to have attributes 
        `uciPublishedTitle1` and `uciPrimaryDepartment`.
        
    Returns
    -------
    int
        Role ID based on the user's LDAP data. It returns one of the following:
        - ROLE_ADMINISTRATOR: If the user's title indicates they are an administrator.
        - ROLE_TEAM_LEAD: If the user's title indicates they are a team lead.
        - ROLE_ED_STAFF: If the user belongs to the Emergency Department.
        - ROLE_GUEST: Default role for other users or if LDAP data is not provided.
    """
    if not ldap_data:
        return ROLE_GUEST

    title = ldap_data.uciPublishedTitle1
    department = ldap_data.uciPrimaryDepartment

    if not title:
        return ROLE_GUEST

    if not department:
        return ROLE_GUEST

    # Check for Administrator roles
    if title in ["Director of Emergency/Trauma Services", "ED Manager"] and department == "Emergency Department":
        return ROLE_ADMINISTRATOR

    # Check for Team Lead role
    if title in ["Asst Nurse Mgr", "Asst. Nurse Mgr", "Assistant Nurse Manager"] and department == "Emergency Department":
        return ROLE_TEAM_LEAD

    # Check for ED Staff role
    if department == "Emergency Department":
        return ROLE_ED_STAFF

    # Default to Guest role
    return ROLE_GUEST
    

# ========================================
# SMS UTILITIES # TODO
# ========================================
