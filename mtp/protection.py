from flask import Flask, flash
from flask_wtf import CSRFProtect
from wtforms.validators import ValidationError
from datetime import datetime
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


class NoFutureDates(object):
    def __init__(self, message=None):
        if not message:
            message = 'The date is not correct.'
        self.message = message

    def __call__(self, form, field):
        date = field.data
        present_time = datetime.now()

        input_date_str = date.strftime('%Y-%m-%d')
        input_date_datetime = datetime.strptime(input_date_str, '%Y-%m-%d')

        if input_date_datetime > present_time:
            raise ValidationError(form_error_message(self.message))


class CheckForNumber(object):

    def __init__(self, message=None):
        if not message:
            message = 'Value must be a number'
        self.message = message

    def __call__(self, form, field):

        value = field.data

        try:
            value_to_int = int(value)
        except ValueError:
            self.message = 'Value must be a number. Can not import text.'
            raise ValidationError(form_error_message(self.message))
