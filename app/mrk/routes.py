from flask import render_template

from app.auth.routes import login_required
from app.mrk import bp
from app.mrk.gtm_spy.gtmintel import GTMIntel
from app.mrk.gtm_spy.index import skip_macro_keys, macros_index, skip_tag_keys, code_snippet_properties, triggers_index
from app.mrk.gtm_spy.lurker import find_in_index
from app.manager.helpers import gtm_trigger_len, extract_nested_strings

from pprint import pprint

model_gtm_id = r'GTM-T7MRFWX'

spy = GTMIntel(model_gtm_id)
container_url = spy.url
container_id = model_gtm_id
container_version = spy.version

# TODO should the final container contain data for color coding?
# TODO add modal preview for lists and certtain variables


@bp.route('/gtm-spy', methods=('GET', 'POST'))
@login_required
def gtm_intel():



    return render_template('mrk/gtm_spy/index.html', model_gtm_path=container_url,
                           gtm_id=container_id, version=container_version)


@bp.route('/gtm-spy/tags', methods=('GET', 'POST'))
@login_required
def gtm_intel_tags():

    tags = spy.create_tag_container()
    variables = spy.create_macro_container()
    predicates = spy.create_predicates_container()

    find_index = find_in_index
    type_check = spy.process_type
    get_macro = spy.process_macro
    process_mapping = spy.process_mapping
    tag_from_predicate = spy.process_predicate_trigger
    string_list = extract_nested_strings

    code_snippets = code_snippet_properties
    skip_keys_tags = skip_tag_keys

    macro_index = macros_index
    triggers = triggers_index



    get_len = gtm_trigger_len

    return render_template('mrk/gtm_spy/tags.html', model_gtm_path=container_url,
                           gtm_id=container_id, version=container_version, tag_list=tags,
                           skip_tag_keys=skip_keys_tags, code_snippets=code_snippets, type_check=type_check,
                           find_index=find_index, get_macro=get_macro, macros_index=macro_index,
                           variables=variables, process_mapping=process_mapping, get_len=get_len,
                           predicates=predicates, triggers_index=triggers, string_list=string_list,
                           tag_from_predicate=tag_from_predicate)


@bp.route('/gtm-spy/variables', methods=('GET', 'POST'))
@login_required
def gtm_intel_variables():

    variables = spy.create_macro_container()
    skip_keys = skip_macro_keys

    type_check = spy.process_type
    get_macro = spy.process_macro
    find_index = find_in_index
    macro_index = macros_index
    process_mapping = spy.process_mapping

    return render_template('mrk/gtm_spy/variables.html', model_gtm_path=container_url,
                           gtm_id=container_id, version=container_version, variables=variables,
                           skip_macro_keys=skip_keys, type_check=type_check, get_macro=get_macro,
                           macros_index=macro_index, find_index=find_index, process_mapping=process_mapping)
