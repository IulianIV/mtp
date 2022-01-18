from flask import (
    request, redirect
)
from flask_login import current_user

from app.api import bp
from app.manager.db.db_interrogations import *


# fixme it is now basically inaccessible form the FE.
#   accessing the /api/data URL with '?loc_path="{url_from_table_map_encoded}"' renders the page as it triggers and
#   bypassing the functionality. Fix this.
# better-me try to reduce cohesion of current function. A more dynamic if choice?
#   anyhow, create an endpoint for utm-stats

@bp.route('/data', methods=['GET'])
def data():

    # get current path
    if request.args.get('loc_path', type=str):
        current_loc = request.args.get('loc_path', type=str)
    else:
        return redirect(url_for('budget.summary'))

    table_map = {
        '/budget/new-expense-entry': {
            'table': BudgetExpense,
            'query': BudgetExpense.query.filter_by(user_id=current_user.get_id()),
            'sort_by': ['expense_date', 'expense_item', 'expense_value'],
            'default_sort': 'expense_date'
        },
        '/budget/new-revenue-entry': {
            'table': BudgetRevenue,
            'query': BudgetRevenue.query.filter_by(user_id=current_user.get_id()),
            'sort_by': ['revenue_date', 'revenue_value'],
            'default_sort': 'revenue_date'
        },
        '/budget/new-savings-entry': {
            'table': BudgetSaving,
            'query': BudgetSaving.query.filter_by(user_id=current_user.get_id()),
            'sort_by': ['saving_date', 'saving_value'],
            'default_sort': 'saving_date'
        },
        # better-me this seems so show the whole number of entries from the table, from all users.
        #   filtering doesn't seem to help.
        '/budget/new_utilities_entry': {
            'table': BudgetUtilities,
            'query': BudgetUtilities.query.filter_by(user_id=current_user.get_id()),
            'sort_by': ['utilities_date', 'utilities_rent_value',
                        'utilities_energy_value', 'utilities_satellite_value',
                        'utilities_maintenance_value'],
            'default_sort': 'utilities_date'
        }
    }

    query = table_map[current_loc]['query']

    # search filter
    search = request.args.get('search[value]')
    if search:
        if current_loc == '/budget/new-expense-entry':
            query = query.filter(db.or_(
                BudgetExpense.expense_date.like(f'%{search}%'),
                BudgetExpense.expense_item.like(f'%{search}%'),
                BudgetExpense.expense_item_category.like(f'%{search}%')
            )).filter_by(user_id=current_user.get_id())
        elif current_loc == '/budget/new-revenue-entry':
            query = query.filter(db.or_(
                BudgetRevenue.revenue_date.like(f'%{search}%')
            )).filter_by(user_id=current_user.get_id())
        elif current_loc == '/budget/new-savings-entry':
            query = query.filter(db.or_(
                BudgetSaving.saving_date.like(f'%{search}%'),
                BudgetSaving.saving_reason.like(f'%{search}%')
            )).filter_by(user_id=current_user.get_id())
        elif current_loc == '/budget/new_utilities_entry':
            query = query.filter(db.or_(
                BudgetUtilities.utilities_date.like(f'%{search}%'),
                BudgetUtilities.utilities_info.like(f'%{search}%')
            )).filter(BudgetUtilities.user_id == current_user.get_id())

    total_filtered = query.count()

    # sorting
    order = []
    i = 0
    while True:
        col_index = request.args.get(f'order[{i}][column]')
        if col_index is None:
            break
        col_name = request.args.get(f'columns[{col_index}][data]')
        if col_name not in table_map[current_loc]['sort_by']:
            col_name = table_map[current_loc]['default_sort']
        descending = request.args.get(f'order[{i}][dir]') == 'desc'
        col = getattr(table_map[current_loc]['table'], col_name)
        if descending:
            col = col.desc()
        order.append(col)
        i += 1
    if order:
        query = query.filter_by(user_id=current_user.get_id()).order_by(*order)

    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    query = query.filter_by(user_id=current_user.get_id()).offset(start).limit(length)

    # response
    return {
        'data': [items.to_dict() for items in query],
        'recordsFiltered': total_filtered,
        'recordsTotal': table_map[current_loc]['table'].query.filter_by(user_id=current_user.get_id()).count(),
        'draw': request.args.get('draw', type=int)
    }


@bp.route('/data/summary-graph/categories', methods=['GET'])
def summary_graph_categories_data():
    user_id = current_user.get_id()
    category_data = [x for x in get_expense_count_by_category(user_id)]

    categories_data = []

    count = [int(x[0]) for x in category_data]
    categories = [x[1] for x in category_data]

    for item in range(len(categories)):
        categories_data.append({'group': '{}'.format(categories[item]), 'value': '{}'.format(count[item])})

    return {
        'data': categories_data
    }


@bp.route('/data/summary-graph/items', methods=['GET'])
def summary_graph_items_data():
    user_id = current_user.get_id()

    item_data = [x for x in get_expense_count_by_item(user_id)]

    items_data = []

    count = [int(x[0]) for x in item_data]
    items = [x[1] for x in item_data]

    for item in range(len(items)):
        items_data.append({'group': '{}'.format(items[item]), 'value': '{}'.format(count[item])})

    return {
        'data': items_data
    }
