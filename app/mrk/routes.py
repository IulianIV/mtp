from flask import render_template

from app.mrk import bp
from app.mrk.gtm_spy.container import Container

model_gtm_id = 'GTM-T7MRFWX'


@bp.route('/gtm-spy', methods=('GET', 'POST'))
def gtm_spy():
    spy = Container(model_gtm_id)
    container_url = spy.url
    spy.process_rules()

    example_map = ["list",
                   ["map", "keyz", "lookup_input", "value", "lookup_output"],
                   ["map", "keyd", "lookup_input", "value", ["macro", 5]],
                   ["map", "keyr", ["macro", 9], "value", "lookup_output"]
                   ]

    spy.process_type()

    print(spy.process_mapping(example_map))

    return render_template('mrk/gtm_spy/index.html', model_gtm_path=container_url)
