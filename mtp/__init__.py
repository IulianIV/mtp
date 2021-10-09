import os
from flask import Flask
from mtp.db_manager.db import Config


__version__ = (1, 0, 0, "dev")


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object(Config)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.update(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from mtp.db_manager import db
    with app.app_context():
        db.init_app()

    # from . import auth, budget, mtp, dataflow
    # app.register_blueprint(auth.bp)
    # app.register_blueprint(mtp.bp)
    # app.register_blueprint(budget.bp)
    # app.register_blueprint(dataflow.bp)

    app.add_url_rule('/', endpoint='index')

    return app
