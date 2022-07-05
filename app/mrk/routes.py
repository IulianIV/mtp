from flask import render_template

from app.mrk import bp
from app.mrk.gtm_spy.gtmintel import GTMIntel
from app.mrk.gtm_spy.index import macros_index, tags_index
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
    macros = spy.macros
    variables = []

    for var in macros:
        variables.append(find_in_index(var['function'], macros_index))

    return render_template('mrk/gtm_spy/variables.html', model_gtm_path=container_url,
                           gtm_id=container_id, version=container_version, variables=variables)