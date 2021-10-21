import functools

from flask import (
    flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from app.manager.db.models import User
from app.auth import bp
from app.manager.db.models import *
from app.manager.protection import form_validated_message, form_error_message
from app.auth.forms import LoginForm
from flask_login import login_user


"""
Form catcher that adds entries to `user` database 

"""


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.order_by(User.query.filter_by(username=username).first()) is not None:
            error = f'User {username} is already registered.'

        if error is None:
            db.session.add(User(username=username, password=generate_password_hash(password)))
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')


"""
Login handling for 'user' database

"""


@bp.route('/login', methods=('GET', 'POST'))
def login():

    login_form = LoginForm()
    error = None

    if request.method == 'POST':

        if login_form.is_submitted() and login_form.validate_on_submit():
            username = login_form.username.data
            password = login_form.password.data
            remember_me = login_form.remember_me.data

            form_validated_message(f'Login requested for user {username}, remember_me={remember_me}')

            user = User.query.filter_by(username=username).first()

            login_user(user)

            # better-me Improve the way errors are shown with custom css or by implementing the card system
            if user is None:
                error = 'Incorrect username.'
            elif not check_password_hash(user.password, password):
                error = 'Incorrect password.'

            if error is None:
                session.clear()
                session['user_id'] = user.id
                return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html', login_form=login_form)


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get(f'User.query.all().first()')

    if user_id is None:
        user = None
    else:
        user = User.query.filter_by(id=user_id).first()

    return user


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if User.query.all() is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

