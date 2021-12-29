import functools

from flask import (
    redirect, render_template, url_for
)
from flask_login import login_user, current_user, logout_user

from app.auth import bp
from app.auth.forms import LoginForm, RegisterForm
from app.manager.db.db_interrogations import *
from app.manager.protection import form_validated_message, form_error_message


# better-me handle situation when user already exists

db_insert = Insert()


@bp.route('/register', methods=('GET', 'POST'))
def register():

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    register_form = RegisterForm()

    if register_form.is_submitted():

        username = register_form.username.data
        password = register_form.password.data
        password_retype = register_form.password_retype.data
        email = register_form.email.data

        if password == password_retype:
            form_validated_message(f'User {username} has been registered. Please log in to continue')

            db_insert.insert_user(username, email, password)
            db.session.commit()

            return redirect(url_for('index'))
        else:
            form_error_message(f'Passwords must be identical.')
            return redirect(url_for('auth.register'))

    return render_template('auth/register.html', register_form=register_form)


# better-me improve the login functionality
@bp.route('/login', methods=('GET', 'POST'))
def login():

    if current_user.is_authenticated:
        return redirect(url_for('/'))

    login_form = LoginForm()

    username = login_form.username.data
    password = login_form.password.data
    remember_me = login_form.remember_me.data

    if login_form.is_submitted() and login_form.validate_on_submit():

        user = User.query.filter_by(username=username).first()

        if user is None or not user.check_password(password):
            form_error_message('Invalid username or password')
            return render_template('auth/login.html', login_form=login_form)
        else:
            if remember_me:
                form_validated_message(f'{username} is now logged in. {username} will be remembered')
            else:
                form_validated_message(f'{username} is now logged in. {username} is not set up for remember')

        login_user(user, remember=remember_me)

        return redirect(url_for('index'))

    return render_template('auth/login.html', login_form=login_form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if User.query.all() is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

