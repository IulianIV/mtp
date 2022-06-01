from flask import render_template

from app.auth.routes import login_required
from app.mrk import bp


@login_required
@bp.route('/nl-template', methods=('GET', 'POST'))
def nl_templating():
    return render_template('mrk/nl_templating.html')