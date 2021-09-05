from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)
from flask_wtf import FlaskForm
from mtp.auth import login_required
from mtp.db_manager.db import get_db
from mtp.db_manager.db_interrogations import Query, Insert
from mtp.protection import CustomCSRF, form_validated_message, form_error_message
from wtforms.fields import SubmitField, TextField, SelectField, DateField, IntegerField, TextAreaField
from wtforms.validators import InputRequired, Regexp


bp = Blueprint('budget', __name__, url_prefix='/budget')

custom_protection = CustomCSRF()

# Class object for handling multiple SQL queries, might be useful in cases where above code does not work


class BudgetDbConnector:
    def __init__(self):
        self.db = get_db()
        self.db_queries = Query()
        self.db_inserts = Insert()

    @property
    def query_expense_entries(self):

        return self.db_queries.query_expense_entries()

    @property
    def query_revenue_entries(self):

        return self.db_queries.query_revenue_entries()

    @property
    def query_savings_entries(self):

        return self.db_queries.query_savings_entries()

    @property
    def query_utilities_entry(self):
        return self.db_queries.query_utilities_entries()

    @property
    def query_validation_items(self):

        return self.db_queries.query_validation_items()

    @property
    def query_validation_categories(self):

        return self.db_queries.query_validation_categories()

    @property
    def query_validation_savings_accounts(self):

        return self.db_queries.query_validation_savings_accounts()

    @property
    def query_validation_sources(self):

        return self.db_queries.query_validation_sources()

    @property
    def query_validation_savings_action_types(self):

        return self.db_queries.query_validation_savings_action_types()

    @property
    def query_validation_savings_reason(self):

        return self.db_queries.query_validation_savings_reason()

    def insert_expense(self, date, item, value, item_category, source):
        return self.db_inserts.insert_expense(date, item, value, item_category, source)

    def insert_revenue(self, date, revenue, source):
        return self.db_inserts.insert_revenue(date, revenue, source)

    def insert_savings(self, date, value, source, reason, action):
        return self.db_inserts.insert_savings(date, value, source, reason, action)

    def insert_utilities(self, date, rent, energy, satellite, maintenance, details):
        return self.db_inserts.insert_utilities(date, rent, energy, satellite, maintenance, details)

    def insert_validation_items(self, item, category):
        return self.db_inserts.insert_validation_items(item, category)

    def insert_validation_categories(self, categories):
        return self.db_inserts.insert_validation_categories(categories)

    def insert_validation_sources(self, sources):
        return self.db_inserts.insert_validation_sources(sources)

    def insert_validation_accounts(self, accounts):
        return self.db_inserts.insert_validation_accounts(accounts)

    def insert_validation_actions(self, actions):
        return self.db_inserts.insert_validation_actions(actions)

    def insert_validation_reasons(self, reasons):
        return self.db_inserts.insert_validation_reasons(reasons)


class AddExpenseEntry(FlaskForm):
    expense_date = DateField([InputRequired()])
    expense_item = SelectField([InputRequired()])
    expense_value = IntegerField([InputRequired()])
    expense_category = SelectField([InputRequired()])
    expense_source = SelectField([InputRequired()])
    submit_expense = SubmitField([InputRequired()])


class AddRevenueEntry(FlaskForm):
    revenue_date = DateField([InputRequired()])  # TODO Add DateTime validation
    revenue_value = IntegerField([InputRequired(), Regexp('[0-9.]+')])
    revenue_source = SelectField([InputRequired()])
    submit_revenue = SubmitField()


class AddSavingsEntry(FlaskForm):
    savings_date = DateField()
    savings_value = IntegerField()
    savings_source = SelectField()
    savings_reason = SelectField()
    savings_action = SelectField()
    submit_savings = SubmitField()


class AddUtilitiesEntry(FlaskForm):
    utilities_date = DateField()
    utilities_rent = IntegerField()
    utilities_energy = IntegerField()
    utilities_satellite = IntegerField()
    utilities_maintenance = IntegerField()
    utilities_details = TextAreaField()
    submit_utilities = SubmitField()


class AddValidationItems(FlaskForm):
    category_value = SelectField(coerce=str)
    item_value = TextField()
    submit_items = SubmitField()


