from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from sqlalchemy import func, or_

from .. import db
from ..models.habit import Habit, HabitCompletion, Frequency
from ..models.user import User
from .forms import HabitForm, HabitCompletionForm

# Create blueprint
habits = Blueprint('habits', __name__)

@habits.route('/')
@login_required
def index():
    """Display all habits with their completion status for today."""
    today = date.today()
    
    # Get all active habits for the current user
    habits_list = Habit.query.filter_by(user_id=current_user.id, is_active=True).all()
    
    # Get today's completions
    completed_habit_ids = [
        hc.habit_id for hc in HabitCompletion.query
        .filter(
            HabitCompletion.completion_date == today,
            HabitCompletion.habit_id.in_([h.id for h in habits_list])
        )
    ]
    
    # Categorize habits
    daily_habits = [h for h in habits_list if h.frequency == Frequency.DAILY]
    weekly_habits = [h for h in habits_list if h.frequency == Frequency.WEEKLY and today.weekday() in h.weekly_days]
    monthly_habits = [h for h in habits_list if h.frequency == Frequency.MONTHLY and today.day in h.monthly_days]
    
    # Calculate streaks for each habit
    for habit in habits_list:
        habit.current_streak = habit.get_current_streak()
        habit.is_completed_today = habit.id in completed_habit_ids
    
    # Get habit statistics for the dashboard
    total_habits = len(habits_list)
    completed_today = len(completed_habit_ids)
    completion_rate = (completed_today / total_habits * 100) if total_habits > 0 else 0
    
    # Get the longest streak
    longest_streak = db.session.query(func.max(Habit.longest_streak))\
        .filter(Habit.user_id == current_user.id)\
        .scalar() or 0
    
    # Get the most consistent habit
    most_consistent_habit = Habit.query\
        .filter(Habit.user_id == current_user.id)\
        .order_by(Habit.longest_streak.desc())\
        .first()
    
    return render_template('habits/index.html',
                         daily_habits=daily_habits,
                         weekly_habits=weekly_habits,
                         monthly_habits=monthly_habits,
                         total_habits=total_habits,
                         completed_today=completed_today,
                         completion_rate=round(completion_rate, 1),
                         longest_streak=longest_streak,
                         most_consistent_habit=most_consistent_habit)

@habits.route('/new', methods=['GET', 'POST'])
@login_required
def new_habit():
    """Create a new habit."""
    form = HabitForm()
    
    if form.validate_on_submit():
        habit = Habit(
            name=form.name.data,
            description=form.description.data,
            frequency=form.frequency.data,
            target_days=form.target_days.data,
            user_id=current_user.id,
            created_at=datetime.utcnow(),
            is_active=True
        )
        
        # Set weekly or monthly days based on frequency
        if form.frequency.data == Frequency.WEEKLY and form.weekly_days.data:
            habit.weekly_days = form.weekly_days.data
        elif form.frequency.data == Frequency.MONTHLY and form.monthly_days.data:
            habit.monthly_days = form.monthly_days.data
        
        db.session.add(habit)
        db.session.commit()
        
        flash('Habit created successfully!', 'success')
        return redirect(url_for('habits.index'))
    
    return render_template('habits/new.html', form=form)

@habits.route('/<int:habit_id>')
@login_required
def view_habit(habit_id):
    """View details of a specific habit."""
    habit = Habit.query.get_or_404(habit_id)
    
    # Ensure the habit belongs to the current user
    if habit.user_id != current_user.id:
        abort(403)
    
    # Get completion history (last 30 days)
    thirty_days_ago = date.today() - timedelta(days=30)
    completions = HabitCompletion.query\
        .filter(
            HabitCompletion.habit_id == habit_id,
            HabitCompletion.completion_date >= thirty_days_ago
        )\
        .order_by(HabitCompletion.completion_date.desc())\
        .all()
    
    # Calculate completion rate
    total_days = (date.today() - thirty_days_ago).days + 1
    completion_rate = (len(completions) / total_days * 100) if total_days > 0 else 0
    
    # Prepare data for the calendar view
    calendar_data = {}
    for i in range(31):  # Last 30 days + today
        day = date.today() - timedelta(days=i)
        calendar_data[day] = any(c.completion_date == day for c in completions)
    
    return render_template('habits/view.html',
                         habit=habit,
                         completions=completions,
                         completion_rate=round(completion_rate, 1),
                         calendar_data=calendar_data)

