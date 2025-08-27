from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app
from .. import db, login_manager

class User(UserMixin, db.Model):
    """User account model."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    date_of_birth = db.Column(db.Date, nullable=False)
    join_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    xp_points = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    profile_image = db.Column(db.String(120), default='default.jpg')
    
    # Relationships
    habits = db.relationship('Habit', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    savings_goals = db.relationship('SavingsGoal', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    @property
    def password(self):
        """Prevent password from being accessed."""
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        """Set password to a hashed password."""
        self.password_hash = generate_password_hash(password)
    
    def set_password(self, password):
        """Set password to a hashed password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if hashed password matches actual password."""
        return check_password_hash(self.password_hash, password)
    
    def get_reset_token(self, expires_sec=1800):
        """Generate a password reset token."""
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')
    
    @staticmethod
    def verify_reset_token(token):
        """Verify the password reset token."""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)
    
    def add_xp(self, points):
        """Add XP points to the user and check for level up."""
        self.xp_points += points
        self.check_level_up()
        db.session.commit()
    
    def check_level_up(self):
        """Check if user has enough XP to level up."""
        xp_needed = self.level * 100  # Simple formula: 100 XP per level
        if self.xp_points >= xp_needed:
            self.level_up()
    
    def level_up(self):
        """Level up the user."""
        self.level += 1
        # You can add level-up rewards here
        # For example, unlock new features, give badges, etc.
        return self.level
    
    def get_age(self):
        """Calculate user's age based on date of birth."""
        today = datetime.now(timezone.utc).date()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
    
    def to_dict(self):
        """Convert user object to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'date_of_birth': self.date_of_birth.isoformat(),
            'join_date': self.join_date.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'xp_points': self.xp_points,
            'level': self.level,
            'profile_image': self.profile_image,
            'age': self.get_age()
        }

# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    """Flask-Login user loader callback."""
    return User.query.get(int(user_id))

# Anonymous user class for Flask-Login
class AnonymousUser:
    """Anonymous user class for Flask-Login."""
    def __init__(self):
        self.is_authenticated = False
        self.is_anonymous = True
        self.is_admin = False
    
    def get_id(self):
        return None

# Set the anonymous user class for Flask-Login
login_manager.anonymous_user = AnonymousUser
