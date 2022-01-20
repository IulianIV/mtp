from urllib.parse import parse_qs, urlparse

import pandas as pd
from flask import render_template
from flask_login import current_user

from app.analytics import bp
from app.manager.db.db_interrogations import *


# TODO Add DataTables filtering to utm-stats table.


@bp.route('/')
def lifetime_expense():
    expense_raw_data = query_expense_entries(user_id=current_user.get_id())

    expense_dict = {'expense_value': [expense.expense_value for expense in expense_raw_data]}

    expense_data_df = pd.DataFrame(data=expense_dict)
    lifetime_expense_total = expense_data_df.sum(numeric_only=True)
    print(expense_data_df)
    print(lifetime_expense_total)

    return render_template('analytics/analytics.html')


@bp.route('/budget-tables')
def budget_tables():

    budget_queries = {
        'expense_entries': query_expense_entries(user_id=current_user.get_id()),
        'revenue_entries': query_revenue_entries(user_id=current_user.get_id()),
        'savings_entries': query_savings_entries(user_id=current_user.get_id()),
        'utilities_entries': query_utilities_entries(user_id=current_user.get_id()),

    }
    table_counts = {
            'expense_count': get_expense_count(user_id=current_user.get_id()),
            'revenue_count': get_revenue_count(user_id=current_user.get_id()),
            'savings_count': get_savings_count(user_id=current_user.get_id()),
            'utilities_count': get_utilities_count(user_id=current_user.get_id())
        }

    validation_counts = {
        'validation_categories': get_validation_categories_count(),
        'validation_items': get_validation_items_count(),
        'validation_accounts': get_validation_accounts_count(),
        'validation_reason': get_validation_reason_count(),
        'validation_sources': get_validation_sources_count()
    }

    return render_template('analytics/budget_tables.html', budget_queries=budget_queries, table_counts=table_counts,
                           validation_counts=validation_counts)


@bp.route('/utm-stats')
def utm_stats():
    raw_entries = get_parsed_urls(user_id=current_user.get_id())
    num_of_params = []
    most_params = 0
    all_values_dict = {'date': [], 'url': [], 'qs': [], 'netloc': []}

    for entry in raw_entries:
        date = entry.url_date
        url = entry.raw_url
        parsed_url = urlparse(url)
        url_domain = parsed_url.netloc
        raw_url_query = parse_qs(parsed_url.query)

        num_of_params.append(len(raw_url_query))
        most_params = max(num_of_params)

        all_values_dict['date'].append(date)
        all_values_dict['url'].append(url)
        all_values_dict['qs'].append(raw_url_query)
        all_values_dict['netloc'].append(url_domain)

    return render_template('analytics/utm_stats.html', url_data=all_values_dict,
                           most_params=most_params)


# fixme To be removed in the future when module is implemented. Exists only for communication purposes
@bp.route('/utm-analyzer-template')
def utm_analyzer():

    return render_template('analytics/test_utm_analyzer.html')
