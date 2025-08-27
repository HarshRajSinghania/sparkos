from datetime import datetime, date
from enum import Enum
from .. import db
from sqlalchemy.ext.hybrid import hybrid_property

class TransactionType(Enum):
    """Enum for transaction types."""
    INCOME = 'income'
    EXPENSE = 'expense'
    TRANSFER = 'transfer'

class TransactionCategory(Enum):
    """Common transaction categories."""
    # Income categories
    ALLOWANCE = 'Allowance'
    GIFT = 'Gift'
    JOB = 'Job'
    FREELANCE = 'Freelance'
    INVESTMENT = 'Investment'
    OTHER_INCOME = 'Other Income'
    
    # Expense categories
    FOOD = 'Food & Dining'
    SHOPPING = 'Shopping'
    TRANSPORTATION = 'Transportation'
    BILLS = 'Bills & Utilities'
    ENTERTAINMENT = 'Entertainment'
    HEALTH = 'Health & Medical'
    EDUCATION = 'Education'
    GIFTS = 'Gifts & Donations'
    PERSONAL_CARE = 'Personal Care'
    TRAVEL = 'Travel'
    GROCERIES = 'Groceries'
    SUBSCRIPTIONS = 'Subscriptions'
    SAVINGS = 'Savings'
    OTHER = 'Other'

class Transaction(db.Model):
    """Transaction model for tracking income and expenses."""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    category = db.Column(db.Enum(TransactionCategory), nullable=False)
    transaction_type = db.Column(db.Enum(TransactionType), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    savings_goal_id = db.Column(db.Integer, db.ForeignKey('savings_goals.id'))
    savings_goal = db.relationship('SavingsGoal', back_populates='transactions')
    
    def __init__(self, **kwargs):
        super(Transaction, self).__init__(**kwargs)
        # Set default values
        if not self.created_at:
            self.created_at = datetime.utcnow()
    
    def __repr__(self):
        return f'<Transaction {self.id}: {self.amount} for {self.description}>'
    
    def to_dict(self):
        """Convert transaction to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'amount': float(self.amount) if self.amount else 0.0,
            'description': self.description,
            'category': self.category.value if self.category else None,
            'type': self.transaction_type.value if self.transaction_type else None,
            'date': self.date.isoformat() if self.date else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'savings_goal_id': self.savings_goal_id
        }
    
    @classmethod
    def get_monthly_summary(cls, user_id, year=None, month=None):
        """Get monthly summary of transactions."""
        if year is None or month is None:
            today = date.today()
            year, month = today.year, today.month
        
        first_day = date(year, month, 1)
        if month == 12:
            last_day = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(year, month + 1, 1) - timedelta(days=1)
        
        # Get total income and expenses for the month
        result = db.session.query(
            db.func.sum(
                db.case([(cls.transaction_type == TransactionType.INCOME, cls.amount)], else_=0)
            ).label('total_income'),
            db.func.sum(
                db.case([(cls.transaction_type == TransactionType.EXPENSE, cls.amount)], else_=0)
            ).label('total_expenses')
        ).filter(
            cls.user_id == user_id,
            cls.date.between(first_day, last_day)
        ).first()
        
        total_income = float(result[0]) if result[0] else 0.0
        total_expenses = float(result[1]) if result[1] else 0.0
        
        return {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'savings': total_income - total_expenses
        }


class SavingsGoal(db.Model):
    """Savings goal model for tracking financial goals."""
    __tablename__ = 'savings_goals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    target_amount = db.Column(db.Numeric(10, 2), nullable=False)
    target_date = db.Column(db.Date)
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    transactions = db.relationship('Transaction', back_populates='savings_goal')
    
    def __init__(self, **kwargs):
        super(SavingsGoal, self).__init__(**kwargs)
        if not self.created_at:
            self.created_at = datetime.utcnow()
    
    def __repr__(self):
        return f'<SavingsGoal {self.id}: {self.name}>'
    
    @hybrid_property
    def progress(self):
        """Calculate progress percentage towards the goal."""
        saved = self.get_saved_amount()
        if self.target_amount <= 0 or saved <= 0:
            return 0.0
        return min(100.0, (float(saved) / float(self.target_amount)) * 100.0)
    
    def get_saved_amount(self):
        """Calculate total saved amount from related transactions."""
        if not self.transactions:
            return 0.0
        
        total = sum(float(t.amount) for t in self.transactions)
        return total
    
    def add_transaction(self, amount, description, date=None, notes=None):
        """Add a new transaction to this savings goal."""
        if date is None:
            date = date.today()
            
        transaction = Transaction(
            user_id=self.user_id,
            amount=amount,
            description=description,
            category=TransactionCategory.SAVINGS,
            transaction_type=TransactionType.TRANSFER,
            date=date,
            notes=notes,
            savings_goal_id=self.id
        )
        
        db.session.add(transaction)
        
        # Check if goal is completed
        saved_amount = self.get_saved_amount() + float(amount)
        if not self.is_completed and saved_amount >= float(self.target_amount):
            self.is_completed = True
            self.completed_at = datetime.utcnow()
        
        return transaction
    
    def to_dict(self):
        """Convert savings goal to dictionary for JSON serialization."""
        saved_amount = self.get_saved_amount()
        
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'target_amount': float(self.target_amount) if self.target_amount else 0.0,
            'saved_amount': saved_amount,
            'target_date': self.target_date.isoformat() if self.target_date else None,
            'progress': self.progress,
            'is_completed': self.is_completed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'days_remaining': (self.target_date - date.today()).days if self.target_date and not self.is_completed else 0
        }
