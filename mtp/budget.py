from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, Flask
)

from wtforms.fields import SubmitField, TextField, SelectField

from mtp.auth import login_required
from mtp.db import get_db

from flask_wtf import FlaskForm

bp = Blueprint('budget', __name__, url_prefix='/budget')
app = Flask(__name__)


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
    def expense_entries(self):
        return self.db.execute(
            'SELECT id, expense_date, expense_item, expense_value, expense_item_category, expense_source'
            ' FROM budget_expense '
            'ORDER BY expense_date ASC'
        )

    @property
    def revenue_entries(self):
        return self.db.execute(
            'SELECT id, revenue_date, revenue_value, revenue_source'
            ' FROM budget_revenue '
            'ORDER BY revenue_date ASC'
        )

    @property
    def savings_entries(self):
        return self.db.execute(
            'SELECT id, savings_date,savings_value, savings_source, savings_reason, savings_action'
            ' FROM budget_savings '
            'ORDER BY savings_date ASC'
        )

    @property
    def validation_items(self):
        return self.db.execute(
            'SELECT id,items'
            ' FROM validation_items'
        )

    @property
    def validation_categories(self):
        return self.db.execute(
            'SELECT categories'
            ' FROM validation_categories'
        )

    @property
    def validation_savings_accounts(self):
        return self.db.execute(
            'SELECT id,savings_accounts'
            ' FROM validation_savings_accounts'
        )

    @property
    def validation_sources(self):
        return self.db.execute(
            'SELECT id,sources'
            ' FROM validation_sources'
        )

    @property
    def validation_savings_action_types(self):
        return self.db.execute(
            'SELECT id,savings_action_types'
            ' FROM validation_savings_action_types'
        )

    @property
    def validation_savings_reason(self):
        return self.db.execute(
            'SELECT id,savings_reason'
            ' FROM validation_savings_reason'
        )


class AddValidationItems(FlaskForm):
    item_value = TextField()
    # fixme RuntimeError: Working outside of application context.
    category_values = [category for category in BudgetDbConnector().validation_items]
    category_value = SelectField(choices=category_values)
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
    # # expense_entries = db.execute(
    # #     'SELECT id, expense_date, expense_item, expense_value, expense_item_category, expense_source'
    # #     ' FROM budget_expense '
    # #     'ORDER BY expense_date ASC'
    # # ).fetchall()
    #
    # revenue_entries = db.execute(
    #     'SELECT id, revenue_date, revenue_value, revenue_source'
    #     ' FROM budget_revenue '
    #     'ORDER BY revenue_date ASC'
    # ).fetchall()
    #
    # savings_entries = db.execute(
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

    items_form = AddValidationItems()
    categories_form = AddValidationCategory()
    sources_form = AddValidationSources()
    accounts_form = AddValidationAccounts()
    actions_form = AddValidationActions()
    reasons_form = AddValidationReason()

    if request.method == 'POST':

        if items_form.is_submitted() and items_form.submit_items.data:
            item = items_form.item_value.data
            category = items_form.category_value.data

            try:
                db.execute(
                    'INSERT INTO validation_items (items,category)'
                    ' VALUES (?,?)',
                    (item, category)
                )
                db.commit()
            except db.IntegrityError:
                error = f'item with name {item} already exists.'
                flash(error)

            return redirect(url_for('budget.validation'))

        if categories_form.is_submitted() and categories_form.submit_category.data:
            categories = categories_form.category_value.data

            try:
                db.execute(
                    'INSERT INTO validation_categories (categories) VALUES (?)',
                    (categories,)
                )
                db.commit()
            except db.IntegrityError:
                error = f'category with name {categories} already exists.'
                flash(error)

            return redirect(url_for('budget.validation'))

        if sources_form.is_submitted() and sources_form.submit_source.data:
            sources = sources_form.source_value.data

            try:
                db.execute(
                    'INSERT INTO validation_sources (sources)'
                    ' VALUES (?)',
                    (sources,)
                )
                db.commit()
            except db.IntegrityError:
                error = f'source with value {sources} already exists.'
                flash(error)

            return redirect(url_for('budget.validation'))

        if accounts_form.is_submitted() and accounts_form.submit_account.data:
            accounts = accounts_form.account_value.data

            try:
                db.execute(
                    'INSERT INTO validation_savings_accounts'
                    ' (savings_accounts) VALUES (?)',
                    (accounts,)
                )
                db.commit()
            except db.IntegrityError:
                error = f'account with value {accounts} already exists.'
                flash(error)

            return redirect(url_for('budget.validation'))

        if actions_form.is_submitted() and actions_form.submit_action.data:
            actions = actions_form.action_value.data

            try:
                db.execute(
                    'INSERT INTO validation_savings_action_types (savings_action_types) VALUES (?)',
                    (actions,)
                )
                db.commit()
            except db.IntegrityError:
                error = f'actions with value {actions} already exists.'
                flash(error)

            return redirect(url_for('budget.validation'))

        if reasons_form.is_submitted() and reasons_form.submit_reason.data:
            reasons = reasons_form.reason_value.data

            try:
                db.execute(
                    'INSERT INTO validation_savings_reason (savings_reason) VALUES (?)',
                    (reasons,)
                )
                db.commit()
            except db.IntegrityError:
                error = f'reasons with value {reasons} already exists.'
                flash(error)

            return redirect(url_for('budget.validation'))

    return render_template('budget/validation.html', _object=BudgetDbConnector(),
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
