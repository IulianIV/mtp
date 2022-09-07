import functools
from collections import defaultdict
from typing import Iterator

from flask import (
    redirect, url_for, request
)
from flask_login import current_user

from app.manager.helpers import extract_nested_strings
from app.manager.db.models import User
from app.manager.db.db_interrogations import get_existing_user_by_id, get_user_role_rules

from app.manager.helpers import app_endpoints, form_error_message


# Converts a Werkzeug url_map to a user and computer friendly module mapping
def convert_url_map_to_module_map(url_map: Iterator, skip_list: list = None):
    if skip_list is None:
        skip_list = []

    rule_map = url_map

    module_map = defaultdict(list)

    for rule in rule_map:
        module = rule.endpoint
        split_module = module.split('.')

        if split_module[0] not in skip_list:
            # default dict is needed to seamlessly add multiple values to the same dictionary key
            module_map[split_module[0]].append([split_module[x] for x in range(1, len(split_module))])
        else:
            continue

    # because de defaultdict is initialized with a list, all previously appended members are nested.
    # this iteration flattens nested lists regardless of nesting depth
    for key, value in module_map.items():
        module_map[key] = extract_nested_strings(value)

    return module_map


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if User.query.all() is None:
            return redirect(url_for(app_endpoints['login']))

        return view(**kwargs)

    return wrapped_view


def requires_permissions(view):
    @functools.wraps(view)
    def permission_wall(**kwargs):
        user_id = current_user.get_id()

        user_role = get_user_role_rules(user_id)
        role_rules = [user_role[x].role_rule for x in range(0, len(user_role))]

        current_endpoint = view.__name__

        if current_endpoint not in role_rules:
            current_path = request.path
            form_error_message(f'You do not have sufficient permission to access this view: {current_path}')

            return redirect(url_for(app_endpoints['blog_index']))

        return view(**kwargs)

    return permission_wall
