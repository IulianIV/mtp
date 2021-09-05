import os

from flask import Flask
from .db_manager import db
from . import auth, budget, mtp, dataflow
from flask_dropzone import Dropzone

dropzone = Dropzone()


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    dropzone.init_app(app)

    app.config.from_mapping(SECRET_KEY='dev', DATABASE=os.path.join(app.instance_path, 'mtp.sqlite'),)
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)

    app.register_blueprint(auth.bp)
    app.register_blueprint(mtp.bp)
    app.register_blueprint(budget.bp)
    app.register_blueprint(dataflow.bp)
    app.add_url_rule('/', endpoint='index')

    return app
