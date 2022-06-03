import os

import click
from flask import Flask
from flask import current_app
from flask.cli import with_appcontext
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

__version__ = (1, 1, 0, "dev")

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
toolbar = DebugToolbarExtension()

# better-me Add a way to switch databases (switch from production to testing)
#   think about how to version a test db.
# TODO Upon choosing a test database, a initialization will autofill with fake data.
# TODO Fix this CLI implementation confusion.

"""
 there seems to be some confusion on how CLI are implemented.
@click.command() coupled with @with_appcontext is for situation when the flask.cli built-in method is not used.
@blueprint_name.cli.command() is the flask.cli built-in method.
Which is better, why does the latter work only if implemented by the formers method?

details: https://flask.palletsprojects.com/en/2.0.x/cli/#custom-commands

"""
# TODO add a password reset form and password request form.
# TODO have password fields be checked as is and when hashed.
# TODO add UTM module from README.md
# TODO Create user profile view
# fixme Validation items should only be editable by an ADMIN or at least make sure that
#   what should be unique stays unique
# better-me Check coupling among all apps. There should be as little as possible functions with responsibilities outside
#   their set scope.
# TODO check what happens when URLs such as Update/Delete are accessed without an account and protect those views.
# TODO add at template return level fail safe "or_404" functionality.
# TODO Add Logging, Error Logging, Error Handlers, Exception Handlers and Custom Error Pages
#   see: https://flask.palletsprojects.com/en/2.0.x/errorhandling/
# TODO Split JS scripts and only add them where needed.
#   e.g.: the Blog view does not need to load the d3.js script
# TODO add a script that checks if the images from the uploads/post/ folder are found in the database.
#   if not found delete.
# TODO add more validation to image upload:
#   Max Files size, max resolution, only certain file types. resize image on upload.


def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    app.cli.add_command(init_db_command)

    # Start of possibly not efficient CLI implementation
    app.cli.add_command(fake_generator.cli_create_fake_users)
    app.cli.add_command(fake_generator.cli_create_fake_validation)
    app.cli.add_command(fake_generator.cli_create_fake_posts)
    app.cli.add_command(fake_generator.cli_create_fake_saving)
    app.cli.add_command(fake_generator.cli_create_fake_validation)
    app.cli.add_command(fake_generator.cli_create_fake_expense)
    app.cli.add_command(fake_generator.cli_create_fake_revenue)
    app.cli.add_command(fake_generator.cli_create_fake_utilities)
    app.cli.add_command(fake_generator.cli_create_fake_urls)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    toolbar.init_app(app)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        # app.config.from_pyfile("config.py", silent=True)
        app.config.from_object(Config)
    else:
        # load the test config if passed in
        app.config.update(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.blog import bp as blog_bp
    app.register_blueprint(blog_bp)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp)

    from app.budget import bp as budget_bp
    app.register_blueprint(budget_bp)

    from app.seo import bp as seo_bp
    app.register_blueprint(seo_bp)

    from app.webtools import bp as webtools_bp
    app.register_blueprint(webtools_bp)

    from app.manager import tests_bp as manager_tests_bp
    app.register_blueprint(manager_tests_bp)

    from app.analytics import bp as analytics_bp
    app.register_blueprint(analytics_bp)

    app.add_url_rule('/', endpoint='index')

    return app


# better-me Add proper functionality to the db init command.
#   check for existence. if exists: do...?
@click.command('init-db')
@with_appcontext
def init_db_command():
    """Initialize and create new database."""
    init_db()
    click.echo('Initialized the database.')


@with_appcontext
def init_db():
    db_init = db.init_app(current_app)
    db.create_all()

    return db_init


from app.manager.db import models
from app.manager.tests import fake_generator