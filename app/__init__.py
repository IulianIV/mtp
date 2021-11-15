import click
from config import Config
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask.cli import with_appcontext
from flask import current_app
from flask_login import LoginManager


__version__ = (1, 0, 0, "dev")

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()


def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    app.cli.add_command(init_db_command)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

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

    # from app.budget import bp as budget_bp
    # app.register_blueprint(budget_bp)
    #
    # from app.dataflow import bp as dataflow_bp
    # app.register_blueprint(dataflow_bp)

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
    db_init.create_all()

    return db_init


from app.manager.db import models