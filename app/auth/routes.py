import functools
from flask import (
   redirect, render_template, request, session, url_for
)
from flask_login import login_user, current_user, logout_user
from app.auth import bp
from app.auth.forms import LoginForm, RegisterForm
from app.manager.protection import form_validated_message, form_error_message
from app.manager.db.models import User
from app import db


# better-me handle situation when user already exists
# better-me handle situation when password != password_retype
# better-me handle logic for password and password retype matching
# better-me check the Register logic from Miguel Grinberg and implement

@bp.route('/register', methods=('GET', 'POST'))
def register():

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    register_form = RegisterForm()

    if register_form.is_submitted() and register_form.validate_on_submit():

        username = register_form.username.data
        password = register_form.password.data

        form_validated_message(f'Register requested for user {username}')

        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('index'))

    elif register_form.is_submitted() and register_form.validate_on_submit():
        form_error_message('Passwords must be identical.')

    return render_template('auth/register.html', register_form=register_form)


# better-me improve the login functionality
# better-me fix the log in
# better-me follow the Log In structure from Miguel Grinberg and implement it

@bp.route('/login', methods=('GET', 'POST'))
def login():

    if current_user.is_authenticated:
        return redirect(url_for('/'))

    login_form = LoginForm()

    username = login_form.username.data
    password = login_form.password.data
    remember_me = login_form.remember_me.data

    if login_form.is_submitted() and login_form.validate_on_submit():

        form_validated_message(f'Login requested for user {username}, remember_me={remember_me}')

        user = User.query.filter_by(username=username).first()

        if user is None or not user.check_password(password):
            form_error_message('Invalid username or password')
            return render_template('auth/login.html', login_form=login_form)

        login_user(user, remember=remember_me)

        return redirect(url_for('index'))

    elif not login_form.validate_on_submit():
        form_error_message('Error occurred.')

    # better-me Improve the way errors are shown with custom css or by implementing the card system

    return render_template('auth/login.html', login_form=login_form)


# better-me follow the Log In structure from Miguel Grinberg and implement it
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get(f'User.query.all().first()')

    if user_id is None:
        user = None
    else:
        user = User.query.filter_by(id=user_id).first()

    return user


# better-me follow the Log In structure from Miguel Grinberg and implement it
@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


# better-me follow the Log In structure from Miguel Grinberg and implement it
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if User.query.all() is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

