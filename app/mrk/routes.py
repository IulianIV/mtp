import json

from flask import render_template, request, redirect, url_for
from flask_login import current_user

from app import db
from app.manager.db.db_interrogations import (
    gtm_container_exists, get_active_gtm_container, insert_gtm_container,
    set_gtm_container_active, set_gtm_container_inactive, inactivate_all_gtm_containers
)
from app.auth.routes import login_required
from app.mrk import bp
from app.mrk.forms import ContainerLoad
from app.mrk.gtm_spy.gtmintel import GTMIntel
from app.mrk.gtm_spy.index import (skip_macro_keys, macros_index, skip_tag_keys,
                                   code_snippet_properties, triggers_index, skip_groups, triggers_not_tags)
from app.mrk.gtm_spy.lurker import find_in_index
from app.manager.helpers import gtm_trigger_len, extract_nested_strings


# TODO should the final container contain data for color coding?
# TODO add modal preview for lists and certain variables

@bp.route('/gtm-spy/', methods=('GET', 'POST'))
@login_required
def gtm_intel():
    container_id_form = ContainerLoad()
    user_id = current_user.get_id()

    if request.method == 'POST':
        if container_id_form.is_submitted() and container_id_form.validate_on_submit():

            inactivate_all_gtm_containers(user_id)

            container_id = container_id_form.container_id.data
            if gtm_container_exists(user_id, container_id):
                set_gtm_container_active(user_id, container_id)
                return redirect(url_for('mrk.gtm_intel_tags'))
            else:
                container = GTMIntel(container_id, True)
                container_data = json.dumps(container.original_container).encode('utf-8')
                insert_gtm_container(user_id, container_id, container_data)
                db.session.commit()
                set_gtm_container_active(user_id, container_id)
                return redirect(url_for('mrk.gtm_intel_tags'))

    return render_template('gtm_base.html', container_id_form=container_id_form)


@bp.route('/gtm-spy/tags', methods=('GET', 'POST'))
@login_required
def gtm_intel_tags():
    container_id_form = ContainerLoad()
    user_id = current_user.get_id()

    container = get_active_gtm_container(user_id)
    print(container)

    c_id = container.container_id
    c_content = container.container_data
    spy = GTMIntel(c_id, False, c_content)

    tags = spy.create_tag_container()
    variables = spy.create_macro_container()
    predicates = spy.create_predicates_container()

    tag_from_predicate = spy.process_predicate_trigger
    type_check = spy.process_type
    get_macro = spy.process_macro
    process_mapping = spy.process_mapping
    string_list = extract_nested_strings
    code_snippets = code_snippet_properties
    get_len = gtm_trigger_len

    container_url = spy.url
    container_id = spy.id
    container_version = spy.version
    skip_keys_tags = skip_tag_keys

    find_index = find_in_index
    macro_index = macros_index
    except_triggers = triggers_not_tags

    return render_template('mrk/gtm_spy/tags.html', model_gtm_path=container_url,
                           gtm_id=container_id, version=container_version, tag_list=tags,
                           skip_tag_keys=skip_keys_tags, code_snippets=code_snippets, type_check=type_check,
                           find_index=find_index, get_macro=get_macro, macros_index=macro_index,
                           variables=variables, process_mapping=process_mapping, get_len=get_len,
                           predicates=predicates, triggers_index=triggers_index, string_list=string_list,
                           tag_from_predicate=tag_from_predicate, except_triggers=except_triggers,
                           container_id_form=container_id_form)


@bp.route('/gtm-spy/triggers', methods=('GET', 'POST'))
@login_required
def gtm_intel_triggers():
    container_id_form = ContainerLoad()
    user_id = current_user.get_id()

    container = get_active_gtm_container(user_id)
    print(container)

    c_id = container.container_id
    c_content = container.container_data
    spy = GTMIntel(c_id, False, c_content)

    triggers = spy.create_trigger_container()
    trigger_groups = spy.process_trigger_groups()
    variables = spy.create_macro_container()
    predicates = spy.create_predicates_container()

    type_check = spy.process_type
    get_macro = spy.process_macro
    process_mapping = spy.process_mapping

    container_url = spy.url
    container_id = spy.id
    container_version = spy.version

    skip_keys_tags = skip_tag_keys
    skip_keys = skip_groups

    find_index = find_in_index
    macro_index = macros_index

    return render_template('mrk/gtm_spy/triggers.html', model_gtm_path=container_url,
                           gtm_id=container_id, version=container_version, triggers=triggers,
                           skip_keys=skip_keys, trigger_groups=trigger_groups, find_index=find_index,
                           triggers_index=triggers_index, predicates=predicates, type_check=type_check,
                           get_macro=get_macro, process_mapping=process_mapping, macros_index=macro_index,
                           variables=variables, skip_tag_keys=skip_keys_tags, container_id_form=container_id_form)


@bp.route('/gtm-spy/variables', methods=('GET', 'POST'))
@login_required
def gtm_intel_variables():
    container_id_form = ContainerLoad()
    user_id = current_user.get_id()

    container = get_active_gtm_container(user_id)
    print(container)

    c_id = container.container_id
    c_content = container.container_data
    spy = GTMIntel(c_id, False, c_content)

    variables = spy.create_macro_container()

    type_check = spy.process_type
    get_macro = spy.process_macro
    process_mapping = spy.process_mapping

    container_url = spy.url
    container_id = spy.id
    container_version = spy.version

    skip_keys = skip_macro_keys

    find_index = find_in_index
    macro_index = macros_index

    return render_template('mrk/gtm_spy/variables.html', model_gtm_path=container_url,
                           gtm_id=container_id, version=container_version, variables=variables,
                           skip_macro_keys=skip_keys, type_check=type_check, get_macro=get_macro,
                           macros_index=macro_index, find_index=find_index, process_mapping=process_mapping,
                           container_id_form=container_id_form)
