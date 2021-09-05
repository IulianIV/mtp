from flask import Flask
from flask_wtf import CSRFProtect
import secrets


class CustomCSRF:

    def __init__(self):

        app = Flask(__name__)

        app.config['SECRET_KEY'] = f'{secrets.token_hex(16)}'

        csrf_token = CSRFProtect(app)