class AddValidationCategory(FlaskForm):
    category_value = TextField()
    submit_category = SubmitField()


class AddValidationSources(FlaskForm):
    source_value = TextField()
    submit_source = SubmitField()


class AddValidationAccounts(FlaskForm):
    account_value = TextField()
    submit_account = SubmitField()


class AddValidationActions(FlaskForm):
    action_value = TextField()
    submit_action = SubmitField()


class AddValidationReason(FlaskForm):
    reason_value = TextField()
    submit_reason = SubmitField()


@bp.route('/')
@login_required
def summary():
    return render_template('budget/summary.html', _object=BudgetDbConnector())


# TODO introduce validation within wtforms or some other way to catch possible errors


@bp.route('/new-expense-entry', methods=('GET', 'POST'))
@login_required
def add_expense_entry():

    db = get_db()
    budget_connect = BudgetDbConnector()
    expense_form = AddExpenseEntry()

    items = budget_connect.query_validation_items
    items_set = [x['items'] for x in items]
    expense_form.expense_item.choices = items_set

    item_categories = budget_connect.query_validation_categories
    item_categories_set = [x['categories'] for x in item_categories]
    expense_form.expense_category.choices = item_categories_set

    sources = budget_connect.query_validation_sources
    sources_set = [x['sources'] for x in sources]
    expense_form.expense_source.choices = sources_set

    if request.method == 'POST':

        if expense_form.is_submitted() and expense_form.validate_on_submit():

            date = expense_form.expense_date.data
            item = expense_form.expense_item.data
            value = expense_form.expense_value.data
            item_category = expense_form.expense_category.data
            source = expense_form.expense_source.data

            form_validated_message('All values validate!')

            budget_connect.insert_expense(date, item, value, item_category, source)
            db.commit()

            return redirect(url_for('budget.add_expense_entry'))

        elif not expense_form.validate_on_submit():

            if not expense_form.expense_date.data or not expense_form.expense_value.data:
                form_error_message('Please provide a valid date and/or valid value integer number.')

            return redirect(url_for('budget.add_expense_entry'))

    return render_template('budget/expense.html', expense_form=expense_form, _object=budget_connect)


@bp.route('/new-revenue-entry', methods=('GET', 'POST'))
@login_required
def add_revenue_entry():

    db = get_db()
    budget_connect = BudgetDbConnector()
    revenue_form = AddRevenueEntry()

    sources = budget_connect.query_validation_sources
    sources_set = [x['sources'] for x in sources]
    revenue_form.revenue_source.choices = sources_set

    if request.method == 'POST':

        if revenue_form.is_submitted() and revenue_form.submit_revenue.data:

            date = revenue_form.revenue_date.data
            revenue = revenue_form.revenue_value.data
            source = revenue_form.revenue_source.data

            budget_connect.insert_revenue(date, revenue, source)
            db.commit()

            return redirect(url_for('budget.add_revenue_entry'))

    return render_template('budget/revenue.html', revenue_form=revenue_form, _object=budget_connect)


@bp.route('/new-savings-entry', methods=('GET', 'POST'))
@login_required
def add_savings_entry():

    db = get_db()
    savings_form = AddSavingsEntry()
    budget_connect = BudgetDbConnector()

    sources = budget_connect.query_validation_sources
    sources_set = [x['sources'] for x in sources]
    savings_form.savings_source.choices = sources_set

    reasons = budget_connect.query_validation_savings_reason
    reasons_set = [x['savings_reason'] for x in reasons]
    savings_form.savings_reason.choices = reasons_set

    actions = budget_connect.query_validation_savings_action_types
    action_set = [x['savings_action_types'] for x in actions]
    savings_form.savings_action.choices = action_set

    if request.method == 'POST':

        date = savings_form.savings_date.data
        value = savings_form.savings_value.data
        source = savings_form.savings_source.data
        reason = savings_form.savings_reason.data
        action = savings_form.savings_action.data

        if savings_form.is_submitted() and savings_form.submit_savings.data:
            budget_connect.insert_savings(date, value, source, reason, action)
            db.commit()
            return redirect(url_for('budget.add_savings_entry'))

    return render_template('budget/savings.html', savings_form=savings_form, _object=budget_connect)


