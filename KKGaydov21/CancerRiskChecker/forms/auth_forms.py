"""
Authentication forms for login, registration, and user management
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from ..utils.validators import StrongPassword, UniqueField, validate_username, validate_email


class LoginForm(FlaskForm):
    """User login form."""
    username = StringField(
        'Username or Email', 
        validators=[DataRequired(), Length(min=3, max=64)],
        render_kw={'placeholder': 'Enter your username or email'}
    )
    password = PasswordField(
        'Password', 
        validators=[DataRequired()],
        render_kw={'placeholder': 'Enter your password'}
    )
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    """User registration form."""
    username = StringField(
        'Username', 
        validators=[DataRequired(), Length(min=3, max=64)],
        render_kw={'placeholder': 'Choose a unique username'}
    )
    email = EmailField(
        'Email', 
        validators=[DataRequired(), Email()],
        render_kw={'placeholder': 'your.email@example.com'}
    )
    full_name = StringField(
        'Full Name', 
        validators=[Length(max=100)],
        render_kw={'placeholder': 'Your full name (optional)'}
    )
    password = PasswordField(
        'Password', 
        validators=[DataRequired(), Length(min=8), StrongPassword()],
        render_kw={'placeholder': 'Create a strong password'}
    )
    password2 = PasswordField(
        'Confirm Password', 
        validators=[
            DataRequired(), 
            EqualTo('password', message='Passwords must match')
        ],
        render_kw={'placeholder': 'Confirm your password'}
    )
    terms_accepted = BooleanField(
        'I accept the terms and conditions',
        validators=[DataRequired(message='You must accept the terms and conditions')]
    )
    submit = SubmitField('Create Account')

    def validate_username(self, username):
        """Validate username format and uniqueness."""
        # Check format
        is_valid, message = validate_username(username.data)
        if not is_valid:
            raise ValidationError(message)
        
        # Check uniqueness
        from ..models.user import User
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')

    def validate_email(self, email):
        """Validate email format and uniqueness."""
        # Check format
        is_valid, message = validate_email(email.data)
        if not is_valid:
            raise ValidationError(message)
        
        # Check uniqueness
        from ..models.user import User
        user = User.query.filter_by(email=email.data.lower()).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email.')


class ChangePasswordForm(FlaskForm):
    """Change password form."""
    current_password = PasswordField(
        'Current Password',
        validators=[DataRequired()],
        render_kw={'placeholder': 'Enter your current password'}
    )
    new_password = PasswordField(
        'New Password',
        validators=[DataRequired(), Length(min=8), StrongPassword()],
        render_kw={'placeholder': 'Enter new password'}
    )
    confirm_password = PasswordField(
        'Confirm New Password',
        validators=[
            DataRequired(),
            EqualTo('new_password', message='Passwords must match')
        ],
        render_kw={'placeholder': 'Confirm new password'}
    )
    submit = SubmitField('Change Password')


class ForgotPasswordForm(FlaskForm):
    """Forgot password form."""
    email = EmailField(
        'Email',
        validators=[DataRequired(), Email()],
        render_kw={'placeholder': 'Enter your email address'}
    )
    submit = SubmitField('Reset Password')

    def validate_email(self, email):
        """Validate that email exists in system."""
        from ..models.user import User
        user = User.query.filter_by(email=email.data.lower()).first()
        if not user:
            raise ValidationError('No account found with that email address.')


class ResetPasswordForm(FlaskForm):
    """Reset password form (with token)."""
    password = PasswordField(
        'New Password',
        validators=[DataRequired(), Length(min=8), StrongPassword()],
        render_kw={'placeholder': 'Enter new password'}
    )
    password2 = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(),
            EqualTo('password', message='Passwords must match')
        ],
        render_kw={'placeholder': 'Confirm new password'}
    )
    submit = SubmitField('Reset Password')


class ProfileUpdateForm(FlaskForm):
    """User profile update form."""
    username = StringField(
        'Username',
        validators=[DataRequired(), Length(min=3, max=64)],
        render_kw={'placeholder': 'Username'}
    )
    email = EmailField(
        'Email',
        validators=[DataRequired(), Email()],
        render_kw={'placeholder': 'Email address'}
    )
    full_name = StringField(
        'Full Name',
        validators=[Length(max=100)],
        render_kw={'placeholder': 'Full name'}
    )
    submit = SubmitField('Update Profile')

    def __init__(self, original_username, original_email, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, username):
        """Validate username if changed."""
        if username.data != self.original_username:
            is_valid, message = validate_username(username.data)
            if not is_valid:
                raise ValidationError(message)
            
            from ..models.user import User
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username already exists.')

    def validate_email(self, email):
        """Validate email if changed."""
        if email.data.lower() != self.original_email.lower():
            is_valid, message = validate_email(email.data)
            if not is_valid:
                raise ValidationError(message)
            
            from ..models.user import User
            user = User.query.filter_by(email=email.data.lower()).first()
            if user:
                raise ValidationError('Email already registered.')