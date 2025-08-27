from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, DateField, SelectField, TextAreaField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Optional, NumberRange, Length
from datetime import date, timedelta
from ..models.wallet import TransactionType, TransactionCategory

class TransactionForm(FlaskForm):
    """Form for adding/editing transactions."""
    amount = DecimalField('Amount', validators=[
        DataRequired(message='Amount is required'),
        NumberRange(min=0.01, message='Amount must be greater than zero')
    ], places=2)
    
    description = StringField('Description', validators=[
        DataRequired(message='Description is required'),
        Length(max=200, message='Description is too long (max 200 characters)')
    ])
    
    category = SelectField('Category', validators=[
        DataRequired(message='Category is required')
    ])
    
    transaction_type = SelectField('Type', 
        choices=[
            (TransactionType.INCOME.value, 'Income'),
            (TransactionType.EXPENSE.value, 'Expense')
        ],
        coerce=int,
        validators=[DataRequired()]
    )
    
    date = DateField('Date', 
        validators=[DataRequired()],
        default=date.today,
        format='%Y-%m-%d'
    )
    
    notes = TextAreaField('Notes', validators=[
        Optional(),
        Length(max=500, message='Notes are too long (max 500 characters)')
    ])
    
    submit = SubmitField('Save Transaction')
    
    def __init__(self, *args, **kwargs):
        super(TransactionForm, self).__init__(*args, **kwargs)
        # Set default category choices based on transaction type
        if self.transaction_type.data == TransactionType.INCOME.value:
            self.category.choices = [(c, c) for c in [
                'Allowance', 'Gift', 'Job', 'Freelance', 'Investment', 'Other Income'
            ]]
        else:
            self.category.choices = [(c, c) for c in [
                'Food & Dining', 'Shopping', 'Transportation', 'Bills & Utilities',
                'Entertainment', 'Health & Medical', 'Education', 'Gifts & Donations',
                'Personal Care', 'Travel', 'Groceries', 'Subscriptions', 'Other'
            ]]
    
    def validate(self, **kwargs):
        """Custom validation for the form."""
        if not super().validate():
            return False
            
        # Ensure amount is positive
        if self.amount.data <= 0:
            self.amount.errors.append('Amount must be greater than zero')
            return False
            
        return True


class SavingsGoalForm(FlaskForm):
    """Form for creating/editing savings goals."""
    name = StringField('Goal Name', validators=[
        DataRequired(message='Goal name is required'),
        Length(max=100, message='Goal name is too long (max 100 characters)')
    ])
    
    target_amount = DecimalField('Target Amount', validators=[
        DataRequired(message='Target amount is required'),
        NumberRange(min=0.01, message='Target amount must be greater than zero')
    ], places=2)
    
    target_date = DateField('Target Date', 
        validators=[DataRequired()],
        default=lambda: date.today() + timedelta(days=30),
        format='%Y-%m-%d'
    )
    
    description = TextAreaField('Description', validators=[
        Optional(),
        Length(max=500, message='Description is too long (max 500 characters)')
    ])
    
    submit = SubmitField('Save Goal')
    
    def validate(self, **kwargs):
        """Custom validation for the form."""
        if not super().validate():
            return False
            
        # Ensure target date is in the future
        if self.target_date.data <= date.today():
            self.target_date.errors.append('Target date must be in the future')
            return False
            
        return True


class TransferForm(FlaskForm):
    """Form for transferring money to savings goals."""
    amount = DecimalField('Amount', validators=[
        DataRequired(message='Amount is required'),
        NumberRange(min=0.01, message='Amount must be greater than zero')
    ], places=2)
    
    from_account = SelectField('From Account', 
        choices=[
            ('checking', 'Checking Account'),
            ('savings', 'Savings Account')
        ],
        default='checking',
        validators=[DataRequired()]
    )
    
    to_goal = SelectField('To Goal', 
        coerce=int,
        validators=[DataRequired()]
    )
    
    notes = TextAreaField('Notes', validators=[
        Optional(),
        Length(max=500, message='Notes are too long (max 500 characters)')
    ])
    
    submit = SubmitField('Transfer Money')


class BudgetForm(FlaskForm):
    """Form for setting up budget categories."""
    category = StringField('Category', validators=[
        DataRequired(message='Category name is required'),
        Length(max=100, message='Category name is too long (max 100 characters)')
    ])
    
    amount = DecimalField('Budgeted Amount', validators=[
        DataRequired(message='Amount is required'),
        NumberRange(min=0.01, message='Amount must be greater than zero')
    ], places=2)
    
    period = SelectField('Budget Period',
        choices=[
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('yearly', 'Yearly')
        ],
        default='monthly',
        validators=[DataRequired()]
    )
    
    submit = SubmitField('Set Budget')
    
    def validate(self, **kwargs):
        """Custom validation for the form."""
        if not super().validate():
            return False
            
        # Ensure amount is positive
        if self.amount.data <= 0:
            self.amount.errors.append('Amount must be greater than zero')
            return False
            
        return True
