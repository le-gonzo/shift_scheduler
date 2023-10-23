#shift_scheduler/app/blueprints/auth/utils.py
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature, BadTimeSignature
from flask_mail import Message
from flask import url_for, current_app, render_template
from app import mail

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
        return None  # valid token, but expired
    except BadSignature:
        current_app.logger.warning("Invalid token has been provided.")
        return None  # invalid token
    
    return email

# ========================================
# EMAIL UTILITIES
# ========================================
def send_confirmation_email(user, token):
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
    
    # Load the email content from the template and render it
    html_body = render_template('flask_user/emails/confirm_email_message.html',user=user, confirm_email_link=confirm_email_link)
    
    # Create message and send email
    message = Message(subject, recipients=recipients, html=html_body, sender=sender)
    mail.send(message)
    

# ========================================
# SMS UTILITIES # TODO
# ========================================
