import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = 'dev'
    FLASK_APP = 'mtp'
    FLASK_ENV = 'development'
    os.environ['FLASK_APP'] = FLASK_APP
    os.environ['FLASK_ENV'] = FLASK_ENV
    DEBUG = True

    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    #     'sqlite:///' + os.path.join(os.path.join(os.path.join(basedir, os.pardir), os.pardir), r'\instance\app.db')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG_TB_PROFILER_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False


