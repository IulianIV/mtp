import os
import secrets
from datetime import datetime
import re

from flask import Flask, flash, url_for
from wtforms.validators import ValidationError

from app import Config

# used across many routs. Greatly helps with code cohesion. This enables a way to male sure there are no duplicate
# constants across the application
app_endpoints = {
    'revenue_entry_endpoint': 'budget.add_revenue_entry',
    'expense_entry_endpoint': 'budget.add_expense_entry',
    'savings_entry_endpoint': 'budget.add_savings_entry',
    'recurrent_entry_endpoint': 'budget.recurrent_payments',
    'validation_endpoint': 'budget.validation',
    'utilities_entry_endpoint': 'budget.add_utilities_entry',
    'blog_index': 'blog.homepage',
    'login': 'auth.login'
}


# checks if the given filename has an extension found within the allowed filetypes.
def allowed_file(filename):
    return '.' in filename and filename.split('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


# handles deletion of images from the uploads' folder on post deletion
def delete_post_image(image_name):
    root_path = Config.POST_IMAGE_UPLOAD_PATH
    post_image_path = os.path.join(root_path, image_name)

    os.remove(post_image_path)

    if os.path.exists(post_image_path):
        return "Image deletion failed."
    else:
        return "Image successfully removed."


# needed to rename images that are uploaded via dropzone.js
def post_image_rename(image_uuid):
    image_name = image_uuid
    image_extension = '.jpg'

    renamed_image = image_name + image_extension

    return renamed_image


# custom security token
class CustomCSRF:

    def __init__(self):
        app = Flask(__name__)

        app.config['SECRET_KEY'] = f'{secrets.token_hex(16)}'


# better-me maybe add this as a class rather than functions?
# custom error flashing that enables flashing of certain error types
def form_validated_message(validation_msg, category='validated'):
    return flash(validation_msg, category)


def form_error_message(error_msg, category='error'):
    return flash(error_msg, category)


# custom form validator that checks if the input date is not set in the future relative to the present date
# this avoids the situations where entries could be saved "in the future"
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


# custom form validator that checks whether the input is a number
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


# Used in faker functionality to check that given input is indeed range type
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


def gtm_trigger_len(nested_list: list) -> int:
    """
    Counts the length of a GTM Firing or Blocking condition.
    Actually counts the length of a list that is n-dimensional by skipping string members.

    :param nested_list: list or nested list
    :type nested_list: list
    :return: length of list
    :rtype: int
    """

    count = 0

    for item in nested_list:
        if type(item) is not str:
            if type(item) is list:
                count += gtm_trigger_len(item)
            else:
                count += 1

    return count


def extract_nested_strings(nested_list: list) -> list:
    """
    Extracts all found string type objects inside a n-levels nested list

    :param nested_list: Any nested list
    :type nested_list: list
    :return: List of all string type objects found
    :rtype: list
    """

    result = []

    for el in nested_list:
        if hasattr(el, "__iter__") and not isinstance(el, str):
            result.extend(extract_nested_strings(el))
        else:
            result.append(el)

    final_list = []

    for item in result:
        if type(item) is str:
            final_list.append(item)

    return list(set(final_list))


def extract_trigger_id(trigger_id: str) -> str:
    """
    Extracts the 'vtp_uniqueTriggerId' from a 'vtp_firingId' found in a trigger group list

    :param trigger_id: any string like: '31742945_23_22'
    :type trigger_id: str
    :return: A unique trigger id like '31742945_22'
    :rtype: str
    """
    vtp_firing_id = trigger_id

    trigger_id = re.sub(r'([0-9]+)_[0-9]+_([0-9]+)', r'\1_\2', vtp_firing_id)

    return trigger_id


# TODO maybe make a better template out of the two functions down here


def generate_table_entry_button(endpoint: str = None, endpoint_arguments: dict = None, extra_attrs: dict = None,
                                css_class: str = None, button_text: str = '', append_nbsp: bool = False,
                                tag: str = 'a', literal_endpoint: bool = False):
    """
    Generates an edit button that can be used in database entry editing

    :param endpoint: URL of page to open. Must be Flask like.
    :type endpoint: str
    :param endpoint_arguments: Arguments to pass to url_for function
    :type endpoint_arguments: dict
    :param css_class: Styling class for button. Defaults to 'btn btn-primary'
    :type css_class: str
    :param button_text: Button text. Defaults to 'Edit'
    :type button_text: str
    :param append_nbsp: Necessary in some cases. Appends a '&nbsp;' at the end of the string.
    :type append_nbsp: bool
    :param tag: On occasion the tag type can be changed to fit different needs
    :type tag: str
    :param extra_attrs: Extra attributes to add to tag
    :type extra_attrs: dict
    :param literal_endpoint: Wheter to consider the given endpoint as literal
    :type literal_endpoint: bool
    :return: styled anchor tag leading to a database entry edit
    :rtype: str
    """
    if css_class is None:
        css_class = 'btn btn-primary'

    if append_nbsp:
        nbsp = '&nbsp;'
    else:
        nbsp = ''

    if endpoint is None:
        endpoint = '#'
    elif endpoint == '':
        endpoint = ''
    elif not literal_endpoint:
        endpoint = url_for(endpoint, **endpoint_arguments)

    def parse_extattr(extra_attributes: dict):

        attributes = ''

        if extra_attributes is None:
            return ''

        for key, value in extra_attributes.items():
            attributes += f'{key}={value} '

        return attributes

    edit_button = f'<{tag} href="{endpoint}" class="{css_class}" {parse_extattr(extra_attrs)}>{button_text}</{tag}>{nbsp}'

    return edit_button
