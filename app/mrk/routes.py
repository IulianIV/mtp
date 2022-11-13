import json
import jsbeautifier

from flask import render_template, request, redirect, url_for
from flask_login import current_user

from app import db
from app.manager.db.db_interrogations import (
    gtm_container_exists, get_active_gtm_container, insert_gtm_container,
    set_gtm_container_active, inactivate_all_gtm_containers,
    get_gtm_containers, update_gtm_container_data, update_gtm_container_source
)
from app.manager.permissions.utils import login_required, requires_permissions
from app.mrk import bp
from app.mrk.forms import ContainerLoad
from app.mrk.tag_spy.gtm_container import GTMResource, GTMRuntime
from app.mrk.tag_spy.index import (skippable_macro_keys, macros_index, skippable_tag_keys,
                                   code_snippet_properties, triggers_index, skippable_trigger_keys, triggers_not_tags)
from app.mrk.tag_spy.utils import gtm_compare_get_version, find_in_index
from app.manager.helpers import gtm_trigger_len, extract_nested_strings, form_validated_message
from app.mrk.tag_spy.gtm_resources import GTMResourceMacros

# TODO should the final container contain data for color coding?
# TODO add modal preview for lists and certain variables

index_url = 'mrk.gtm_intel'


@bp.context_processor
def inject_containers():
    user_id = current_user.get_id()
    raw_containers = get_gtm_containers(user_id)
    containers = [container.container_id for container in raw_containers]
    new_version = gtm_compare_get_version

    return dict(containers=containers, new_version=new_version)


@bp.route('/gtm-spy/', methods=('GET', 'POST'))
@requires_permissions
@login_required
def gtm_intel():
    container_id_form = ContainerLoad()
    user_id = current_user.get_id()

    if user_id is None:
        return redirect(url_for(index_url))

    gtm_tags_url = 'mrk.gtm_intel_tags'

    if request.method == 'POST':
        if container_id_form.is_submitted() and container_id_form.validate_on_submit():

            container_id = container_id_form.container_id.data

            if container_id == 'Reload from Source':
                current_container_id = get_active_gtm_container(user_id).container_id

                container = GTMResource(current_container_id, True)
                container_data = json.dumps(container.original_container).encode('utf-8')

                update_gtm_container_data(user_id, current_container_id, container_data)

                form_validated_message(f'Successfully loaded a new container version (v{container.version})')

                return redirect(url_for(gtm_tags_url))

            inactivate_all_gtm_containers(user_id)

            if gtm_container_exists(user_id, container_id):
                set_gtm_container_active(user_id, container_id)
                return redirect(url_for(gtm_tags_url))
            else:
                container = GTMResource(container_id, True)
                container_data = json.dumps(container.original_container).encode('utf-8')
                insert_gtm_container(user_id, container_id, container_data)
                db.session.commit()
                set_gtm_container_active(user_id, container_id)
                return redirect(url_for(gtm_tags_url))

    return render_template('tag_spy_base.html', container_id_form=container_id_form)


@bp.route('/gtm-spy/add-domain', methods=('GET', 'POST'))
@login_required
def add_container_domain():
    user_id = current_user.get_id()
    container_id = request.args.get('container_id')
    container_domain = request.args.get('container_domain')

    update_gtm_container_source(user_id, container_id, container_domain)

    return redirect(url_for(request.url))

@bp.route('/gtm-spy/variables', methods=('GET', 'POST'))
@login_required
def gtm_intel_variables():
    container_id_form = ContainerLoad()
    user_id = current_user.get_id()

    if user_id is None:
        return redirect(url_for(index_url))

    container = get_active_gtm_container(user_id)

    c_id = container.container_id
    c_content = container.container_data
    spy = GTMResource(c_id, False, c_content)

    variables = spy.macros.parse().parsed

    type_check = spy.macros.determine_type
    get_macro = spy.macros.get_macro_by_reference
    process_mapping = spy.macros.process_mapping

    container_url = spy.url
    container_id = spy.id
    container_domain = container.container_source
    container_version = spy.version

    skip_keys = skippable_macro_keys
    code_snippets = code_snippet_properties

    find_index = find_in_index
    macro_index = macros_index

    js_prettify = jsbeautifier.beautify

    return render_template('mrk/tag_spy/variables.html', model_gtm_path=container_url,
                           gtm_id=container_id, version=container_version, variables=variables,
                           skip_macro_keys=skip_keys, type_check=type_check, get_macro=get_macro,
                           macros_index=macro_index, find_index=find_index, process_mapping=process_mapping,
                           container_id_form=container_id_form, code_snippets=code_snippets,
                           GTMResourceMacro=GTMResourceMacros,js_prettify=js_prettify,
                           container_domain=container_domain)


@bp.route('/gtm-spy/summary', methods=('GET', 'POST'))
@requires_permissions
@login_required
def gtm_intel_summary():
    container_id_form = ContainerLoad()
    user_id = current_user.get_id()

    if user_id is None:
        return redirect(url_for(index_url))

    container = get_active_gtm_container(user_id)

    container_id = container.container_id
    container_domain = container.container_source
    container_content = container.container_data
    spy = GTMResource(container_id, False, container_content)

    container_url = spy.url
    container_version = spy.version

    container_data = {
        'tags': len(spy.tags.parse().parsed),
        'triggers': len(spy.tags.create_trigger_container()),
        'variables': len(spy.macros.parsed)
    }

    return render_template('mrk/tag_spy/index.html', model_gtm_path=container_url, gtm_id=container_id,
                           container_id=container_id, container_id_form=container_id_form,
                           container_data=container_data, container_domain=container_domain, version=container_version)


