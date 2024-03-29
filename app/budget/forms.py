from datetime import datetime

from flask_wtf import FlaskForm
from wtforms.fields import DateField
from wtforms.fields import SubmitField, StringField, SelectField, TextAreaField, HiddenField
from wtforms.validators import DataRequired

from app.manager.helpers import NoFutureDates, CheckForNumber


# fixme check all validators. Some Select Text Fields have "CheckForNumber()" validators that don't even do their job.


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


class AddRecurrentPayment(FlaskForm):
    recurrent_name = StringField('Payment name', validators=[DataRequired()])
    recurrent_value = StringField('Currency', validators=[DataRequired()])
    submit_recurrent = SubmitField('Add Recurrent payment')


class RecurrentPaymentOperations(FlaskForm):
    recurrent_id_field = HiddenField('recurrent_id')
    loop_index_field = HiddenField('loop_index_field')
    new_recurrent_name = StringField('Payment name')
    new_recurrent_value = StringField('Currency')
    save_edited_entry = SubmitField('Save edit')
    delete_edited_entry = SubmitField('Delete entry')
    send_recurrent_entry = SubmitField('Add expense')


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


class UpdateRevenueEntry(FlaskForm):
    update_date = DateField(validators=[DataRequired(), NoFutureDates(message='You can not set a future date.')],
                            format='%Y-%m-%d', default=datetime.now())
    update_value = StringField(validators=[DataRequired(), CheckForNumber()])
    update_sources = SelectField(validators=[DataRequired(), CheckForNumber()])
    submit_update = SubmitField()


class UpdateExpenseEntry(FlaskForm):
    update_date = DateField(validators=[DataRequired(), NoFutureDates(message='You can not set a future date.')],
                            format='%Y-%m-%d', default=datetime.now())
    update_item = SelectField(validators=[DataRequired()])
    update_value = StringField(validators=[DataRequired(), CheckForNumber()])
    update_source = SelectField(validators=[DataRequired()])
    submit_update = SubmitField(validators=[DataRequired()])


class UpdateSavingsEntry(FlaskForm):
    update_date = DateField(validators=[DataRequired(), NoFutureDates(message='You can not set a future date.')],
                            format='%Y-%m-%d', default=datetime.now())
    update_value = StringField(validators=[DataRequired(), CheckForNumber()])
    update_account = SelectField(validators=[DataRequired()])
    update_reason = SelectField(validators=[DataRequired()])
    update_action = SelectField(validators=[DataRequired()])
    submit_update = SubmitField()
