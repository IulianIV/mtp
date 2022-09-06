from flask import (
    redirect, render_template, request, url_for, current_app
)
from flask_login import current_user
from app.manager.helpers import login_required
from app.manager.permissions import bp


@bp.route('/user-roles/view', methods=('GET',))
@login_required
def user_roles_view():
    user_id = current_user.get_id()

    return render_template('manager/permissions/view_user_roles.html')


@bp.route('/user-roles/create', methods=('POST', 'GET'))
def user_roles_create():

    all_urls = current_app.url_map.iter_rules()
    for url in all_urls:
        print(f'URL endpoint: {url.endpoint}')
        print(f'URL rule: {url.rule}')

    return render_template('manager/permissions/create_user_roles.html')