from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, FloatField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, ValidationError
from models import User


class LoginForm(FlaskForm):
    username = StringField('Username or Email', validators=[DataRequired(), Length(min=4, max=64)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    full_name = StringField('Full Name', validators=[Length(max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please choose a different one.')


class AssessmentForm(FlaskForm):
    radius_mean = FloatField('Radius (Mean)', validators=[
        DataRequired(), 
        NumberRange(min=6.0, max=30.0, message='Radius must be between 6.0 and 30.0')
    ])
    texture_mean = FloatField('Texture (Mean)', validators=[
        DataRequired(), 
        NumberRange(min=9.0, max=40.0, message='Texture must be between 9.0 and 40.0')
    ])
    perimeter_mean = FloatField('Perimeter (Mean)', validators=[
        DataRequired(), 
        NumberRange(min=40.0, max=200.0, message='Perimeter must be between 40.0 and 200.0')
    ])
    area_mean = FloatField('Area (Mean)', validators=[
        DataRequired(), 
        NumberRange(min=140.0, max=2500.0, message='Area must be between 140.0 and 2500.0')
    ])
    concave_points_mean = FloatField('Concave Points (Mean)', validators=[
        DataRequired(), 
        NumberRange(min=0.0, max=0.2, message='Concave Points must be between 0.0 and 0.2')
    ])
    symmetry_mean = FloatField('Symmetry (Mean)', validators=[
        DataRequired(), 
        NumberRange(min=0.1, max=0.3, message='Symmetry must be between 0.1 and 0.3')
    ])
    submit = SubmitField('Assess Risk')
