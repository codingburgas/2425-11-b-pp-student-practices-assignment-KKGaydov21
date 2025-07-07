"""
Application factory and initialization
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from ..config.settings import get_config



class Base(DeclarativeBase):
    pass

app = Flask(__name__)
# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()


def create_app(config_name=None):
    """Application factory pattern."""
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    config_class = get_config()
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Configure Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Add proxy fix for production
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Register blueprints
    from ..blueprints.auth import auth_bp
    from ..blueprints.main import main_bp
    from ..blueprints.assessment import assessment_bp
    from ..blueprints.dashboard import dashboard_bp
    from ..blueprints.api import api_bp
    from ..blueprints.admin import admin_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(assessment_bp, url_prefix='/assessment')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from ..models.user import User
        return User.query.get(int(user_id))
    
    # Create database tables
    with app.app_context():
        from ..models import user, assessment  # Import models
        db.create_all()
    
    return app