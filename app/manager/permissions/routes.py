from flask import (
    render_template, current_app, request, redirect, url_for
)
from app.manager.permissions.utils import login_required, requires_permissions,\
    convert_url_map_to_module_map, process_rule_list
from app.manager.permissions import bp
from app.manager.db.db_interrogations import get_all_roles, get_all_users
from app.manager.helpers import form_validated_message, form_error_message
from app import Config

from app.manager.permissions import forms

# TODO Must have in mind the following: assuming that we have a collection of modules and submodules that upon user
#   selection become a JSON object that is stored in a database, what happens when and if an endpoint is modified
#   or even removed?
#   If an endpoint is removed it is pretty easy, I suppose - you reparse the rules, create the JSON and update the DB
#   but eliminate the differences between them.
#   What if an endpoint is just plain modified?


@bp.route('/user-roles', methods=('GET', 'POST'))
@requires_permissions
@login_required
def user_roles():
    rules_form = forms.RulesForm()

    all_roles = get_all_roles()
    rule_map = current_app.url_map.iter_rules()

    module_map = convert_url_map_to_module_map(rule_map, skip_list=Config.MODULE_EXCEPTIONS)

    # HTML forms limitations enforce usage of requests to get checkbox array data
    # read more info in permissions/forms.py comments
    if request.method == 'POST':
        if rules_form.is_submitted() and rules_form.validate_on_submit():
            selected_modules_list = request.form.getlist('module_name')

            print(selected_modules_list)


            rule_list = process_rule_list(selected_modules_list, module_map)


            if selected_modules_list == ['']:
                form_error_message('You can not create a Role with no rules.')

                return redirect(url_for('permissions.user_roles'))

            form_validated_message(f'New role "{rules_form.role_name.data}" '
                                   f'has been submitted. It will become available in a few moments')

            return redirect(url_for('permissions.user_roles'))

            # add function that processes the selected list.
            # if in the selected list is a Parent module name remove parent, remove children and
            # re-populate with parents children (basically give module wide access)

    return render_template('manager/permissions/user_roles.html', rules_form=rules_form,
                           module_map=module_map, all_roles=all_roles)


@bp.route('/all-users', methods=('GET', 'POST'))
@requires_permissions
@login_required
def all_users():

    users = get_all_users()

    return render_template('manager/permissions/all_users.html', all_users=users)