@bp.route('/gtm-spy/tags', methods=('GET', 'POST'))
@requires_permissions
@login_required
def gtm_intel_tags():
    container_id_form = ContainerLoad()
    user_id = current_user.get_id()

    if user_id is None:
        return redirect(url_for(index_url))

    container = get_active_gtm_container(user_id)

    c_id = container.container_id
    c_content = container.container_data
    spy = GTMResource(c_id, False, c_content)

    tags = spy.tags.parse().parsed
    variables = spy.tags.macros.parse()
    predicates = spy.predicates.parse().parsed

    tag_from_predicate = spy.tags.process_predicate_trigger
    type_check = spy.tags.determine_type
    get_macro = variables.get_macro_by_reference
    process_mapping = variables.process_mapping
    string_list = extract_nested_strings
    code_snippets = code_snippet_properties
    get_len = gtm_trigger_len

    container_url = spy.url
    container_id = spy.id
    container_domain = container.container_source
    container_version = spy.version
    skip_keys_tags = skippable_tag_keys

    find_index = find_in_index
    macro_index = macros_index
    except_triggers = triggers_not_tags

    js_prettify = jsbeautifier.beautify

    return render_template('mrk/tag_spy/tags.html', model_gtm_path=container_url,
                           gtm_id=container_id, version=container_version, tag_list=tags,
                           skip_tag_keys=skip_keys_tags, code_snippets=code_snippets, type_check=type_check,
                           find_index=find_index, get_macro=get_macro, macros_index=macro_index,
                           variables=variables.parsed, process_mapping=process_mapping, get_len=get_len,
                           predicates=predicates, triggers_index=triggers_index, string_list=string_list,
                           tag_from_predicate=tag_from_predicate, except_triggers=except_triggers,
                           container_id_form=container_id_form, container_domain=container_domain,
                           GTMResourceMacro=GTMResourceMacros, js_prettify=js_prettify)


@bp.route('/gtm-spy/triggers', methods=('GET', 'POST'))
@requires_permissions
@login_required
def gtm_intel_triggers():
    container_id_form = ContainerLoad()
    user_id = current_user.get_id()

    if user_id is None:
        return redirect(url_for(index_url))

    container = get_active_gtm_container(user_id)

    c_id = container.container_id
    container_domain = container.container_source
    c_content = container.container_data
    spy = GTMResource(c_id, False, c_content)

    triggers = spy.tags.create_trigger_container()
    variables = spy.macros.parse().parsed
    predicates = spy.predicates.parse().parsed
    trigger_groups = spy.tags.process_trigger_groups()

    type_check = spy.macros.determine_type
    get_macro = spy.macros.get_macro_by_reference
    process_mapping = spy.macros.process_mapping
    tag_from_predicate = spy.tags.process_predicate_trigger
    code_snippets = code_snippet_properties
    search_in_container = spy.tags.get_by_key_value

    container_url = spy.url
    container_id = spy.id
    container_version = spy.version

    skip_keys_tags = skippable_tag_keys
    skip_keys = skippable_trigger_keys

    find_index = find_in_index
    macro_index = macros_index
    get_len = gtm_trigger_len

    js_prettify = jsbeautifier.beautify

    return render_template('mrk/tag_spy/triggers.html', model_gtm_path=container_url,
                           gtm_id=container_id, version=container_version, triggers=triggers,
                           skip_keys=skip_keys, trigger_groups=trigger_groups, find_index=find_index,
                           triggers_index=triggers_index, predicates=predicates, type_check=type_check,
                           get_macro=get_macro, process_mapping=process_mapping, macros_index=macro_index,
                           variables=variables, skip_tag_keys=skip_keys_tags, container_id_form=container_id_form,
                           get_len=get_len, tag_from_predicate=tag_from_predicate, code_snippets=code_snippets,
                           search_in_container=search_in_container, GTMResourceMacro=GTMResourceMacros,
                           js_prettify=js_prettify, container_domain=container_domain)


@bp.route('/gtm-spy/runtime/<string:template_type>', methods=('GET', 'POST'))
def gtm_intel_runtime(template_type):
    container_id_form = ContainerLoad()
    user_id = current_user.get_id()
    templates = ''

    if user_id is None:
        return redirect(url_for(index_url))

    container = get_active_gtm_container(user_id)

    c_id = container.container_id
    c_content = container.container_data
    spy = GTMRuntime(c_id, False, c_content)

    resource = GTMResource(c_id, False, c_content)

    container_url = spy.url
    container_id = spy.id
    container_domain = container.container_source
    container_version = spy.version

    if template_type == 'custom-tags':
        templates = (template if template.name in resource.tags.get_names() else '' for template in spy.templates)

    if template_type == 'custom-variables':
        templates = (template if template.name in resource.macros.get_names() else '' for template in spy.templates)

    js_prettify = jsbeautifier.beautify

    return render_template('mrk/tag_spy/runtime.html', model_gtm_path=container_url,
                           gtm_id=container_id, version=container_version, container_id_form=container_id_form,
                           templates=templates, js_prettify=js_prettify, container_domain=container_domain)
