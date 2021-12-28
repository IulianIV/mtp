from flask_wtf import FlaskForm
from app.manager.protection import CheckForNumber
from wtforms.fields import SubmitField, TextAreaField, SelectField, BooleanField
from wtforms.validators import DataRequired


class AddFakes(FlaskForm):
    fake_choices = SelectField('Choose what data to fake', validators=[DataRequired()])
    fake_number = TextAreaField('Choose number of fakes to generate [range] (e.g. 5-25)', validators=[DataRequired(),
                                                                                                      CheckForNumber()])
    have_params = BooleanField('Add randomized UTMs?')
    randomized_params = BooleanField('Add randomized URL params and values?')
    submit_fakes = SubmitField()
