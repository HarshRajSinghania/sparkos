from app import db
from datetime import datetime, timedelta

class Habit(db.Model):
    __tablename__ = 'habits'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    frequency = db.Column(db.String(20), default='daily')  # daily, weekly, monthly
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_completed = db.Column(db.DateTime)
    
    # Relationship
    completions = db.relationship('HabitCompletion', backref='habit', lazy=True, cascade='all, delete-orphan')
    
    def add_completion(self):
        """Mark habit as completed for today"""
        today = datetime.utcnow().date()
        
        # Check if already completed today
        last_completion = HabitCompletion.query.filter_by(
            habit_id=self.id,
            completion_date=today
        ).first()
        
        if not last_completion:
            completion = HabitCompletion(
                habit_id=self.id,
                completion_date=today
            )
            db.session.add(completion)
            
            # Update streak
            self.last_completed = datetime.utcnow()
            self.current_streak += 1
            
            if self.current_streak > self.longest_streak:
                self.longest_streak = self.current_streak
                
            db.session.commit()
            return True
        return False

class HabitCompletion(db.Model):
    __tablename__ = 'habit_completions'
    
    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey('habits.id'), nullable=False)
    completion_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    
    __table_args__ = (
        db.UniqueConstraint('habit_id', 'completion_date', name='unique_habit_completion'),
    )
