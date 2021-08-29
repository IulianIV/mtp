from flask import (
    Blueprint, flash, redirect, render_template, request, url_for,
)
from flask_wtf import FlaskForm
from mtp.auth import login_required
from mtp.db import get_db
from wtforms.fields import SubmitField, TextField, SelectField, DateField, IntegerField


bp = Blueprint('budget', __name__, url_prefix='/budget')

# @bp.route('/budget/index')
# @login_required
# def index():
#     return render_template('budget/index.html')
#     pass


# Class object for handling multiple SQL queries, might be useful in cases where above code does not work

class BudgetDbConnector:
    def __init__(self):
        self.db = get_db()

    @property
    def query_expense_entries(self):
        return self.db.execute(
            'SELECT id, expense_date, expense_item, expense_value, expense_item_category, expense_source'
            ' FROM budget_expense '
            'ORDER BY expense_date ASC'
        )

    @property
    def query_revenue_entries(self):
        return self.db.execute(
            'SELECT id, revenue_date, revenue_value, revenue_source'
            ' FROM budget_revenue '
            'ORDER BY revenue_date ASC'
        )

    @property
    def query_savings_entries(self):
        return self.db.execute(
            'SELECT id, savings_date,savings_value, savings_source, savings_reason, savings_action'
            ' FROM budget_savings '
            'ORDER BY savings_date ASC'
        )

    @property
    def query_validation_items(self):
        return self.db.execute(
            'SELECT id,items'
            ' FROM validation_items'
        )

    @property
    def query_validation_categories(self):
        return self.db.execute(
            'SELECT id,categories'
            ' FROM validation_categories'
        )

    @property
    def query_validation_savings_accounts(self):
        return self.db.execute(
            'SELECT id,savings_accounts'
            ' FROM validation_savings_accounts'
        )

    @property
    def query_validation_sources(self):
        return self.db.execute(
            'SELECT id,sources'
            ' FROM validation_sources'
        )

    @property
    def query_validation_savings_action_types(self):
        return self.db.execute(
            'SELECT id,savings_action_types'
            ' FROM validation_savings_action_types'
        )

    @property
    def query_validation_savings_reason(self):
        return self.db.execute(
            'SELECT id,savings_reason'
            ' FROM validation_savings_reason'
        )

    def insert_expense(self, date, item, value, item_category, source):
        return self.db.execute(
            'INSERT INTO budget_expense (expense_date, expense_item, '
            'expense_value, expense_item_category, expense_source)'
            'VALUES (?, ?, ?, ?, ?)', (date, item, value, item_category, source)
        )

    def insert_revenue(self, date, revenue, source):
        return self.db.execute(
                'INSERT INTO budget_revenue (revenue_date, revenue_value, revenue_source)'
                'VALUES (?, ?, ?)', (date, revenue, source)
            )

    def insert_savings(self, date, value, source, reason, action):
        return self.db.execute(
                'INSERT INTO budget_savings (savings_date, savings_value, savings_source,'
                'savings_reason, savings_action) VALUES (?, ?, ?, ?, ?)',
                (date, value, source, reason, action)
            )

    def insert_validation_items(self, item, category):
        return self.db.execute(
                     'INSERT INTO validation_items (items,category)'
                     ' VALUES (?,?)',
                     (item, category)
                 )

    def insert_validation_categories(self, categories):
        return self.db.execute(
            'INSERT INTO validation_categories (categories) VALUES (?)',
            (categories,)
        )

    def insert_validation_sources(self, sources):
        return self.db.execute(
                    'INSERT INTO validation_sources (sources)'
                    ' VALUES (?)',
                    (sources,)
        )

    def insert_validation_accounts(self, accounts):
        return self.db.execute(
                    'INSERT INTO validation_savings_accounts'
                    ' (savings_accounts) VALUES (?)',
                    (accounts,)
        )

    def insert_validation_actions(self, actions):
        return self.db.execute(
                    'INSERT INTO validation_savings_action_types (savings_action_types) VALUES (?)',
                    (actions,)
        )

    def insert_validation_reasons(self, reasons):
        return self.db.execute(
                    'INSERT INTO validation_savings_reason (savings_reason) VALUES (?)',
                    (reasons,)
        )


class AddExpenseEntry(FlaskForm):
    expense_date = DateField()
    expense_item = SelectField()
    expense_value = IntegerField()
    expense_category = SelectField()
    expense_source = SelectField()
    submit_expense = SubmitField()


class AddRevenueEntry(FlaskForm):
    revenue_date = DateField()
    revenue_value = IntegerField()
    revenue_source = SelectField()
    submit_revenue = SubmitField()


class AddSavingsEntry(FlaskForm):
    savings_date = DateField()
    savings_value = IntegerField()
    savings_source = SelectField()
    savings_reason = SelectField()
    savings_action = SelectField()
    submit_savings = SubmitField()


class AddValidationItems(FlaskForm):
    category_value = SelectField('Transportation', coerce=str)
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
    # db = get_db()
    # # query_expense_entries = db.execute(
    # #     'SELECT id, expense_date, expense_item, expense_value, expense_item_category, expense_source'
    # #     ' FROM budget_expense '
    # #     'ORDER BY expense_date ASC'
    # # ).fetchall()
    #
    # query_revenue_entries = db.execute(
    #     'SELECT id, revenue_date, revenue_value, revenue_source'
    #     ' FROM budget_revenue '
    #     'ORDER BY revenue_date ASC'
    # ).fetchall()
    #
    # query_savings_entries = db.execute(
    #     'SELECT id, savings_date,savings_value, savings_source, savings_reason, savings_action'
    #     ' FROM budget_savings '
    #     'ORDER BY savings_date ASC'
    # ).fetchall()

    return render_template('budget/summary.html', _object=BudgetDbConnector())


# TODO introduce validation within wtforms or some other way to catch possible errors


@bp.route('/new-expense-entry', methods=('GET', 'POST'))
@login_required
def add_expense_entry():

    db = get_db()
    budget_connect = BudgetDbConnector()
    expense_form = AddExpenseEntry()

    # fixme sqlite3.IntegrityError: NOT NULL constraint failed: budget_expense.expense_date

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

        if expense_form.is_submitted() and expense_form.submit_expense.data:

            date = expense_form.expense_date.data
            item = expense_form.expense_item.data
            value = expense_form.expense_value.data
            item_category = expense_form.expense_category.data
            source = expense_form.expense_source.data

            budget_connect.insert_expense(date, item, value, item_category, source)
            db.commit()

            return redirect(url_for('budget.add_expense_entry'))

    return render_template('budget/expense.html', expense_form=expense_form)


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

    return render_template('budget/revenue.html', revenue_form=revenue_form)


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

    return render_template('budget/savings.html', savings_form=savings_form)


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
