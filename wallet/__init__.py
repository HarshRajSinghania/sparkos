from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from sqlalchemy import func, extract, and_, or_
from decimal import Decimal

from .. import db
from ..models.wallet import Transaction, SavingsGoal, TransactionCategory, TransactionType
from ..models.user import User
from .forms import TransactionForm, SavingsGoalForm, BudgetForm, TransferForm

# Create blueprint
wallet = Blueprint('wallet', __name__)

# Common expense categories
COMMON_EXPENSE_CATEGORIES = [
    'Food & Dining', 'Shopping', 'Transportation', 'Bills & Utilities',
    'Entertainment', 'Health & Medical', 'Education', 'Gifts & Donations',
    'Personal Care', 'Travel', 'Groceries', 'Subscriptions', 'Other'
]

# Common income categories
COMMON_INCOME_CATEGORIES = [
    'Allowance', 'Gift', 'Job', 'Freelance', 'Investment', 'Other Income'
]

# Import route handlers
from . import routes  # This will import all routes from routes.py

# Register error handlers
@wallet.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403

@wallet.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@wallet.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500
