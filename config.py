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
    POST_IMAGE_UPLOAD_PATH = os.path.join(basedir, 'app\\uploads\\post\\')
    GTM_SPY_DOWNLOAD_PATH = os.path.join(basedir, 'app\\uploads\\gtm_scripts')

    '''
    PythonAnywhere Database Config
    
    They are to be added extra or in place of what is above.
    
    db_u = 'user'
    db_p = 'pass'
    db_h = 'maiels.mysql.pythonanywhere-services.com'
    db_d = 'mtpdb'
    
    SQLALCHEMY_DATABASE_URI = f'mysql+mysqlconnector://{db_u}:{db_p}@{db_h}/{db_d}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_RECYCLE = 299

    
    '''



