from flask import (
    Blueprint, flash, redirect, render_template, request, url_for,
)
from flask_wtf import FlaskForm
from mtp.auth import login_required
from mtp.db import get_db
from wtforms.fields import SubmitField, TextField, SelectField


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


"""
Form catcher that adds entries to `budget_expense` database 

"""


@bp.route('/new-expense-entry', methods=('GET', 'POST'))
@login_required
def add_expense_entry():
    if request.method == 'POST':
        date = request.form['date']
        item = request.form['item']
        value = request.form['value']
        item_category = request.form['category']
        source = request.form['source']
        db = get_db()
        error = None

        if not date:
            error = 'Date is required.'
        elif not item:
            error = 'Item is required'
        elif not value:
            error = 'Value is required'
        elif not item_category:
            error = 'Item Category is required'
        elif not source:
            error = 'Source is required'
        elif error is None:
            db.execute(
                'INSERT INTO budget_expense (expense_date, expense_item, '
                'expense_value, expense_item_category, expense_source)'
                'VALUES (?, ?, ?, ?, ?)', (date, item, value, item_category, source)
            )
            db.commit()
            return redirect(url_for('budget.add_expense_entry'))

        flash(error)
    return render_template('budget/expense.html', _object=BudgetDbConnector())


"""
Form catcher that adds entries to `budget_revenue` database 

"""


class RevenueForm(FlaskForm):
    pass
    # date = DateField('date', validators=DataRequired())
    # revenue = IntegerField('revenue', validators=DataRequired())
    # source = StringField('source', validators=DataRequired())


@bp.route('/new-revenue-entry', methods=('GET', 'POST'))
@login_required
def add_revenue_entry():
    if request.method == 'POST':
        date = request.form['date']
        revenue = request.form['revenue']
        source = request.form['source']
        db = get_db()
        error = None

        if not date:
            error = 'Date is required'
        elif not revenue:
            error = 'Revenue is required'
        elif not source:
            error = 'Source is required'
        elif error is None:
            db.execute(
                'INSERT INTO budget_revenue (revenue_date, revenue_value, revenue_source)'
                'VALUES (?, ?, ?)', (date, revenue, source)
            )
            db.commit()
            return redirect(url_for('budget.add_revenue_entry'))

        flash(error)

    return render_template('budget/revenue.html', _object=BudgetDbConnector())


"""
Form catcher that adds entries to `budget_savings` database 

"""


@bp.route('/new-savings-entry', methods=('GET', 'POST'))
@login_required
def add_savings_entry():
    if request.method == 'POST':
        date = request.form['date']
        value = request.form['value']
        source = request.form['source']
        reason = request.form['reason']
        action = request.form['action']
        db = get_db()
        error = None

        if not date:
            error = 'Date is required'
        elif not value:
            error = '"Value" is required'
        elif not source:
            error = 'Source is required'
        elif not reason:
            error = 'Reason is required'
        elif not action:
            error = 'Action is required'
        elif error is None:
            db.execute(
                'INSERT INTO budget_savings (savings_date, savings_value, savings_source,'
                'savings_reason, savings_action) VALUES (?, ?, ?, ?, ?)',
                (date, value, source, reason, action)
            )
            db.commit()
            return redirect(url_for('budget.add_savings_entry'))

        flash(error)

    return render_template('budget/savings.html', _object=BudgetDbConnector())


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
    category_set = [(x['categories'], x['categories']) for x in categories]
    items_form.category_value.choices = category_set

    # better-me the SelectField item allocation in the database works. But, the selected option
    #   is not actually visible when selected.

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
