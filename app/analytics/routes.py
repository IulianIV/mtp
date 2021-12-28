import pandas as pd
from flask import render_template

from app.analytics import bp
from app.manager.db.db_interrogations import *

db_queries = Query()


@bp.route('/')
def lifetime_expense():
    expense_raw_data = db_queries.query_expense_entries()

    expense_dict = {'expense_value': [expense.expense_value for expense in expense_raw_data]}

    expense_data_df = pd.DataFrame(data=expense_dict)
    lifetime_expense_total = expense_data_df.sum(numeric_only=True)
    print(expense_data_df)
    print(lifetime_expense_total)

    return render_template('analytics/analytics.html')
