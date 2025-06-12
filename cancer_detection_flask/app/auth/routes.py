from flask import Blueprint, render_template, redirect, url_for, flash, request
from app import db
from .forms import RegistrationForm, LoginForm
from ..models import User
from flask_login import login_user, logout_user, current_user, login_required

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.survey'))  # if already logged in, go to survey

    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already registered. Please log in or use another email.', 'warning')
            return redirect(url_for('auth.register'))
        user = User(
            username=form.username.data,
            email=form.email.data,
            role='user',
            allow_prediction_sharing=False
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully. Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.survey'))  # already logged in → survey page

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Logged in successfully!', 'success')
            # Redirect to next page if exists or survey page
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.survey'))
        else:
            flash('Invalid email or password', 'danger')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
