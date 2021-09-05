from flask import Flask, flash
from flask_wtf import CSRFProtect
import secrets


class CustomCSRF:

    def __init__(self):

        app = Flask(__name__)

        app.config['SECRET_KEY'] = f'{secrets.token_hex(16)}'

        csrf_token = CSRFProtect(app)


def form_validated_message(validation_msg, category='validated'):
    return flash(validation_msg, category)


def form_error_message(error_msg, category='error'):
    return flash(error_msg, category)

