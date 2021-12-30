import io
import random
from urllib.parse import parse_qs, urlparse

import pandas as pd
from flask import render_template, Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

from app.analytics import bp
from app.manager.db.db_interrogations import *

db_queries = Query()

# TODO Add DataTables filtering to utm-stats table.


@bp.route('/')
def lifetime_expense():
    expense_raw_data = db_queries.query_expense_entries()

    expense_dict = {'expense_value': [expense.expense_value for expense in expense_raw_data]}

    expense_data_df = pd.DataFrame(data=expense_dict)
    lifetime_expense_total = expense_data_df.sum(numeric_only=True)
    print(expense_data_df)
    print(lifetime_expense_total)

    return render_template('analytics/analytics.html')


@bp.route('/utm-stats')
def utm_stats():
    raw_entries = db_queries.get_parsed_urls()
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
