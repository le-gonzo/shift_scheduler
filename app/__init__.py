# shift_scheduler/app/__init__.py

# 1. Standard Library Imports
import os
import logging
from logging.handlers import RotatingFileHandler

# 2. Third-party Library Imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from flask_user import UserManager


# 3. Extensions Instances
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()
migrate = Migrate()


def create_app():
    # App Configurations
    app = Flask(__name__) #, template_folder='./templates'
    app.config.from_object('config')  # Load all configurations from config.py
    from app.models.user import User  # Directly import User
    
    # Extensions Initialization
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    # Instantiate UserManager; even though it's not directly accessed here,
    # this setup initializes the UserManager with the app and db which is 
    # required for its functionality in other parts of the application
    user_manager = UserManager(app, db, User)

    
    login_manager.login_view = "auth.login"
    
    # User Loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User  # This import avoids circular dependencies
        user = User.query.get(int(user_id))
        if user:
            return user
        return None
    
    # Blueprints
    from app.blueprints.main import main_bp
    app.register_blueprint(main_bp)
    from app.blueprints.auth import auth_bp
    app.register_blueprint(auth_bp)
    from app.blueprints.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    from app.blueprints.sysadmin import sysadmin_bp
    app.register_blueprint(sysadmin_bp, url_prefix='/sysadmin')
    from app.blueprints.schedule import schedule_bp
    app.register_blueprint(schedule_bp, url_prefix='/schedule')

    
    # Logging setup
    if not app.debug:
        # Ensure logs directory exists
        if not os.path.exists('logs'):
            os.mkdir('logs')

        file_handler = RotatingFileHandler('logs/app.log', maxBytes=1024 * 1024 * 10, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Shift Scheduler startup')
    
    return app