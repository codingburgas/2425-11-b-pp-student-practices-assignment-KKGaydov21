"""
User model for authentication and profile management
"""
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from ..app import db


class User(UserMixin, db.Model):
    """User model for storing user account information."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(100), nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    last_assessment = db.Column(db.DateTime, nullable=True)
    
    # Statistics
    total_assessments = db.Column(db.Integer, default=0, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relationships
    assessments = db.relationship('Assessment', backref='user', lazy='dynamic', 
                                cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set user password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash."""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Update last login timestamp."""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def increment_assessments(self):
        """Increment total assessments count."""
        self.total_assessments += 1
        self.last_assessment = datetime.utcnow()
        db.session.commit()
    
    def get_recent_assessments(self, limit=10):
        """Get user's recent assessments."""
        return self.assessments.order_by(
            db.desc('timestamp')
        ).limit(limit).all()
    
    def get_risk_distribution(self):
        """Get distribution of risk levels for user."""
        from ..models.assessment import Assessment
        return db.session.query(
            Assessment.risk_level,
            db.func.count(Assessment.id).label('count')
        ).filter_by(user_id=self.id).group_by(Assessment.risk_level).all()
    
    def to_dict(self):
        """Convert user to dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'created_at': self.created_at.isoformat(),
            'total_assessments': self.total_assessments,
            'last_assessment': self.last_assessment.isoformat() if self.last_assessment else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>'