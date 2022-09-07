from flask import (
    redirect, render_template, url_for, current_app
)
from flask_login import current_user
from app.manager.permissions.utils import login_required, requires_permissions
from app.manager.permissions import bp
from app.manager.permissions.utils import convert_url_map_to_module_map
from app.manager.db.db_interrogations import get_user_role_rules

MODULE_EXCEPTIONS = ['debugtoolbar', 'api', 'auth', '_debug_toolbar', 'static', 'static_from_root']


# TODO Must have in mind the following: assuming that we have a collection of modules and submodules that upon user
#   selection become a JSON object that is stored in a database, what happens when and if an endpoint is modified
#   or even removed?
#   If an endpoint is removed it is pretty easy, I suppose - you reparse the rules, create the JSON and update the DB
#   but eliminate the differences between them.
#   What if an endpoint is just plain modified?
@bp.route('/user-roles', methods=('GET',))
@requires_permissions
@login_required
def user_roles():

    rule_map = current_app.url_map.iter_rules()

    module_map = convert_url_map_to_module_map(rule_map, skip_list=MODULE_EXCEPTIONS)

    print(module_map)

    return render_template('manager/permissions/user_roles.html', module_map=module_map)



