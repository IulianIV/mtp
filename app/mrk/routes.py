from flask import render_template

from app.mrk import bp
from app.mrk.gtm_spy.container import Container

model_gtm_id = 'GTM-T7MRFWX'


@bp.route('/gtm-spy', methods=('GET', 'POST'))
def gtm_spy():

    spy = Container(model_gtm_id)
    container_url = spy.url
    macro_func = spy.get_functions(spy.tags)
    print(macro_func)
    print(spy.container)
    print(container_url)

    return render_template('mrk/gtm_spy/index.html', model_gtm_path=container_url)
