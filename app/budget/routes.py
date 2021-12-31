from datetime import datetime
from flask import (
    redirect, render_template, request, url_for
)
from app.auth.routes import login_required
from app.manager.db.db_interrogations import Query, Insert
from app.manager.protection import CustomCSRF, form_validated_message, form_error_message
from app.budget import forms
from wtforms.validators import ValidationError
from app.budget import bp
from app import db

custom_protection = CustomCSRF()
db_queries = Query()
db_inserts = Insert()


# TODO Add RON to EUR Conversion by passing already converted values to template then process them with AJAX when box
#   is checked
@bp.route('/')
@login_required
def summary():

    now = datetime.now()

    display_date = now.strftime('%B, ') + now.strftime('%Y')

    current_month_revenue_values = db_queries.get_current_month_revenue()
    total_current_month_revenue = sum(current_month_revenue_values[x][0] for x
                                      in range(len(current_month_revenue_values)))

    summary_data = {
        'date': display_date,
        'current_month_total_expense': total_current_month_revenue
    }

    return render_template('budget/summary.html', summary_data=summary_data )


@bp.route('/new-expense-entry', methods=('GET', 'POST'))
@login_required
def add_expense_entry():
    expense_form = forms.AddExpenseEntry()

    table_counts = {
        'expense_count': db_queries.get_expense_count()
    }

    items = db_queries.query_validation_items()
    items_set = [x['items'] for x in items]
    expense_form.expense_item.choices = items_set

    item_categories = db_queries.query_validation_categories()
    item_categories_set = [x['categories'] for x in item_categories]
    expense_form.expense_category.choices = item_categories_set

    sources = db_queries.query_validation_sources()
    sources_set = [x['sources'] for x in sources]
    expense_form.expense_source.choices = sources_set

    if expense_form.is_submitted() and expense_form.validate_on_submit():

        date = expense_form.expense_date.data
        item = expense_form.expense_item.data
        value = expense_form.expense_value.data
        item_category = expense_form.expense_category.data
        source = expense_form.expense_source.data

        form_validated_message('All values validated!')

        db_inserts.insert_expense(date, item, value, item_category, source)
        db.session.commit()

        return redirect(url_for('budget.add_expense_entry'))

    return render_template('budget/expense.html', expense_form=expense_form, db_queries=db_queries,
                           table_counts=table_counts)


@bp.route('/new-revenue-entry', methods=('GET', 'POST'))
@login_required
def add_revenue_entry():
    revenue_form = forms.AddRevenueEntry()

    table_counts = {
        'revenue_count': db_queries.get_revenue_count()
    }

    sources = db_queries.query_validation_sources()
    sources_set = [x['sources'] for x in sources]
    revenue_form.revenue_source.choices = sources_set

    if revenue_form.is_submitted() and revenue_form.validate_on_submit():

        date = revenue_form.revenue_date.data
        revenue = revenue_form.revenue_value.data
        source = revenue_form.revenue_source.data

        form_validated_message('All values validated!')

        db_inserts.insert_revenue(date, revenue, source)
        db.session.commit()

        return redirect(url_for('budget.add_revenue_entry'))

    return render_template('budget/revenue.html', revenue_form=revenue_form, db_queries=db_queries,
                           table_counts=table_counts)


