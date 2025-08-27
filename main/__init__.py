from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func

from ..models.user import User
from ..models.habit import Habit, HabitCompletion
from ..models.wallet import Transaction, SavingsGoal

# Create blueprint
main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    """Render the home page with user's dashboard."""
    # Get user's recent habits
    recent_habits = Habit.query.filter_by(user_id=current_user.id)\
        .order_by(Habit.last_updated.desc())\
        .limit(5).all()
    
    # Get today's habit completions
    today = datetime.utcnow().date()
    completed_habits = HabitCompletion.query\
        .join(Habit, Habit.id == HabitCompletion.habit_id)\
        .filter(Habit.user_id == current_user.id)\
        .filter(func.date(HabitCompletion.completion_date) == today)\
        .count()
    
    # Get recent transactions
    recent_transactions = Transaction.query\
        .filter_by(user_id=current_user.id)\
        .order_by(Transaction.date.desc())\
        .limit(5).all()
    
    # Calculate wallet balance
    income = Transaction.query\
        .filter_by(user_id=current_user.id, transaction_type='income')\
        .with_entities(func.sum(Transaction.amount))\
        .scalar() or 0
    
    expenses = Transaction.query\
        .filter_by(user_id=current_user.id, transaction_type='expense')\
        .with_entities(func.sum(Transaction.amount))\
        .scalar() or 0
    
    balance = income - expenses
    
    # Get savings goals progress
    savings_goals = SavingsGoal.query\
        .filter_by(user_id=current_user.id)\
        .order_by(SavingsGoal.target_date.asc())\
        .limit(3).all()
    
    return render_template('index.html',
                         recent_habits=recent_habits,
                         completed_habits=completed_habits,
                         recent_transactions=recent_transactions,
                         balance=balance,
                         savings_goals=savings_goals)

@main.route('/profile')
@login_required
def profile():
    """Render the user's profile page."""
    return render_template('profile.html')

@main.route('/settings')
@login_required
def settings():
    """Render the user's settings page."""
    return render_template('settings.html')

@main.route('/help')
def help():
    """Render the help page."""
    return render_template('help.html')

@main.route('/about')
def about():
    """Render the about page."""
    return render_template('about.html')

@main.route('/privacy')
def privacy():
    """Render the privacy policy page."""
    return render_template('privacy.html')

@main.route('/terms')
def terms():
    """Render the terms of service page."""
    return render_template('terms.html')
