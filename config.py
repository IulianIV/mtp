import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = 'dev'
    FLASK_APP = 'mtp'
    FLASK_ENV = 'development'
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:admin@localhost/mtp'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG_TB_PROFILER_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False


