from flask import (
    render_template, )
from flask_dropzone import Dropzone
from flask_wtf import FlaskForm
from wtforms.fields import SubmitField

from app.manager.permissions.utils import login_required, requires_permissions
from app.dataflow import bp


class UploadForm(FlaskForm):
    uploaded_file = SubmitField()
    submit_upload = SubmitField()


@bp.route('/importer', methods=('GET', 'POST'))
@requires_permissions
@login_required
def importer():
    upload_form = UploadForm()

    dropzone = Dropzone()

    return render_template('dataflow/importer.html', dropzone=dropzone, upload_form=upload_form)


@bp.route('/exporter')
@requires_permissions
@login_required
def exporter():
    return render_template('dataflow/exporter.html')
    pass
