from bs4 import BeautifulSoup
from flask import render_template

from app.auth.routes import login_required
from app.mrk import bp
from app.mrk.forms import TemplateForm

# API Section & Credentials - For Future Use #
'''
url_req = requests.post("https://api.mjml.io/v1/render", auth=(app_id, secret_key), json=mjml_snippet)
    
    response_dict = ast.literal_eval(url_req.content.decode())
    response_html = response_dict['html']
    app_id = 'cf88612b-a7ee-47f3-a0cf-80b119c09b74'

    # use in server-side
    secret_key = 'ec0b2386-5ea9-4e30-b903-457e962eef92'

    # use if request from browser
    pub_key = '7e4ff060-d699-41c0-bead-3f87f17c4199'
    
'''
# API Section End #


def get_template_elements():
    mjml_snippet = {
        "mjml": "<title><mjml><mj-body><mj-container><mj-section mark='product_section'><mj-column "
                "mark='product_cell_1'><mj-text mark='product_name_1'>Hello "
                "World</mj-text><mj-text mark='product_name_2'>Hello "
                "World 2</mj-text><mj-text mark='product_name_3'>Hello "
                "World 3</mj-text></mj-column></mj-section></mj-container></mj-body></mjml></title> "
    }

    soup = BeautifulSoup(mjml_snippet['mjml'], 'html.parser')
    tags = soup.find_all('mj-text')

    attrs = [tag['mark'] for tag in tags]

    return attrs


@login_required
@bp.route('/nl-template', methods=('GET', 'POST'))
def nl_templating():

    form = TemplateForm()

    for _ in range(len(get_template_elements())):
        form.elements.append_entry()

    get_template_elements()

    return render_template('mrk/nl_templating.html', form=form)
