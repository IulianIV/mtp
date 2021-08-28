from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)

from mtp.auth import login_required
from mtp.db import get_db

from flask_wtf import FlaskForm


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

    #
    # validation_items = db.execute(
    #     'SELECT items'
    #     ' FROM validation_items'
    # ).fetchall()
    #
    # validation_categories = db.execute(
    #     'SELECT categories'
    #     ' FROM validation_categories'
    # ).fetchall()
    #
    # validation_savings_accounts = db.execute(
    #     'SELECT savings_accounts'
    #     ' FROM validation_savings_accounts'
    # ).fetchall()
    #
    # validation_sources = db.execute(
    #     'SELECT sources'
    #     ' FROM validation_sources'
    # ).fetchall()
    #
    # validation_savings_action_types = db.execute(
    #     'SELECT savings_action_types'
    #     ' FROM validation_savings_action_types'
    # ).fetchall()
    #
    # validation_savings_reason = db.execute(
    #     'SELECT savings_reason'
    #     ' FROM validation_savings_reason'
    # ).fetchall()

    if request.method == 'POST':
        categories = request.form['categories']
        items = request.form['items']
        source = request.form['sources']
        accounts = request.form['accounts']
        actions = request.form['actions']
        reasons = request.form['reason']

        error = None

        if not items:
            error = 'An item must be added'
        elif not categories:
            error = 'Item category must be set.'
        elif not source:
            error = 'Source is required'
        elif not reasons:
            error = 'Reason for transaction'
        elif not actions:
            error = 'Action is required'
        elif not accounts:
            error = 'An account must be chosen'
        elif error is None:

            try:
                db.execute(
                    'INSERT INTO validation_categories (categories) VALUES (?)',
                    (categories,)
                )
                db.commit()
            except db.IntegrityError:
                error = f'category with name {categories} already exists.'
                flash(error)

            try:
                db.execute(
                    'INSERT INTO validation_items (items,category)'
                    ' VALUES (?,?)',
                    (items, categories)
                )
                db.commit()
            except db.IntegrityError:
                error = f'item with name {items} already exists.'
                flash(error)

            try:
                db.execute(
                    'INSERT INTO validation_sources (sources)'
                    ' VALUES (?)',
                    (source,)
                )
                db.commit()
            except db.IntegrityError:
                error = f'source with value {source} already exists.'
                flash(error)

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

            try:
                db.execute(
                    'INSERT INTO validation_savings_action_types (savings_action_types) VALUES (?)',
                    (actions,)
                )
                db.commit()

                db.execute(
                    'INSERT INTO validation_savings_reason (savings_reason) VALUES (?)',
                    (reasons,)
                )
                db.commit()
            except db.IntegrityError:
                error = f'reasons with value {reasons} already exists.'
                flash(error)

            return redirect(url_for('budget.validation'))

        flash(error)

    return render_template('budget/validation.html', _object=BudgetDbConnector())


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
