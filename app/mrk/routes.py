from flask import render_template

from app.mrk import bp
from app.mrk.gtm_spy.container import Container

model_gtm_id = 'GTM-T7MRFWX'


@bp.route('/gtm-spy', methods=('GET', 'POST'))
def gtm_spy():

    spy = Container(model_gtm_id)
    container_url = spy.url
    tags = spy.tags

    item_props = spy.available_item_properties(tags[5])
    section_props = spy.get_section_properties(tags)

    tag_id_properties = spy.get_section_properties_values(tags, 'tag_id')

    print(tag_id_properties)
    print(item_props)
    print(section_props)
    print(tags[5]['tag_id'])

    return render_template('mrk/gtm_spy/index.html', model_gtm_path=container_url)
