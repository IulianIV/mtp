from flask import (
    request
)
from app.manager.db.models import BudgetExpense
from app.api import bp
from app import db


# TODO move toa  different file in the project
#   not doing so will significantly increase the file length
#   leading to difficult administration.
#   having all server-side table management in a different file is recommended
# better-me do something so that this data is only visible only to admins for debugging


@bp.route('/expense-data', methods=('GET', 'POST'))
def data():
    query = BudgetExpense.query

    # search filter
    search = request.args.get('search[value]')
    if search:
        query = query.filter(db.or_(
            BudgetExpense.expense_date.like(f'%{search}%'),
            BudgetExpense.expense_item.like(f'%{search}%'),
            BudgetExpense.expense_item_category.like(f'%{search}%')
        ))

    total_filtered = query.count()

    # sorting
    order = []
    i = 0
    while True:
        col_index = request.args.get(f'order[{i}][column]')
        if col_index is None:
            break
        col_name = request.args.get(f'columns[{col_index}][data]')
        if col_name not in ['expense_date', 'expense_item', 'expense_value']:
            col_name = 'expense_date'
        descending = request.args.get(f'order[{i}][dir]') == 'desc'
        col = getattr(BudgetExpense, col_name)
        if descending:
            col = col.desc()
        order.append(col)
        i += 1
    if order:
        query = query.order_by(*order)

    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('end', type=int)
    query = query.offset(start).limit(length)

    # response
    return {
        'data': [user.to_dict() for user in query],
        'recordsFiltered': total_filtered,
        'recordsTotal': BudgetExpense.query.count(),
        'draw': request.args.get('draw', type=int)
    }

