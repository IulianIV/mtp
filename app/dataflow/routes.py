from flask import (
    render_template, )
from flask_dropzone import Dropzone
from flask_wtf import FlaskForm
from wtforms.fields import SubmitField

from app.manager.helpers import login_required
from app.dataflow import bp


class UploadForm(FlaskForm):
    uploaded_file = SubmitField()
    submit_upload = SubmitField()


@bp.route('/importer', methods=('GET', 'POST'))
@login_required
def importer():
    upload_form = UploadForm()

    dropzone = Dropzone()

    return render_template('dataflow/importer.html', dropzone=dropzone, upload_form=upload_form)


@bp.route('/exporter')
@login_required
def exporter():
    return render_template('dataflow/exporter.html')
    pass
