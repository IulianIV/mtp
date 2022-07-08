from flask import render_template

from app.mrk import bp
from app.mrk.gtm_spy.gtmintel import GTMIntel
from app.mrk.gtm_spy.index import tags_index, skip_macro_keys, macros_index
from app.mrk.gtm_spy.lurker import find_in_index

model_gtm_id = 'GTM-T7MRFWX'

spy = GTMIntel(model_gtm_id)
container_url = spy.url
container_id = model_gtm_id
container_version = spy.version

# TODO should the final container contain data for color coding?
# TODO add modal preview for lists and certtain variables


@bp.route('/gtm-spy', methods=('GET', 'POST'))
def gtm_intel():



    return render_template('mrk/gtm_spy/index.html', model_gtm_path=container_url,
                           gtm_id=container_id, version=container_version)


# fixme this error passes silently. Deal with KeyError cases.
@bp.route('/gtm-spy/tags', methods=('GET', 'POST'))
def gtm_intel_tags():
    tags = spy.tags
    tag_list = []

    for tag in tags:
        try:
            tag_list.append(find_in_index(tag['function'], tags_index))
        except KeyError:
            continue

    return render_template('mrk/gtm_spy/tags.html', model_gtm_path=container_url,
                           gtm_id=container_id, version=container_version, tag_list=tag_list)


@bp.route('/gtm-spy/variables', methods=('GET', 'POST'))
def gtm_intel_variables():

    variables = spy.create_macro_container()
    skip_keys = skip_macro_keys

    type_check = spy.process_type
    get_macro = spy.process_macro
    find_index = find_in_index
    macro_index = macros_index
    process_mapping = spy.process_mapping

    # Creates a new dictionary that contains:
    #   1. All the relevant data from the original container
    #   2. Dict keys with all the relevant information from the index
    #   3. When parsing the final dict in the front-end these dict keys should not be shown in the modal
    #       title, isBuiltin, pill, nameProperty, function
    return render_template('mrk/gtm_spy/variables.html', model_gtm_path=container_url,
                           gtm_id=container_id, version=container_version, variables=variables,
                           skip_macro_keys=skip_keys, type_check=type_check, get_macro=get_macro,
                           macros_index=macro_index, find_index=find_index, process_mapping=process_mapping)
