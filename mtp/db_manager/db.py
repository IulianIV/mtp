from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from flask.cli import with_appcontext
from flask_migrate import Migrate
import os
import click


basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = 'dev'

    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    #     'sqlite:///' + os.path.join(os.path.join(os.path.join(basedir, os.pardir), os.pardir), r'\instance\app.db')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


def init_app():

    db = SQLAlchemy(current_app)
    migrate = Migrate(current_app, db)

    current_app.cli.add_command(init_db_command)

    return db


def get_db():

    database = init_app()

    return database


def init_db():

    db_init = init_app()

    from mtp.db_manager.models import User

    db_init.create_all()

    return db_init


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')
#
#
# def init_app(app):
#     app.cli.add_command(init_db_command)
