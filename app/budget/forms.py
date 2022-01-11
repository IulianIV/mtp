from datetime import datetime

from flask_wtf import FlaskForm
from wtforms.fields import DateField
from wtforms.fields import SubmitField, StringField, SelectField, TextAreaField
from wtforms.validators import DataRequired

from app.manager.protection import NoFutureDates, CheckForNumber


class AddExpenseEntry(FlaskForm):
    expense_date = DateField(validators=[DataRequired(), NoFutureDates(message='You can not set a future date.')],
                             format='%Y-%m-%d', default=datetime.now())
    expense_item = SelectField(validators=[DataRequired()])
    expense_value = StringField(validators=[DataRequired(), CheckForNumber()])
    expense_source = SelectField(validators=[DataRequired()])
    submit_expense = SubmitField(validators=[DataRequired()])


class AddRevenueEntry(FlaskForm):
    revenue_date = DateField(validators=[DataRequired(), NoFutureDates(message='You can not set a future date.')],
                             format='%Y-%m-%d', default=datetime.now())
    revenue_value = StringField(validators=[DataRequired(), CheckForNumber()])
    revenue_source = SelectField(validators=[DataRequired()])
    submit_revenue = SubmitField()


class AddSavingsEntry(FlaskForm):
    savings_date = DateField(validators=[DataRequired(), NoFutureDates(message='You can not set a future date.')],
                             format='%Y-%m-%d', default=datetime.now())
    savings_value = StringField(validators=[DataRequired(), CheckForNumber()])
    savings_account = SelectField(validators=[DataRequired()])
    savings_reason = SelectField(validators=[DataRequired()])
    savings_action = SelectField(validators=[DataRequired()])
    submit_savings = SubmitField()


class AddUtilitiesEntry(FlaskForm):
    utilities_date = DateField(validators=[DataRequired(), NoFutureDates(message='You can not set a future date.')],
                               format='%Y-%m-%d', default=datetime.now())
    utilities_rent = StringField(validators=[DataRequired(), CheckForNumber()])
    utilities_energy = StringField(validators=[DataRequired(), CheckForNumber()])
    utilities_satellite = StringField(validators=[DataRequired(), CheckForNumber()])
    utilities_maintenance = StringField(validators=[DataRequired(), CheckForNumber()])
    utilities_details = TextAreaField(validators=[DataRequired()])
    utilities_budget_sources = SelectField(validators=[DataRequired()])
    submit_utilities = SubmitField()


class AddValidationItems(FlaskForm):
    category_value = SelectField(validators=[DataRequired()], coerce=str)
    item_value = StringField(validators=[DataRequired()])
    submit_items = SubmitField()


class AddValidationCategory(FlaskForm):
    category_value = StringField(validators=[DataRequired()])
    submit_category = SubmitField()


class AddValidationSources(FlaskForm):
    source_value = StringField(validators=[DataRequired()])
    submit_source = SubmitField()


class AddValidationAccounts(FlaskForm):
    account_value = StringField(validators=[DataRequired()])
    submit_account = SubmitField()


class AddValidationActions(FlaskForm):
    action_value = StringField(validators=[DataRequired()])
    submit_action = SubmitField()


class AddValidationReason(FlaskForm):
    reason_value = StringField(validators=[DataRequired()])
    submit_reason = SubmitField()


class UpdateUtilitiesEntry(FlaskForm):
    update_date = DateField(validators=[DataRequired(), NoFutureDates(message='You can not set a future date.')],
                               format='%Y-%m-%d', default=datetime.now())
    update_rent = StringField(validators=[DataRequired(), CheckForNumber()])
    update_energy = StringField(validators=[DataRequired(), CheckForNumber()])
    update_satellite = StringField(validators=[DataRequired(), CheckForNumber()])
    update_maintenance = StringField(validators=[DataRequired(), CheckForNumber()])
    update_details = TextAreaField(validators=[DataRequired()])
    update_budget_sources = SelectField(validators=[DataRequired()])
    submit_update = SubmitField()
