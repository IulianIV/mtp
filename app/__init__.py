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

__version__ = (1, 0, 0, "dev")

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
toolbar = DebugToolbarExtension()

# better-me Add a way to switch databases (switch from production to testing)
#   think about how to version a test db.
# TODO Upon choosing a test database, a initialization will autofill with fake data.

def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    app.cli.add_command(init_db_command)

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

    # from app.dataflow import bp as dataflow_bp
    # app.register_blueprint(dataflow_bp)

    from app.webtools import bp as webtools_bp
    app.register_blueprint(webtools_bp)

    app.add_url_rule('/', endpoint='index')

    return app


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


@with_appcontext
def init_db():
    db_init = db.init_app(current_app)
    db.create_all()

    return db_init

# fixme Needs to be fixed. Issues a "No such command error"


@click.command('fake-validation')
@with_appcontext
def create_fake_validation_command():
    populate_fakes.create_fake_validation()
    click.echo('Created fake validation entries..')

from app.manager.db import models
from app.manager.tests import populate_fakes