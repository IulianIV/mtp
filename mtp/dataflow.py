from flask import (
    Blueprint, flash, redirect, render_template, request, url_for,
)
from flask_wtf import FlaskForm
from mtp.auth import login_required
from flask_dropzone import Dropzone
from wtforms.fields import SubmitField, FileField


bp = Blueprint('dataflow', __name__, url_prefix='/dataflow')


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
