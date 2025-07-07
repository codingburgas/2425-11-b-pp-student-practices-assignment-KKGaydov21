"""
Custom validators for forms and data validation
"""
from wtforms.validators import ValidationError
import re


class StrongPassword:
    """Validator for strong password requirements."""
    
    def __init__(self, message=None):
        if not message:
            message = ('Password must contain at least 8 characters with '
                      'uppercase, lowercase, number, and special character.')
        self.message = message
    
    def __call__(self, form, field):
        password = field.data
        
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        
        if not re.search(r'[A-Z]', password):
            raise ValidationError('Password must contain at least one uppercase letter.')
        
        if not re.search(r'[a-z]', password):
            raise ValidationError('Password must contain at least one lowercase letter.')
        
        if not re.search(r'\d', password):
            raise ValidationError('Password must contain at least one number.')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError('Password must contain at least one special character.')


class MedicalRange:
    """Validator for medical measurement ranges."""
    
    def __init__(self, min_val, max_val, message=None):
        self.min_val = min_val
        self.max_val = max_val
        if not message:
            message = f'Value must be between {min_val} and {max_val}.'
        self.message = message
    
    def __call__(self, form, field):
        if field.data is None:
            return
        
        if not (self.min_val <= field.data <= self.max_val):
            raise ValidationError(self.message)


class UniqueField:
    """Validator to check field uniqueness in database."""
    
    def __init__(self, model, field_name, message=None):
        self.model = model
        self.field_name = field_name
        if not message:
            message = f'{field_name.title()} already exists.'
        self.message = message
    
    def __call__(self, form, field):
        existing = self.model.query.filter(
            getattr(self.model, self.field_name) == field.data
        ).first()
        
        if existing:
            raise ValidationError(self.message)


def validate_username(username):
    """Validate username format."""
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    
    if len(username) > 64:
        return False, "Username must be less than 64 characters"
    
    if not re.match(r'^[a-zA-Z0-9_.-]+$', username):
        return False, "Username can only contain letters, numbers, dots, hyphens, and underscores"
    
    return True, "Valid username"


def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    if len(email) > 120:
        return False, "Email must be less than 120 characters"
    
    return True, "Valid email"


def validate_medical_measurements(measurements):
    """Validate all medical measurements at once."""
    ranges = {
        'radius_mean': (6.0, 30.0),
        'texture_mean': (9.0, 40.0),
        'perimeter_mean': (40.0, 200.0),
        'area_mean': (140.0, 2500.0),
        'concave_points_mean': (0.0, 0.2),
        'symmetry_mean': (0.1, 0.3)
    }
    
    errors = []
    
    for field, value in measurements.items():
        if field in ranges:
            min_val, max_val = ranges[field]
            if not (min_val <= value <= max_val):
                errors.append(f"{field.replace('_', ' ').title()} must be between {min_val} and {max_val}")
    
    return len(errors) == 0, errors