@habits.route('/<int:habit_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_habit(habit_id):
    """Edit an existing habit."""
    habit = Habit.query.get_or_404(habit_id)
    
    # Ensure the habit belongs to the current user
    if habit.user_id != current_user.id:
        abort(403)
    
    form = HabitForm(obj=habit)
    
    if form.validate_on_submit():
        habit.name = form.name.data
        habit.description = form.description.data
        habit.frequency = form.frequency.data
        habit.target_days = form.target_days.data
        habit.updated_at = datetime.utcnow()
        
        # Update weekly or monthly days based on frequency
        if form.frequency.data == Frequency.WEEKLY:
            habit.weekly_days = form.weekly_days.data
            habit.monthly_days = []
        elif form.frequency.data == Frequency.MONTHLY:
            habit.monthly_days = form.monthly_days.data
            habit.weekly_days = []
        else:  # DAILY
            habit.weekly_days = []
            habit.monthly_days = []
        
        db.session.commit()
        flash('Habit updated successfully!', 'success')
        return redirect(url_for('habits.view_habit', habit_id=habit.id))
    
    # Pre-populate form with current values
    if request.method == 'GET':
        form.weekly_days.data = habit.weekly_days or []
        form.monthly_days.data = habit.monthly_days or []
    
    return render_template('habits/edit.html', form=form, habit=habit)

@habits.route('/<int:habit_id>/delete', methods=['POST'])
@login_required
def delete_habit(habit_id):
    """Delete a habit."""
    habit = Habit.query.get_or_404(habit_id)
    
    # Ensure the habit belongs to the current user
    if habit.user_id != current_user.id:
        abort(403)
    
    # Soft delete by marking as inactive
    habit.is_active = False
    habit.updated_at = datetime.utcnow()
    db.session.commit()
    
    flash('Habit deleted successfully!', 'success')
    return redirect(url_for('habits.index'))

@habits.route('/<int:habit_id>/complete', methods=['POST'])
@login_required
def complete_habit(habit_id):
    """Mark a habit as completed for today."""
    habit = Habit.query.get_or_404(habit_id)
    
    # Ensure the habit belongs to the current user
    if habit.user_id != current_user.id:
        abort(403)
    
    today = date.today()
    
    # Check if already completed today
    existing_completion = HabitCompletion.query.filter_by(
        habit_id=habit_id,
        completion_date=today
    ).first()
    
    if existing_completion:
        # Toggle completion status
        db.session.delete(existing_completion)
        message = 'Habit marked as not completed for today.'
        completed = False
    else:
        # Add new completion
        completion = HabitCompletion(
            habit_id=habit_id,
            completion_date=today,
            created_at=datetime.utcnow()
        )
        db.session.add(completion)
        message = 'Habit completed for today!'
        completed = True
        
        # Add XP points for completing a habit
        current_user.add_xp(10)  # 10 XP per habit completion
    
    # Update streak
    habit.update_streak(completed)
    db.session.commit()
    
    if request.is_json:
        return jsonify({
            'status': 'success',
            'message': message,
            'completed': completed,
            'current_streak': habit.current_streak,
            'xp': current_user.xp_points,
            'level': current_user.level
        })
    
    flash(message, 'success')
    return redirect(url_for('habits.index'))

@habits.route('/api/stats')
@login_required
def get_habits_stats():
    """Get habit statistics for the dashboard."""
    # Get completion data for the last 7 days
    seven_days_ago = date.today() - timedelta(days=6)
    
    # Get active habits count
    active_habits = Habit.query.filter_by(user_id=current_user.id, is_active=True).count()
    
    # Get completion data
    completion_data = {}
    for i in range(7):
        day = date.today() - timedelta(days=i)
        completion_data[day.strftime('%a')] = 0
    
    # Get completions for the last 7 days
    completions = db.session.query(
        func.date(HabitCompletion.completion_date).label('date'),
        func.count(HabitCompletion.id).label('count')
    ).join(Habit, Habit.id == HabitCompletion.habit_id)\
    .filter(
        Habit.user_id == current_user.id,
        HabitCompletion.completion_date >= seven_days_ago
    ).group_by('date').all()
    
    # Update completion data with actual values
    for date_str, count in completions:
        day_name = date_str.strftime('%a')
        completion_data[day_name] = count
    
    # Get the most consistent habit
    most_consistent_habit = Habit.query\
        .filter(Habit.user_id == current_user.id)\
        .order_by(Habit.longest_streak.desc())\
        .first()
    
    # Get the most missed habit
    most_missed_habit = Habit.query\
        .filter(Habit.user_id == current_user.id)\
        .order_by(Habit.missed_days.desc())\
        .first()
    
    return jsonify({
        'active_habits': active_habits,
        'completion_data': completion_data,
        'most_consistent_habit': {
            'name': most_consistent_habit.name if most_consistent_habit else None,
            'streak': most_consistent_habit.longest_streak if most_consistent_habit else 0
        },
        'most_missed_habit': {
            'name': most_missed_habit.name if most_missed_habit else None,
            'missed_days': most_missed_habit.missed_days if most_missed_habit else 0
        }
    })
