from flask_wtf import FlaskForm

from wtforms.fields import StringField, TextAreaField, SubmitField, HiddenField
from wtforms.validators import DataRequired

# TODO add a post title 30 char limit
# TODO add a post body 255 char limit


class ContainerLoad(FlaskForm):
    container_id = StringField('Container ID', validators=[DataRequired()])
    submit_id = SubmitField('Load')

