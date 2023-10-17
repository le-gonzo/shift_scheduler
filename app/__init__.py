#shift_scheduler/app/__init__.py
# 1. Imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from flask_user import UserManager

# 2. Extensions Instances
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()
migrate = Migrate()

def create_app():
    # App Configurations
    app = Flask(__name__) #, template_folder='./templates'
    app.config.from_object('config')  # Load all configurations from config.py
    
    # Extensions Initialization
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
    
    login_manager.login_view = "auth.login"
    
    # User Loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User  # This import avoids circular dependencies
        return User.query.get(int(user_id))
    
    # Blueprints
    from app.blueprints.main import main_bp
    app.register_blueprint(main_bp)
    from app.blueprints.auth import auth_bp
    app.register_blueprint(auth_bp)

    # User Manager Configuration
    # UserManager is instantiated for its side effects (setup routes and other configurations)
    from app.models.user import User  # Directly import User
    user_manager = UserManager(app, db, User)
    
    return app