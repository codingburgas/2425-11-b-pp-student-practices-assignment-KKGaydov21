"""
Assessment model for storing cancer risk evaluations
"""
from datetime import datetime
from ..app import db


class Assessment(db.Model):
    """Assessment model for storing cancer risk evaluation data."""
    
    __tablename__ = 'assessments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Input features (6 simplified measurements)
    radius_mean = db.Column(db.Float, nullable=False)
    texture_mean = db.Column(db.Float, nullable=False)
    perimeter_mean = db.Column(db.Float, nullable=False)
    area_mean = db.Column(db.Float, nullable=False)
    concave_points_mean = db.Column(db.Float, nullable=False)
    symmetry_mean = db.Column(db.Float, nullable=False)
    
    # Prediction results
    prediction_probability = db.Column(db.Float, nullable=False)
    prediction_class = db.Column(db.Integer, nullable=False)  # 0 for benign, 1 for malignant
    risk_level = db.Column(db.String(20), nullable=False, index=True)  # Very Low, Low, Moderate, High
    
    # Additional metadata
    model_version = db.Column(db.String(50), default='1.0', nullable=False)
    processing_time = db.Column(db.Float, nullable=True)  # Time taken for prediction
    
    @property
    def features_as_list(self):
        """Return input features as a list."""
        return [
            self.radius_mean,
            self.texture_mean,
            self.perimeter_mean,
            self.area_mean,
            self.concave_points_mean,
            self.symmetry_mean
        ]
    
    @property
    def prediction_text(self):
        """Return human-readable prediction."""
        return 'Malignant' if self.prediction_class == 1 else 'Benign'
    
    @property
    def probability_percentage(self):
        """Return probability as percentage."""
        return round(self.prediction_probability * 100, 1)
    
    @property
    def risk_color(self):
        """Return Bootstrap color class for risk level."""
        risk_colors = {
            'Very Low': 'success',
            'Low': 'primary',
            'Moderate': 'warning',
            'High': 'danger'
        }
        return risk_colors.get(self.risk_level, 'secondary')
    
    def get_recommendations(self):
        """Get recommendations based on risk level."""
        recommendations = {
            'Very Low': {
                'message': 'The analysis suggests a very low probability of malignancy.',
                'advice': 'Continue regular health monitoring and follow your doctor\'s recommendations for routine screenings.',
                'urgency': 'routine'
            },
            'Low': {
                'message': 'The analysis suggests a low probability of malignancy.',
                'advice': 'Maintain regular check-ups and discuss these results with your healthcare provider.',
                'urgency': 'routine'
            },
            'Moderate': {
                'message': 'The analysis suggests a moderate probability of malignancy.',
                'advice': 'It is important to discuss these results with your healthcare provider for further evaluation and potential additional testing.',
                'urgency': 'follow-up'
            },
            'High': {
                'message': 'The analysis suggests a higher probability of malignancy.',
                'advice': 'Please consult with your healthcare provider immediately for comprehensive evaluation and appropriate medical intervention.',
                'urgency': 'immediate'
            }
        }
        return recommendations.get(self.risk_level, recommendations['Low'])
    
    def to_dict(self):
        """Convert assessment to dictionary."""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'features': {
                'radius_mean': self.radius_mean,
                'texture_mean': self.texture_mean,
                'perimeter_mean': self.perimeter_mean,
                'area_mean': self.area_mean,
                'concave_points_mean': self.concave_points_mean,
                'symmetry_mean': self.symmetry_mean
            },
            'prediction_probability': self.prediction_probability,
            'prediction_class': self.prediction_class,
            'prediction_text': self.prediction_text,
            'risk_level': self.risk_level,
            'probability_percentage': self.probability_percentage
        }
    
    @staticmethod
    def get_statistics():
        """Get platform-wide assessment statistics."""
        total = Assessment.query.count()
        malignant = Assessment.query.filter_by(prediction_class=1).count()
        benign = Assessment.query.filter_by(prediction_class=0).count()
        
        risk_distribution = db.session.query(
            Assessment.risk_level,
            db.func.count(Assessment.id).label('count')
        ).group_by(Assessment.risk_level).all()
        
        return {
            'total_assessments': total,
            'malignant_count': malignant,
            'benign_count': benign,
            'risk_distribution': {level: count for level, count in risk_distribution}
        }
    
    def __repr__(self):
        return f'<Assessment {self.id} - {self.risk_level} ({self.prediction_text})>'