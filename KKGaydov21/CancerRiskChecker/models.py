from app import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_assessment = db.Column(db.DateTime, nullable=True)
    total_assessments = db.Column(db.Integer, default=0)
    
    # Relationship to assessments
    assessments = db.relationship('Assessment', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Simplified input features (5-6 key measurements)
    radius_mean = db.Column(db.Float, nullable=False)
    texture_mean = db.Column(db.Float, nullable=False)
    perimeter_mean = db.Column(db.Float, nullable=False)
    area_mean = db.Column(db.Float, nullable=False)
    concave_points_mean = db.Column(db.Float, nullable=False)
    symmetry_mean = db.Column(db.Float, nullable=False)
    
    # Prediction results
    prediction_probability = db.Column(db.Float, nullable=False)
    prediction_class = db.Column(db.Integer, nullable=False)  # 0 for benign, 1 for malignant
    risk_level = db.Column(db.String(20), nullable=False)  # Very Low, Low, Moderate, High
    
    def __repr__(self):
        return f'<Assessment {self.id} - {self.risk_level}>'
