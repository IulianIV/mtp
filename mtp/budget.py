from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from mtp.auth import login_required
from mtp.db import get_db

bp = Blueprint('budget', __name__, url_prefix='/budget')


# @bp.route('/budget/index')
# @login_required
# def index():
#     return render_template('budget/index.html')
#     pass


@bp.route('/')
@login_required
def summary():
    db = get_db()
    entries = db.execute(
        'SELECT id, expense_date, expense_item, expense_value, expense_item_category, expense_source'
        ' FROM budget_expense'
        ' ORDER BY expense_date ASC'
    ).fetchall()

    return render_template('budget/summary.html', entries=entries)


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
            return redirect(url_for('budget.summary'))

        flash(error)
    return render_template('budget/expense.html')


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
            error = 'Source if required'
        elif error is None:
            db.execute(
                'INSERT INTO budget_revenue (revenue_date, revenue_value, revenue_source)'
                'VALUES (?, ?, ?)', (date, revenue, source)
            )
            db.commit()
            return redirect(url_for('budget.summary'))

        flash(error)

    return render_template('budget/revenue.html')


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
            error = 'Value is required'
        elif not source:
            error = 'Source is required'
        elif not reason:
            error = 'Reason is required'
        elif not action:
            error = 'Action is required'
        elif error is None:
            db.execute(
                'INSERT INTO budget_savings (savings_date, savings_value, savings_source'
                'savings_reasons, savings_action) VALUES (?, ?, ?, ?, ?)',
                (date, value, source, reason, action)
            )
            db.commit()
            return redirect(url_for('budget.summary'))

        flash(error)

    return render_template('budget/savings.html')
