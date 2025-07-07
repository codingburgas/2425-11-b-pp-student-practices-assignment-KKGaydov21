"""
Authentication blueprint for user login, registration, and logout
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from ..utils.helpers import flash_errors, log_user_activity
from ..utils.validators import StrongPassword, UniqueField, validate_username, validate_email



auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page and handler."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    from ..forms.auth_forms import LoginForm
    form = LoginForm()
    
    if form.validate_on_submit():
        from ..models.user import User
        
        # Check if username is email or username
        user = User.query.filter(
            (User.username == form.username.data) | (User.email == form.username.data)
        ).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            user.update_last_login()
            
            # Handle next page redirect
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('dashboard.index')
            
            log_user_activity('login', f'from {request.remote_addr}')
            flash('Login successful! Welcome back.', 'success')
            return redirect(next_page)
        else:
            flash('Invalid username or password. Please try again.', 'danger')
            log_user_activity('failed_login', f'username: {form.username.data}')
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page and handler."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    from ..forms.auth_forms import RegistrationForm
    from ..models.user import User
    from ..app import db
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        try:
            # Create new user
            user = User(
                username=form.username.data,
                email=form.email.data.lower(),
                full_name=form.full_name.data
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            log_user_activity('registration', f'new user: {user.username}')
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'danger')
            print(f"Registration error: {e}")
    
    return render_template('auth/register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout handler."""
    username = current_user.username
    logout_user()
    log_user_activity('logout', f'user: {username}')
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/profile')
@login_required
def profile():
    """User profile page."""
    return render_template('auth/profile.html', user=current_user)


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password page and handler."""
    from ..forms.auth_forms import ChangePasswordForm
    from ..app import db
    
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            log_user_activity('password_change', 'successful')
            flash('Password changed successfully!', 'success')
            return redirect(url_for('auth.profile'))
        else:
            flash('Current password is incorrect.', 'danger')
    
    return render_template('auth/change_password.html', form=form)