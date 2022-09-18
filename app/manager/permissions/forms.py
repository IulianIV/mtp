from flask_wtf import FlaskForm

from wtforms.fields import SubmitField, StringField, SelectField
from wtforms.validators import DataRequired


class RulesForm(FlaskForm):
    role_name = StringField('Role Name', validators=[DataRequired()])
    # for future reference
    # Currently, using a FieldList to grab an array of checkboxes is not possible due to HTML limitations
    # more info at: https://wtforms.readthedocs.io/en/2.3.x/fields/#wtforms.fields.FieldList
    # role_rules = FieldList(BooleanField('Role Rules', validators=[DataRequired()]))
    submit_rules = SubmitField('Submit Rules')


class UpdateUserRole(FlaskForm):
    user_role = SelectField(validators=[DataRequired()])


