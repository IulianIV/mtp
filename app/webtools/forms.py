from flask_wtf import FlaskForm
from wtforms.fields import TextAreaField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Optional


class EncodeDecode(FlaskForm):
    url_field = TextAreaField('URL Field', validators=[DataRequired()])
    encode = BooleanField('Encode', validators=[Optional()])
    decode = BooleanField('Decode', validators=[Optional()])
    select_encoding = SelectField('Select encoding', validators=[Optional()])
    submit = SubmitField()

