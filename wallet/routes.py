from flask import render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from sqlalchemy import func, extract, and_, or_
from decimal import Decimal

from .. import db
from ..models.wallet import Transaction, SavingsGoal, TransactionType
from . import wallet
from .forms import TransactionForm, SavingsGoalForm, BudgetForm, TransferForm

# Common categories
COMMON_EXPENSE_CATEGORIES = [
    'Food & Dining', 'Shopping', 'Transportation', 'Bills & Utilities',
    'Entertainment', 'Health & Medical', 'Education', 'Gifts & Donations',
    'Personal Care', 'Travel', 'Groceries', 'Subscriptions', 'Other'
]

COMMON_INCOME_CATEGORIES = [
    'Allowance', 'Gift', 'Job', 'Freelance', 'Investment', 'Other Income'
]

# Wallet Dashboard
@wallet.route('/')
@login_required
def index():
    """Display the wallet dashboard with summary and recent transactions."""
    today = date.today()
    first_day = today.replace(day=1)
    last_day = (first_day.replace(month=first_day.month % 12 + 1, day=1) - timedelta(days=1))
    
    # Calculate monthly totals
    monthly_income = db.session.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == TransactionType.INCOME,
        Transaction.date >= first_day,
        Transaction.date <= last_day
    ).scalar() or 0
    
    monthly_expenses = db.session.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == TransactionType.EXPENSE,
        Transaction.date >= first_day,
        Transaction.date <= last_day
    ).scalar() or 0
    
    monthly_savings = monthly_income - monthly_expenses
    
    # Get recent transactions
    recent_transactions = Transaction.query\
        .filter_by(user_id=current_user.id)\
        .order_by(Transaction.date.desc(), Transaction.created_at.desc())\
        .limit(10).all()
    
    # Get active savings goals
    savings_goals = SavingsGoal.query\
        .filter(
            SavingsGoal.user_id == current_user.id,
            or_(
                SavingsGoal.target_date >= today,
                SavingsGoal.is_completed == False
            )
        )\
        .order_by(SavingsGoal.target_date.asc())\
        .limit(3).all()
    
    # Calculate progress for each goal
    for goal in savings_goals:
        goal.saved_amount = goal.get_saved_amount()
        goal.progress = min(int((goal.saved_amount / goal.target_amount) * 100), 100)
    
    # Get spending by category
    spending_by_category = db.session.query(
        Transaction.category,
        func.sum(Transaction.amount).label('total_amount')
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == TransactionType.EXPENSE,
        Transaction.date >= first_day,
        Transaction.date <= last_day
    ).group_by(Transaction.category).order_by(func.sum(Transaction.amount).desc()).all()
    
    # Prepare data for charts
    categories = [category[0].value for category in spending_by_category]
    amounts = [float(amount[1]) for amount in spending_by_category]
    
    # Get monthly trend (last 6 months)
    monthly_trend = []
    for i in range(5, -1, -1):
        month_start = (today - timedelta(days=30*i)).replace(day=1)
        month_end = (month_start.replace(month=month_start.month % 12 + 1, day=1) - timedelta(days=1))
        
        monthly_expense = db.session.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
            Transaction.user_id == current_user.id,
            Transaction.transaction_type == TransactionType.EXPENSE,
            Transaction.date >= month_start,
            Transaction.date <= month_end
        ).scalar() or 0
        
        monthly_trend.append({
            'month': month_start.strftime('%b %Y'),
            'amount': float(monthly_expense)
        })
    
    return render_template('wallet/index.html',
                         monthly_income=monthly_income,
                         monthly_expenses=monthly_expenses,
                         monthly_savings=monthly_savings,
                         recent_transactions=recent_transactions,
                         savings_goals=savings_goals,
                         spending_categories=categories,
                         spending_amounts=amounts,
                         monthly_trend=monthly_trend)

# Transactions
@wallet.route('/transactions')
@login_required
def transactions():
    """Display all transactions with filtering and pagination."""
    # Get filter parameters
    transaction_type = request.args.get('type', 'all')
    category = request.args.get('category', 'all')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    search = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 15
    
    # Build query
    query = Transaction.query.filter_by(user_id=current_user.id)
    
    # Apply filters
    if transaction_type != 'all':
        query = query.filter(Transaction.transaction_type == transaction_type)
    
    if category != 'all':
        query = query.filter(Transaction.category == category)
    
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Transaction.date >= start_date)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Transaction.date <= end_date)
        except ValueError:
            pass
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Transaction.description.ilike(search_term),
                Transaction.notes.ilike(search_term)
            )
        )
    
    # Get paginated transactions
    transactions = query.order_by(
        Transaction.date.desc(),
        Transaction.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    # Get available categories for filter dropdown
    categories = db.session.query(Transaction.category)\
        .filter(Transaction.user_id == current_user.id)\
        .distinct()\
        .all()
    
    return render_template('wallet/transactions.html',
                         transactions=transactions,
                         transaction_type=transaction_type,
                         category=category,
                         start_date=start_date,
                         end_date=end_date,
                         search=search,
                         categories=[c[0] for c in categories])
