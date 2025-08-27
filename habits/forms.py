from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SelectMultipleField, IntegerField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from wtforms.widgets import CheckboxInput, ListWidget
from datetime import datetime, timedelta

from ..models.habit import Frequency

# Custom widget for multiple checkboxes
class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class HabitForm(FlaskForm):
    """Form for creating and editing habits."""
    name = StringField('Habit Name', validators=[
        DataRequired(message='Habit name is required'),
        Length(max=100, message='Habit name is too long (max 100 characters)')
    ])
    
    description = TextAreaField('Description', validators=[
        Length(max=500, message='Description is too long (max 500 characters)'),
        Optional()
    ])
    
    frequency = SelectField('Frequency', 
        choices=[
            (Frequency.DAILY.value, 'Daily'),
            (Frequency.WEEKLY.value, 'Weekly'),
            (Frequency.MONTHLY.value, 'Monthly'),
            (Frequency.CUSTOM.value, 'Custom')
        ],
        coerce=int,
        validators=[DataRequired()]
    )
    
    # Target days per week/month for frequency calculation
    target_days = IntegerField('Target Days', 
        validators=[
            NumberRange(min=1, max=31, message='Target days must be between 1 and 31'),
            Optional()
        ],
        default=1
    )
    
    # Weekly options (days of the week)
    weekly_days = MultiCheckboxField('Days of the Week',
        choices=[
            (0, 'Monday'),
            (1, 'Tuesday'),
            (2, 'Wednesday'),
            (3, 'Thursday'),
            (4, 'Friday'),
            (5, 'Saturday'),
            (6, 'Sunday')
        ],
        coerce=int,
        validators=[Optional()]
    )
    
    # Monthly options (days of the month)
    monthly_days = MultiCheckboxField('Days of the Month',
        choices=[(i, str(i)) for i in range(1, 32)],
        coerce=int,
        validators=[Optional()]
    )
    
    # Reminder settings
    enable_reminder = BooleanField('Enable Reminder', default=False)
    reminder_time = StringField('Reminder Time', 
        validators=[Optional()],
        render_kw={'type': 'time'}
    )
    
    # Streak goal (optional)
    streak_goal = IntegerField('Streak Goal (days)', 
        validators=[
            NumberRange(min=1, message='Streak goal must be at least 1 day'),
            Optional()
        ]
    )
    
    submit = SubmitField('Save Habit')
    
    def validate(self, **kwargs):
        """Custom validation for the form."""
        # Run standard validators
        if not super().validate():
            return False
        
        # Validate weekly days if frequency is weekly
        if self.frequency.data == Frequency.WEEKLY and not self.weekly_days.data:
            self.weekly_days.errors.append('Please select at least one day of the week')
            return False
        
        # Validate monthly days if frequency is monthly
        if self.frequency.data == Frequency.MONTHLY and not self.monthly_days.data:
            self.monthly_days.errors.append('Please select at least one day of the month')
            return False
        
        # Validate reminder time if enabled
        if self.enable_reminder.data and not self.reminder_time.data:
            self.reminder_time.errors.append('Please select a reminder time')
            return False
            
        return True


class HabitCompletionForm(FlaskForm):
    """Form for marking a habit as completed."""
    notes = TextAreaField('Notes', 
        validators=[
            Length(max=500, message='Notes are too long (max 500 characters)'),
            Optional()
        ]
    )
    
    rating = SelectField('How did it go?',
        choices=[
            (5, '😊 Great!'),
            (4, '🙂 Good'),
            (3, '😐 Okay'),
            (2, '😕 Hard'),
            (1, '😫 Very Hard')
        ],
        coerce=int,
        default=3
    )
    
    completion_date = StringField('Completion Date', 
        validators=[DataRequired()],
        default=datetime.now().strftime('%Y-%m-%d'),
        render_kw={'type': 'date'}
    )
    
    submit = SubmitField('Mark as Completed')


class HabitFilterForm(FlaskForm):
    """Form for filtering habits."""
    frequency = SelectField('Frequency',
        choices=[
            ('all', 'All Frequencies'),
            (Frequency.DAILY.value, 'Daily'),
            (Frequency.WEEKLY.value, 'Weekly'),
            (Frequency.MONTHLY.value, 'Monthly')
        ],
        default='all',
        coerce=str
    )
    
    status = SelectField('Status',
        choices=[
            ('all', 'All Statuses'),
            ('active', 'Active'),
            ('inactive', 'Inactive'),
            ('on_streak', 'On a Streak'),
            ('needs_attention', 'Needs Attention')
        ],
        default='active',
        coerce=str
    )
    
    sort_by = SelectField('Sort By',
        choices=[
            ('recent', 'Most Recent'),
            ('name', 'Name (A-Z)'),
            ('streak', 'Current Streak'),
            ('completion', 'Completion Rate')
        ],
        default='recent',
        coerce=str
    )
    
    submit = SubmitField('Apply Filters')
