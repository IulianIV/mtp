from collections import defaultdict
from typing import Iterator

from flask import (
    redirect, render_template, request, url_for, current_app
)
from flask_login import current_user
from app.manager.helpers import login_required, extract_nested_strings
from app.manager.permissions import bp
from app.manager.permissions.utils import convert_url_map_to_module_map

MODULE_EXCEPTIONS = ['debugtoolbar', 'api', 'auth', '_debug_toolbar', 'static', 'static_from_root']


@bp.route('/user-roles/view', methods=('GET',))
@login_required
def user_roles_view():
    user_id = current_user.get_id()

    return render_template('manager/permissions/view_user_roles.html')


# TODO Must have in mind the following: assuming that we have a collection of modules and submodules that upon user
#   selection become a JSON object that is stored in a database, what happens when and if an endpoint is modified
#   or even removed?
#   If an endpoint is removed it is pretty easy, I suppose - you reparse the rules, create the JSON and update the DB
#   but eliminate the differences between them.
#   What if an endpoint is just plain modified?
@bp.route('/user-roles/create', methods=('POST', 'GET'))
def user_roles_create():
    rule_map = current_app.url_map.iter_rules()

    module_map = convert_url_map_to_module_map(rule_map, skip_list=MODULE_EXCEPTIONS)

    return render_template('manager/permissions/create_user_roles.html', module_map=module_map)
