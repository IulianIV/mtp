import os
import secrets
from datetime import datetime

from flask import Flask, flash
from wtforms.validators import ValidationError

from app import Config

app_endpoints = {
    'revenue_entry_endpoint': 'budget.add_revenue_entry',
    'expense_entry_endpoint': 'budget.add_expense_entry',
    'savings_entry_endpoint': 'budget.add_savings_entry',
    'validation_endpoint': 'budget.validation',
    'utilities_entry_endpoint': 'budget.add_utilities_entry',
    'blog_index': 'blog.index',
    'login': 'auth.login'
}

ALLOWED_EXTENSIONS = {'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and filename.split('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def delete_post_image(image_name):
    root_path = Config.POST_IMAGE_UPLOAD_PATH
    post_image_path = os.path.join(root_path, image_name)

    os.remove(post_image_path)

    if os.path.exists(post_image_path):
        return "Image deletion failed."
    else:
        return "Image successfully removed."


def post_image_rename(image_uuid):
    image_name = image_uuid
    image_extension = '.jpg'

    renamed_image = image_name + image_extension

    return renamed_image



class CustomCSRF:

    def __init__(self):

        app = Flask(__name__)

        app.config['SECRET_KEY'] = f'{secrets.token_hex(16)}'


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


def check_range(ranged_faker_func):

    def wrapper(*args):
        range_nums = args[0].split('-')

        if int(range_nums[0]) >= int(range_nums[1]):
            form_error_message(f'Given range {args[0]} must '
                               f'evaluate to an ascending positive integer range (e.g. 1-5). ')
        else:
            print('they are good', 'test 2 after validty check')
            print(args[0], 'arguments print good, decorator')
            return ranged_faker_func(args[0])

    return wrapper


# Used in api/routes to transform a specific database query into a JSON file
def expense_count_to_json(data_list: list) -> dict:
    items_data = []

    count = [int(x[0]) for x in data_list]
    items = [x[1] for x in data_list]

    for item in range(len(items)):
        items_data.append({'group': '{}'.format(items[item]), 'value': '{}'.format(count[item])})

    return {
        'data': items_data
    }
