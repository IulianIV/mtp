import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.urandom(32)
    FLASK_APP = 'mtp'
    FLASK_ENV = 'development'
    DEBUG = False

    if basedir == '/home/maiels/mtp':

        SQLALCHEMY_DATABASE_URI = f'mysql+mysqlconnector://{db_u}:{db_p}@{db_h}/{db_d}'
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        SQLALCHEMY_POOL_RECYCLE = 299
        DEBUG_TB_PROFILER_ENABLED = True
        POST_IMAGE_UPLOAD_PATH = os.path.join(basedir, 'app/uploads/post/')
        GTM_SPY_DOWNLOAD_PATH = os.path.join(basedir, 'app/uploads/gtm_scripts/')

    else:

        SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:admin@localhost/mtp'
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        DEBUG_TB_PROFILER_ENABLED = True
        DEBUG_TB_INTERCEPT_REDIRECTS = False
        POST_IMAGE_UPLOAD_PATH = os.path.join(basedir, 'app\\uploads\\post\\')
        GTM_SPY_DOWNLOAD_PATH = os.path.join(basedir, r'app\uploads\gtm_scripts')

        DEBUG = True



