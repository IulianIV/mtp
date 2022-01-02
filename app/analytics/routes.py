import io
import random
from urllib.parse import parse_qs, urlparse

import pandas as pd
from flask import render_template, Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

from app.analytics import bp
from app.manager.db.db_interrogations import *


# TODO Add DataTables filtering to utm-stats table.


@bp.route('/')
def lifetime_expense():
    expense_raw_data = query_expense_entries()

    expense_dict = {'expense_value': [expense.expense_value for expense in expense_raw_data]}

    expense_data_df = pd.DataFrame(data=expense_dict)
    lifetime_expense_total = expense_data_df.sum(numeric_only=True)
    print(expense_data_df)
    print(lifetime_expense_total)

    return render_template('analytics/analytics.html')


# better-me maybe find a better name for this function and its template?
@bp.route('/budget-tables')
def budget_tables():

    budget_queries = {
        'expense_entries': query_expense_entries(),
        'revenue_entries': query_revenue_entries(),
        'savings_entries': query_savings_entries(),

    }
    table_counts = {
            'expense_count': get_expense_count(),
            'revenue_count': get_revenue_count(),
            'savings_count': get_savings_count()
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
    raw_entries = get_parsed_urls()
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

    fig = create_figure()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)

    return render_template('analytics/utm_stats.html', output=output.getvalue(), url_data=all_values_dict,
                           most_params=most_params, mimetype='image/png')


@bp.route('/plot.png')
def plot_png():
    fig = create_figure()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


def create_figure():
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    xs = range(100)
    ys = [random.randint(1, 50) for x in xs]
    axis.plot(xs, ys)
    return fig


# fixme To be removed in the future when module is implemented. Exists only for communication purposes
@bp.route('/utm-analyzer-template')
def utm_analyzer():

    return render_template('analytics/test_utm_analyzer.html')
