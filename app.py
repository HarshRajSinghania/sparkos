import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_migrate import Migrate
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from config import config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

# Import models after db to avoid circular imports
from models.user import User
from models.habit import Habit, HabitCompletion
from models.wallet import Transaction, SavingsGoal

def create_app(config_name='default'):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Apply configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Register blueprints
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from .habits import habits as habits_blueprint
    app.register_blueprint(habits_blueprint, url_prefix='/habits')
    
    from .wallet import wallet as wallet_blueprint
    app.register_blueprint(wallet_blueprint, url_prefix='/wallet')
    
    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api/v1')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403
    
    # Template filters
    @app.template_filter('format_currency')
    def format_currency(value):
        return f'${value:,.2f}'
    
    @app.template_filter('format_date')
    def format_date(value, format='%B %d, %Y'):
        if value is None:
            return ''
        return value.strftime(format)
    
    @app.template_filter('time_ago')
    def time_ago(value):
        now = datetime.utcnow()
        diff = now - value
        
        if diff < timedelta(minutes=1):
            return 'just now'
        elif diff < timedelta(hours=1):
            minutes = int(diff.seconds / 60)
            return f'{minutes} minute{"s" if minutes > 1 else ""} ago'
        elif diff < timedelta(days=1):
            hours = int(diff.seconds / 3600)
            return f'{hours} hour{"s" if hours > 1 else ""} ago'
        elif diff < timedelta(days=30):
            days = diff.days
            return f'{days} day{"s" if days > 1 else ""} ago'
        else:
            return value.strftime('%B %d, %Y')
    
    # Shell context
    @app.shell_context_processor
    def make_shell_context():
        return {
            'db': db, 
            'User': User, 
            'Habit': Habit, 
            'Transaction': Transaction,
            'SavingsGoal': SavingsGoal
        }
    
    return app

# This is only used when running directly with Python
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
