"""
Assessment forms for cancer risk evaluation
"""
from flask_wtf import FlaskForm
from wtforms import FloatField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, NumberRange, Optional
from ..utils.validators import MedicalRange


class AssessmentForm(FlaskForm):
    """Cancer risk assessment form with 6 simplified inputs."""
    
    radius_mean = FloatField(
        'Radius (Mean)',
        validators=[
            DataRequired(message='Radius measurement is required'),
            MedicalRange(6.0, 30.0, 'Radius must be between 6.0 and 30.0 mm')
        ],
        render_kw={
            'placeholder': 'e.g., 14.5',
            'step': '0.1',
            'min': '6.0',
            'max': '30.0'
        }
    )
    
    texture_mean = FloatField(
        'Texture (Mean)',
        validators=[
            DataRequired(message='Texture measurement is required'),
            MedicalRange(9.0, 40.0, 'Texture must be between 9.0 and 40.0 units')
        ],
        render_kw={
            'placeholder': 'e.g., 19.2',
            'step': '0.1',
            'min': '9.0',
            'max': '40.0'
        }
    )
    
    perimeter_mean = FloatField(
        'Perimeter (Mean)',
        validators=[
            DataRequired(message='Perimeter measurement is required'),
            MedicalRange(40.0, 200.0, 'Perimeter must be between 40.0 and 200.0 mm')
        ],
        render_kw={
            'placeholder': 'e.g., 95.3',
            'step': '0.1',
            'min': '40.0',
            'max': '200.0'
        }
    )
    
    area_mean = FloatField(
        'Area (Mean)',
        validators=[
            DataRequired(message='Area measurement is required'),
            MedicalRange(140.0, 2500.0, 'Area must be between 140.0 and 2500.0 mm²')
        ],
        render_kw={
            'placeholder': 'e.g., 654.7',
            'step': '0.1',
            'min': '140.0',
            'max': '2500.0'
        }
    )
    
    concave_points_mean = FloatField(
        'Concave Points (Mean)',
        validators=[
            DataRequired(message='Concave points measurement is required'),
            MedicalRange(0.0, 0.2, 'Concave points must be between 0.0 and 0.2')
        ],
        render_kw={
            'placeholder': 'e.g., 0.05',
            'step': '0.001',
            'min': '0.0',
            'max': '0.2'
        }
    )
    
    symmetry_mean = FloatField(
        'Symmetry (Mean)',
        validators=[
            DataRequired(message='Symmetry measurement is required'),
            MedicalRange(0.1, 0.3, 'Symmetry must be between 0.1 and 0.3')
        ],
        render_kw={
            'placeholder': 'e.g., 0.18',
            'step': '0.001',
            'min': '0.1',
            'max': '0.3'
        }
    )
    
    notes = TextAreaField(
        'Additional Notes (Optional)',
        validators=[Optional()],
        render_kw={
            'placeholder': 'Any additional medical notes or observations...',
            'rows': 3
        }
    )
    
    submit = SubmitField('Assess Risk')


class QuickAssessmentForm(FlaskForm):
    """Simplified quick assessment form with fewer validations."""
    
    radius_mean = FloatField(
        'Radius',
        validators=[DataRequired(), NumberRange(min=6.0, max=30.0)],
        render_kw={'placeholder': '14.5', 'step': '0.1'}
    )
    
    texture_mean = FloatField(
        'Texture',
        validators=[DataRequired(), NumberRange(min=9.0, max=40.0)],
        render_kw={'placeholder': '19.2', 'step': '0.1'}
    )
    
    perimeter_mean = FloatField(
        'Perimeter',
        validators=[DataRequired(), NumberRange(min=40.0, max=200.0)],
        render_kw={'placeholder': '95.3', 'step': '0.1'}
    )
    
    area_mean = FloatField(
        'Area',
        validators=[DataRequired(), NumberRange(min=140.0, max=2500.0)],
        render_kw={'placeholder': '654.7', 'step': '0.1'}
    )
    
    concave_points_mean = FloatField(
        'Concave Points',
        validators=[DataRequired(), NumberRange(min=0.0, max=0.2)],
        render_kw={'placeholder': '0.05', 'step': '0.001'}
    )
    
    symmetry_mean = FloatField(
        'Symmetry',
        validators=[DataRequired(), NumberRange(min=0.1, max=0.3)],
        render_kw={'placeholder': '0.18', 'step': '0.001'}
    )
    
    submit = SubmitField('Quick Assess')


class BulkAssessmentForm(FlaskForm):
    """Form for bulk assessment uploads (CSV)."""
    
    csv_data = TextAreaField(
        'CSV Data',
        validators=[DataRequired(message='CSV data is required')],
        render_kw={
            'placeholder': 'radius_mean,texture_mean,perimeter_mean,area_mean,concave_points_mean,symmetry_mean\n14.5,19.2,95.3,654.7,0.05,0.18\n...',
            'rows': 10
        }
    )
    
    submit = SubmitField('Process Bulk Assessment')


class AssessmentFilterForm(FlaskForm):
    """Form for filtering assessment history."""
    
    risk_level = FloatField(
        'Risk Level',
        validators=[Optional()],
        render_kw={'placeholder': 'Filter by risk level'}
    )
    
    date_from = FloatField(
        'From Date',
        validators=[Optional()],
        render_kw={'type': 'date'}
    )
    
    date_to = FloatField(
        'To Date',
        validators=[Optional()],
        render_kw={'type': 'date'}
    )
    
    submit = SubmitField('Apply Filters')