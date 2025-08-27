from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import re

from .. import db
from ..models.user import User
from .forms import LoginForm, RegistrationForm, ForgotPasswordForm, ResetPasswordForm

# Create blueprint
auth = Blueprint('auth', __name__)

def is_strong_password(password):
    """Check if the password meets strength requirements."""
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            flash('You have been logged in!', 'success')
            return redirect(next_page or url_for('main.index'))
        
        flash('Invalid email or password', 'danger')
    
    return render_template('auth/login.html', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if username or email already exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already taken. Please choose a different one.', 'danger')
            return render_template('auth/register.html', form=form)
        
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered. Please use a different email or log in.', 'danger')
            return render_template('auth/register.html', form=form)
        
        # Check password strength
        if not is_strong_password(form.password.data):
            flash('Password must be at least 8 characters long and include uppercase, lowercase, numbers, and special characters.', 'danger')
            return render_template('auth/register.html', form=form)
        
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            date_of_birth=form.date_of_birth.data,
            join_date=datetime.utcnow()
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Handle password reset request."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # In a real app, send a password reset email
            flash('If an account exists with this email, you will receive a password reset link.', 'info')
        else:
            # Don't reveal that the email doesn't exist
            flash('If an account exists with this email, you will receive a password reset link.', 'info')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html', form=form)

@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handle password reset with token."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # In a real app, verify the token
    user = User.verify_reset_token(token)
    if not user:
        flash('Invalid or expired token', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        # Check password strength
        if not is_strong_password(form.password.data):
            flash('Password must be at least 8 characters long and include uppercase, lowercase, numbers, and special characters.', 'danger')
            return render_template('auth/reset_password.html', form=form, token=token)
        
        user.set_password(form.password.data)
        db.session.commit()
        
        flash('Your password has been reset. You can now log in with your new password.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', form=form, token=token)

@auth.route('/account')
@login_required
def account():
    """View and edit account details."""
    return render_template('auth/account.html')

@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change the current user's password."""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not current_user.check_password(current_password):
            flash('Current password is incorrect.', 'danger')
        elif new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
        elif not is_strong_password(new_password):
            flash('Password must be at least 8 characters long and include uppercase, lowercase, numbers, and special characters.', 'danger')
        else:
            current_user.set_password(new_password)
            db.session.commit()
            flash('Your password has been updated.', 'success')
            return redirect(url_for('auth.account'))
    
    return render_template('auth/change_password.html')