@bp.route('/validation', methods=('GET', 'POST'))
@login_required
def validation():

    db = get_db()
    budget_connect = BudgetDbConnector()

    items_form = AddValidationItems()
    categories_form = AddValidationCategory()
    sources_form = AddValidationSources()
    accounts_form = AddValidationAccounts()
    actions_form = AddValidationActions()
    reasons_form = AddValidationReason()

    categories = budget_connect.query_validation_categories
    category_set = [(x['categories']) for x in categories]
    items_form.category_value.choices = category_set

    # better-me the SelectField item allocation in the database works. But, the selected option
    #   is not actually visible when selected.
    # TODO add Green Card confirmation when a valid database addition has been successful

    if request.method == 'POST':

        if items_form.is_submitted() and items_form.submit_items.data:

            item = items_form.item_value.data
            category = items_form.category_value.data

            try:
                budget_connect.insert_validation_items(item, category)
                db.commit()
            except db.IntegrityError:
                error = f'item with name {item} already exists.'
                flash(error)

            return redirect(url_for('budget.validation'))

        if categories_form.is_submitted() and categories_form.submit_category.data:
            categories = categories_form.category_value.data

            try:
                budget_connect.insert_validation_categories(categories)
                db.commit()
            except db.IntegrityError:
                error = f'category with name {categories} already exists.'
                flash(error)

            return redirect(url_for('budget.validation'))

        if sources_form.is_submitted() and sources_form.submit_source.data:
            sources = sources_form.source_value.data

            try:
                budget_connect.insert_validation_sources(sources)
                db.commit()
            except db.IntegrityError:
                error = f'source with value {sources} already exists.'
                flash(error)

            return redirect(url_for('budget.validation'))

        if accounts_form.is_submitted() and accounts_form.submit_account.data:
            accounts = accounts_form.account_value.data

            try:
                budget_connect.insert_validation_accounts(accounts)
                db.commit()
            except db.IntegrityError:
                error = f'account with value {accounts} already exists.'
                flash(error)

            return redirect(url_for('budget.validation'))

        if actions_form.is_submitted() and actions_form.submit_action.data:
            actions = actions_form.action_value.data

            try:
                budget_connect.insert_validation_actions(actions)
                db.commit()
            except db.IntegrityError:
                error = f'actions with value {actions} already exists.'
                flash(error)

            return redirect(url_for('budget.validation'))

        if reasons_form.is_submitted() and reasons_form.submit_reason.data:
            reasons = reasons_form.reason_value.data

            try:
                budget_connect.insert_validation_reasons(reasons)
                db.commit()
            except db.IntegrityError:
                error = f'reasons with value {reasons} already exists.'
                flash(error)

            return redirect(url_for('budget.validation'))

    return render_template('budget/validation.html', _object=budget_connect,
                           items_form=items_form,
                           categories_form=categories_form,
                           sources_form=sources_form,
                           accounts_form=accounts_form,
                           actions_form=actions_form,
                           reasons_form=reasons_form)


@bp.route('/add_utilities_entry', methods=('GET', 'POST'))
@login_required
def add_utilities_entry():

    db = get_db()
    budget_connect = BudgetDbConnector()
    utilities_form = AddUtilitiesEntry()

    if request.method == 'POST':
        if utilities_form.is_submitted() and utilities_form.submit_utilities.data:

            date = utilities_form.utilities_date.data
            rent = utilities_form.utilities_rent.data
            energy = utilities_form.utilities_energy.data
            satellite = utilities_form.utilities_satellite.data
            maintenance = utilities_form.utilities_maintenance.data
            details = utilities_form.utilities_details.data

            budget_connect.insert_utilities(date, rent, energy, satellite, maintenance, details)
            db.commit()

            return redirect(url_for('budget.add_utilities_entry'))

    return render_template('budget/utilities.html', _object=budget_connect, utilities_form=utilities_form)


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update_entry():
    return render_template('budget/update.html')
    pass


@login_required
@bp.route('/statistics')
def statistics():
    return render_template('budget/statistics.html')
    pass


@bp.route('/report')
@login_required
def report():
    return render_template('budget/report.html')
    pass


@bp.route('/lookup')
@login_required
def lookup():
    return render_template('budget/lookup.html')
    pass
