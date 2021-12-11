from flask_wtf import FlaskForm
from wtforms.fields import TextAreaField, BooleanField, SubmitField, SelectField, StringField
from wtforms.validators import DataRequired, Optional


class EncodeDecodeParse(FlaskForm):
    url_field = TextAreaField('URL Field', validators=[DataRequired()])
    encode = BooleanField('Encode', validators=[Optional()])
    decode = BooleanField('Decode', validators=[Optional()])
    select_encoding = SelectField('Select encoding', validators=[Optional()])
    encode_decode = SubmitField(label='Encode/Decode')
    parse = SubmitField(label='Parse')
