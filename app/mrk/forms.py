from flask_wtf import FlaskForm

from wtforms.fields import StringField, SubmitField, FormField, FieldList


class TemplateElementForm(FlaskForm):
    element = StringField('Template element')


class TemplateForm(FlaskForm):
    elements = FieldList(FormField(TemplateElementForm))
    submit_elements = SubmitField('Submit')