@bp.route('/new-savings-entry', methods=('GET', 'POST'))
@login_required
def add_savings_entry():
    savings_form = forms.AddSavingsEntry()

    table_counts = {
        'saving_count': db_queries.get_savings_count()
    }

    sources = db_queries.query_validation_sources()
    sources_set = [x['sources'] for x in sources]
    savings_form.savings_source.choices = sources_set

    reasons = db_queries.query_validation_savings_reason()
    reasons_set = [x['saving_reason'] for x in reasons]
    savings_form.savings_reason.choices = reasons_set

    actions = db_queries.query_validation_savings_action_types()
    action_set = [x['saving_action_type'] for x in actions]
    savings_form.savings_action.choices = action_set

    if request.method == 'POST':

        if savings_form.is_submitted() and savings_form.validate_on_submit():

            date = savings_form.savings_date.data
            value = savings_form.savings_value.data
            source = savings_form.savings_source.data
            reason = savings_form.savings_reason.data
            action = savings_form.savings_action.data

            form_validated_message('All values validated!')

            db_inserts.insert_savings(date, value, source, reason, action)
            db.session.commit()
            return redirect(url_for('budget.add_savings_entry'))

        return redirect(url_for('budget.add_savings_entry'))

    return render_template('budget/savings.html', savings_form=savings_form, db_queries=db_queries,
                           table_counts=table_counts)


@bp.route('/validation', methods=('GET', 'POST'))
@login_required
def validation():

    items_form = forms.AddValidationItems()
    categories_form = forms.AddValidationCategory()
    sources_form = forms.AddValidationSources()
    accounts_form = forms.AddValidationAccounts()
    actions_form = forms.AddValidationActions()
    reasons_form = forms.AddValidationReason()

    categories = db_queries.query_validation_categories()
    category_set = [(x['categories']) for x in categories]
    items_form.category_value.choices = category_set

    return render_template('budget/validation.html', db_queries=db_queries,
                           items_form=items_form,
                           categories_form=categories_form,
                           sources_form=sources_form,
                           accounts_form=accounts_form,
                           actions_form=actions_form,
                           reasons_form=reasons_form)


@bp.route('/validation/items', methods=('GET', 'POST'))
@login_required
def validation_items():

    items_form = forms.AddValidationItems()
    categories_form = forms.AddValidationCategory()
    sources_form = forms.AddValidationSources()
    accounts_form = forms.AddValidationAccounts()
    actions_form = forms.AddValidationActions()
    reasons_form = forms.AddValidationReason()

    categories = db_queries.query_validation_categories()
    category_set = [(x['categories']) for x in categories]
    items_form.category_value.choices = category_set

    if items_form.is_submitted() and items_form.validate_on_submit():

        item = items_form.item_value.data
        category = items_form.category_value.data

        item_list = db_queries.get_validation_item(item)

        if item_list is not None and item in item_list:

            form_error_message(f'The value you chose for item: "{item}" already exists')

        elif item_list is None:

            form_validated_message('Item value validated!')
            db_inserts.insert_validation_items(item, category)
            db.session.commit()

        return redirect(url_for('budget.validation'))

    elif not items_form.validate_on_submit():

        if items_form.item_value.data:
            ValidationError(message=form_error_message('Item Value field only accepts letters and spaces.'))

        return redirect(url_for('budget.validation'))

    return render_template('budget/validation.html', db_queries=db_queries,
                           items_form=items_form,
                           categories_form=categories_form,
                           sources_form=sources_form,
                           accounts_form=accounts_form,
                           actions_form=actions_form,
                           reasons_form=reasons_form)


@bp.route('/validation/category', methods=('GET', 'POST'))
@login_required
def validation_categories():

    items_form = forms.AddValidationItems()
    categories_form = forms.AddValidationCategory()
    sources_form = forms.AddValidationSources()
    accounts_form = forms.AddValidationAccounts()
    actions_form = forms.AddValidationActions()
    reasons_form = forms.AddValidationReason()

    categories = db_queries.query_validation_categories()
    category_set = [(x['categories']) for x in categories]
    items_form.category_value.choices = category_set

    if categories_form.is_submitted() and categories_form.validate_on_submit():
        categories = categories_form.category_value.data

        category_list = db_queries.get_validation_category(categories)

        # fixme repair the login. ATM it throws an
        #  TypeError: argument of type 'ValidationSavingCategories' is not iterable

        # if category_list is not None and categories in category_list:
        #
        #     form_error_message(f'The value you chose for category: "{categories}" already exists')

        # fixme was a `elif` previous to TypeError.

        if category_list is None:
            form_validated_message('Category value validated!')
            db_inserts.insert_validation_categories(categories)
            db.session.commit()

        return redirect(url_for('budget.validation'))

    elif not categories_form.validate_on_submit():

        if categories_form.category_value.data:
            ValidationError(message=form_error_message('Category Value field only accepts letters and spaces.'))

        return redirect(url_for('budget.validation'))

    return render_template('budget/validation.html', db_queries=db_queries,
                           items_form=items_form,
                           categories_form=categories_form,
                           sources_form=sources_form,
                           accounts_form=accounts_form,
                           actions_form=actions_form,
                           reasons_form=reasons_form)


