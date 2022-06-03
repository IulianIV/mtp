import functools

from flask import (
    redirect, render_template, url_for
)
from flask_login import login_user, current_user, logout_user

from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegisterForm
from app.manager.db.db_interrogations import check_existing_user, insert_user
from app.manager.db.models import User
from app.manager.helpers import form_validated_message, form_error_message, app_endpoints

login_endpoint = app_endpoints['login']


@bp.route('/register', methods=('GET', 'POST'))
def register():

    if current_user.is_authenticated:
        return redirect(url_for('index'))
    # temporary added in deployment version to remove ability to register
    else:
        return redirect(url_for('index'))

    register_form = RegisterForm()

    if register_form.is_submitted() and register_form.validate_on_submit():

        username = register_form.username.data
        password = register_form.password.data
        password_retype = register_form.password_retype.data
        email = register_form.email.data

        username_validity = check_existing_user(username)

        if password == password_retype and username_validity is None:
            form_validated_message(f'User {username} has been registered. Please log in to continue')

            insert_user(username, email, password)
            db.session.commit()

            return redirect(url_for('index'))

        elif password != password_retype and username_validity:
            form_error_message(f'Passwords must be identical. Username {username} already exists.')

            return redirect(url_for('auth.register'))
        else:
            form_error_message('Either password or username are incorrect.')

            return redirect(url_for('auth.register'))

    return render_template('auth/register.html', register_form=register_form)


@bp.route('/login', methods=('GET', 'POST'))
def login():

    if current_user.is_authenticated:
        form_error_message('You are already logged in.')
        return redirect(url_for('index'))

    login_form = LoginForm()

    username = login_form.username.data
    password = login_form.password.data
    remember_me = login_form.remember_me.data

    if login_form.is_submitted() and login_form.validate_on_submit():

        user = User.query.filter_by(username=username).first()

        if user is None or not user.check_password(password):
            form_error_message('Invalid username or password')
            return redirect(url_for(login_endpoint))
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
    return redirect(url_for(login_endpoint))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if User.query.all() is None:
            return redirect(url_for(login_endpoint))

        return view(**kwargs)

    return wrapped_view