@bp.route('/validation/sources', methods=('GET', 'POST'))
@login_required
def validation_sources():

    items_form = forms.AddValidationItems()
    categories_form = forms.AddValidationCategory()
    sources_form = forms.AddValidationSources()
    accounts_form = forms.AddValidationAccounts()
    actions_form = forms.AddValidationActions()
    reasons_form = forms.AddValidationReason()

    categories = db_queries.query_validation_categories()
    category_set = [(x['categories']) for x in categories]
    items_form.category_value.choices = category_set

    if sources_form.is_submitted() and sources_form.validate_on_submit():

        sources = sources_form.source_value.data
        sources_list = db_queries.get_validation_source(sources)

        if sources_list is not None and sources in sources_list:

            form_error_message(f'The value you chose for source: "{sources}" already exists')

        elif sources_list is None:
            form_validated_message('Source value validated!')
            db_inserts.insert_validation_sources(sources)
            db.session.commit()

        return redirect(url_for('budget.validation'))

    elif not sources_form.validate_on_submit():

        if sources_form.source_value.data:
            ValidationError(message=form_error_message('Sources Value field only accepts letters and spaces.'))

        return redirect(url_for('budget.validation'))

    return render_template('budget/validation.html', db_queries=db_queries,
                           items_form=items_form,
                           categories_form=categories_form,
                           sources_form=sources_form,
                           accounts_form=accounts_form,
                           actions_form=actions_form,
                           reasons_form=reasons_form)


@bp.route('/validation/accounts', methods=('GET', 'POST'))
@login_required
def validation_accounts():

    items_form = forms.AddValidationItems()
    categories_form = forms.AddValidationCategory()
    sources_form = forms.AddValidationSources()
    accounts_form = forms.AddValidationAccounts()
    actions_form = forms.AddValidationActions()
    reasons_form = forms.AddValidationReason()

    categories = db_queries.query_validation_categories()
    category_set = [(x['categories']) for x in categories]
    items_form.category_value.choices = category_set

    if accounts_form.is_submitted() and accounts_form.validate_on_submit():
        accounts = accounts_form.account_value.data

        accounts_list = db_queries.get_validation_account(accounts)

        if accounts_list is not None and accounts in accounts_list:

            form_error_message(f'The value you chose for account: "{accounts}" already exists')

        elif accounts_list is None:
            form_validated_message('Account value validated!')
            db_inserts.insert_validation_accounts(accounts)
            db.session.commit()

        return redirect(url_for('budget.validation'))

    elif not accounts_form.validate_on_submit():

        if accounts_form.account_value.data:
            ValidationError(message=form_error_message('Account Value field only accepts letters and spaces.'))

        return redirect(url_for('budget.validation'))

    return render_template('budget/validation.html', db_queries=db_queries,
                           items_form=items_form,
                           categories_form=categories_form,
                           sources_form=sources_form,
                           accounts_form=accounts_form,
                           actions_form=actions_form,
                           reasons_form=reasons_form)


@bp.route('/validation/actions', methods=('GET', 'POST'))
@login_required
def validation_actions():

    items_form = forms.AddValidationItems()
    categories_form = forms.AddValidationCategory()
    sources_form = forms.AddValidationSources()
    accounts_form = forms.AddValidationAccounts()
    actions_form = forms.AddValidationActions()
    reasons_form = forms.AddValidationReason()

    categories = db_queries.query_validation_categories()
    category_set = [(x['categories']) for x in categories]
    items_form.category_value.choices = category_set

    if actions_form.is_submitted() and actions_form.validate_on_submit():

        actions = actions_form.action_value.data

        action_list = db_queries.get_validation_actions(actions)

        if action_list is not None and actions in action_list:

            form_error_message(f'The value you chose for action: "{actions}" already exists')

        elif action_list is None:

            form_validated_message('Action value validated!')
            db_inserts.insert_validation_actions(actions)
            db.session.commit()

        return redirect(url_for('budget.validation'))

    elif not actions_form.validate_on_submit():

        if actions_form.action_value.data:
            ValidationError(message=form_error_message('Action Value field only accepts letters and spaces.'))

        return redirect(url_for('budget.validation'))

    return render_template('budget/validation.html', db_queries=db_queries,
                           items_form=items_form,
                           categories_form=categories_form,
                           sources_form=sources_form,
                           accounts_form=accounts_form,
                           actions_form=actions_form,
                           reasons_form=reasons_form)


@bp.route('/validation/reasons', methods=('GET', 'POST'))
@login_required
def validation_reasons():

    items_form = forms.AddValidationItems()
    categories_form = forms.AddValidationCategory()
    sources_form = forms.AddValidationSources()
    accounts_form = forms.AddValidationAccounts()
    actions_form = forms.AddValidationActions()
    reasons_form = forms.AddValidationReason()

    categories = db_queries.query_validation_categories()
    category_set = [(x['categories']) for x in categories]
    items_form.category_value.choices = category_set

    if reasons_form.is_submitted() and reasons_form.validate_on_submit():

        reasons = reasons_form.reason_value.data
        reasons_list = db_queries.get_validation_reason(reasons)

        if reasons_list is not None and reasons in reasons_list:

            form_error_message(f'The value you chose for reason: "{reasons}" already exists')

        elif reasons_list is None:
            form_validated_message('Reason value validated!')
            db_inserts.insert_validation_reasons(reasons)
            db.session.commit()

        return redirect(url_for('budget.validation'))

    elif not reasons_form.validate_on_submit():

        if reasons_form.reason_value.data:
            ValidationError(message=form_error_message('Reason Value field only accepts letters and spaces.'))

        return redirect(url_for('budget.validation'))

    return render_template('budget/validation.html', db_queries=db_queries,
                           items_form=items_form,
                           categories_form=categories_form,
                           sources_form=sources_form,
                           accounts_form=accounts_form,
                           actions_form=actions_form,
                           reasons_form=reasons_form)


@bp.route('/new-utilities-entry', methods=('GET', 'POST'))
@login_required
def add_utilities_entry():
    utilities_form = forms.AddUtilitiesEntry()

    table_counts = {
        'utilities_count': db_queries.get_utilities_count()
    }

    date = utilities_form.utilities_date.data
    rent = utilities_form.utilities_rent.data
    energy = utilities_form.utilities_energy.data
    satellite = utilities_form.utilities_satellite.data
    maintenance = utilities_form.utilities_maintenance.data
    details = utilities_form.utilities_details.data

    if utilities_form.is_submitted() and utilities_form.validate_on_submit():

        form_validated_message('All values validated!')

        db_inserts.insert_utilities(date, rent, energy, satellite, maintenance, details)
        db.session.commit()

        return redirect(url_for('budget.add_utilities_entry'))

    return render_template('budget/utilities.html', db_queries=db_queries,
                           utilities_form=utilities_form, table_counts=table_counts)


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update_entry():
    return render_template('budget/update.html')
    pass


@bp.route('/report')
@login_required
def report():
    return render_template('budget/report.html')
    pass
