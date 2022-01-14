from flask import (
    redirect, render_template, request
)
from flask_login import current_user
from forex_python.converter import CurrencyRates
from wtforms.validators import ValidationError

from app.auth.routes import login_required
from app.budget import bp
from app.budget import forms
from app.manager.db.db_interrogations import *
from app.manager.protection import CustomCSRF, form_validated_message, form_error_message

custom_protection = CustomCSRF()
currency = CurrencyRates()


# TODO format dates to a more user-friendly format
# TODO Create a "transfer" view where you can initiate transfers between accounts - Spend -> saving and vice-versa.
# TODO add a way to keep track of cards
# TODO Make sure to add form_validation_error/success to all views.

@bp.route('/')
@login_required
def summary():
    user_id = current_user.get_id()

    now = datetime.now()
    display_date = now.strftime('%B, ') + now.strftime('%Y')

    current_month_revenue_values = get_current_month_data(user_id)['revenue']
    total_current_month_revenue = sum(current_month_revenue_values[x][0] for x
                                      in range(len(current_month_revenue_values)))

    current_month_expense_values = get_current_month_data(user_id)['expense']
    total_current_month_expense = sum(current_month_expense_values[x][0] for x
                                      in range(len(current_month_expense_values)))

    ec_savings_total_value = sum([x.saving_value for x in get_savings_data(user_id)['ec']])
    ed_savings_total_value = sum([x.saving_value for x in get_savings_data(user_id)['ed']])
    if_savings_total_value = sum([x.saving_value for x in get_savings_data(user_id)['if']])
    overall_savings_total = ec_savings_total_value + ed_savings_total_value + if_savings_total_value

    current_month_general_summary = [x for x in get_current_month_summary(user_id)]

    current_month_useful_money = total_current_month_revenue - get_current_month_mandatory_expense(user_id)

    current_month_spendable_money = total_current_month_revenue - total_current_month_expense

    summary_data = {
        'date': display_date,
        'current_month_total_revenue': total_current_month_revenue,
        'current_month_total_expense': total_current_month_expense,
        'ec_savings': ec_savings_total_value,
        'ed_savings': ed_savings_total_value,
        'if_savings': if_savings_total_value,
        'savings_total': overall_savings_total,
        'ec_savings_EUR': currency.convert('RON', 'EUR', ec_savings_total_value),
        'ed_savings_EUR': currency.convert('RON', 'EUR', ed_savings_total_value),
        'if_savings_EUR': currency.convert('RON', 'EUR', if_savings_total_value),
        'savings_total_EUR': currency.convert('RON', 'EUR', overall_savings_total),
        'current_month_summary': current_month_general_summary,
        'current_month_useful_money': current_month_useful_money,
        'current_month_spendable_money': current_month_spendable_money
    }

    return render_template('budget/summary.html', summary_data=summary_data)


@bp.route('/new-expense-entry', methods=('GET', 'POST'))
@login_required
def add_expense_entry():
    user_id = current_user.get_id()
    expense_form = forms.AddExpenseEntry()
    expense_entries = query_expense_entries()

    table_counts = {
        'expense_count': get_expense_count()
    }

    items = query_validation_items()
    items_set = [x['items'] for x in items]
    expense_form.expense_item.choices = items_set

    sources = query_validation_sources()
    sources_set = [x['sources'] for x in sources]
    expense_form.expense_source.choices = sources_set

    if expense_form.is_submitted() and expense_form.validate_on_submit():
        date = expense_form.expense_date.data
        item = expense_form.expense_item.data
        value = expense_form.expense_value.data
        source = expense_form.expense_source.data

        form_validated_message('All values validated!')

        insert_expense(user_id, date, item, value, source)
        db.session.commit()

        return redirect(url_for('budget.add_expense_entry'))

    return render_template('budget/budget_entry/expense.html', expense_form=expense_form,
                           expense_entries=expense_entries,
                           table_counts=table_counts)


@bp.route('/new-revenue-entry', methods=('GET', 'POST'))
@login_required
def add_revenue_entry():
    user_id = current_user.get_id()
    revenue_form = forms.AddRevenueEntry()
    revenue_entries = query_revenue_entries()

    table_counts = {
        'revenue_count': get_revenue_count()
    }

    sources = query_validation_sources()
    sources_set = [x['sources'] for x in sources]
    revenue_form.revenue_source.choices = sources_set

    if revenue_form.is_submitted() and revenue_form.validate_on_submit():
        date = revenue_form.revenue_date.data
        revenue = revenue_form.revenue_value.data
        source = revenue_form.revenue_source.data

        form_validated_message('All values validated!')

        insert_revenue(user_id, date, revenue, source)
        db.session.commit()

        return redirect(url_for('budget.add_revenue_entry'))

    return render_template('budget/budget_entry/revenue.html', revenue_form=revenue_form,
                           revenue_entries=revenue_entries,
                           table_counts=table_counts)


# TODO FIX Validation something is not right about validation fields.
@bp.route('/new-savings-entry', methods=('GET', 'POST'))
@login_required
def add_savings_entry():
    user_id = current_user.get_id()
    savings_form = forms.AddSavingsEntry()
    savings_entries = query_savings_entries()

    table_counts = {
        'saving_count': get_savings_count()
    }

    accounts = query_validation_savings_accounts()
    account_set = [x['saving_accounts'] for x in accounts]
    savings_form.savings_account.choices = account_set

    reasons = query_validation_savings_reason()
    reasons_set = [x['saving_reason'] for x in reasons]
    savings_form.savings_reason.choices = reasons_set

    actions = query_validation_savings_action_types()
    action_set = [x['saving_action_type'] for x in actions]
    savings_form.savings_action.choices = action_set

    if request.method == 'POST':

        if savings_form.is_submitted() and savings_form.validate_on_submit():
            date = savings_form.savings_date.data
            value = savings_form.savings_value.data
            account = savings_form.savings_account.data
            reason = savings_form.savings_reason.data
            action = savings_form.savings_action.data

            form_validated_message('All values validated!')

            insert_savings(user_id, date, value, account, reason, action)
            db.session.commit()
            return redirect(url_for('budget.add_savings_entry'))

        return redirect(url_for('budget.add_savings_entry'))

    return render_template('budget/budget_entry/savings.html', savings_form=savings_form,
                           savings_entries=savings_entries,
                           table_counts=table_counts)


@bp.route('/validation', methods=('GET', 'POST'))
@login_required
def validation():
    validation_entries = {
        'validation_items': query_validation_items(),
        'validation_categories': query_validation_categories(),
        'validation_sources': query_validation_sources(),
        'validation_accounts': query_validation_savings_accounts(),
        'validation_action_types': query_validation_savings_action_types(),
        'validation_reasons': query_validation_savings_reason()
    }

    items_form = forms.AddValidationItems()
    categories_form = forms.AddValidationCategory()
    sources_form = forms.AddValidationSources()
    accounts_form = forms.AddValidationAccounts()
    actions_form = forms.AddValidationActions()
    reasons_form = forms.AddValidationReason()

    categories = query_validation_categories()
    category_set = [(x['categories']) for x in categories]
    items_form.category_value.choices = category_set

    return render_template('budget/validation.html', validation_entries=validation_entries,
                           items_form=items_form,
                           categories_form=categories_form,
                           sources_form=sources_form,
                           accounts_form=accounts_form,
                           actions_form=actions_form,
                           reasons_form=reasons_form)


@bp.route('/validation/items', methods=('GET', 'POST'))
@login_required
def validation_items():
    validation_entries = {
        'validation_items': query_validation_items(),
        'validation_categories': query_validation_categories(),
        'validation_sources': query_validation_sources(),
        'validation_accounts': query_validation_savings_accounts(),
        'validation_action_types': query_validation_savings_action_types(),
        'validation_reasons': query_validation_savings_reason()
    }

    items_form = forms.AddValidationItems()
    categories_form = forms.AddValidationCategory()
    sources_form = forms.AddValidationSources()
    accounts_form = forms.AddValidationAccounts()
    actions_form = forms.AddValidationActions()
    reasons_form = forms.AddValidationReason()

    categories = query_validation_categories()
    category_set = [(x['categories']) for x in categories]
    items_form.category_value.choices = category_set

    if items_form.is_submitted() and items_form.validate_on_submit():

        item = items_form.item_value.data
        category = items_form.category_value.data

        found_item = get_validation_item(item)

        if found_item:

            form_error_message(f'The value you chose for item: "{found_item.items}" already exists')

        elif found_item is None:

            form_validated_message('Item value validated!')
            insert_validation_items(item, category)
            db.session.commit()

        return redirect(url_for('budget.validation'))

    elif not items_form.validate_on_submit():

        if items_form.item_value.data:
            ValidationError(message=form_error_message('Item Value field only accepts letters and spaces.'))

        return redirect(url_for('budget.validation'))

    return render_template('budget/validation.html', validation_entries=validation_entries,
                           items_form=items_form,
                           categories_form=categories_form,
                           sources_form=sources_form,
                           accounts_form=accounts_form,
                           actions_form=actions_form,
                           reasons_form=reasons_form)


@bp.route('/validation/category', methods=('GET', 'POST'))
@login_required
def validation_categories():
    validation_entries = {
        'validation_items': query_validation_items(),
        'validation_categories': query_validation_categories(),
        'validation_sources': query_validation_sources(),
        'validation_accounts': query_validation_savings_accounts(),
        'validation_action_types': query_validation_savings_action_types(),
        'validation_reasons': query_validation_savings_reason()
    }

    items_form = forms.AddValidationItems()
    categories_form = forms.AddValidationCategory()
    sources_form = forms.AddValidationSources()
    accounts_form = forms.AddValidationAccounts()
    actions_form = forms.AddValidationActions()
    reasons_form = forms.AddValidationReason()

    categories = query_validation_categories()
    category_set = [(x['categories']) for x in categories]
    items_form.category_value.choices = category_set

    if categories_form.is_submitted() and categories_form.validate_on_submit():
        categories = categories_form.category_value.data

        category_list = get_validation_category(categories)

        # fixme repair the login. ATM it throws an
        #  TypeError: argument of type 'ValidationSavingCategories' is not iterable

        # if category_list is not None and categories in category_list:
        #
        #     form_error_message(f'The value you chose for category: "{categories}" already exists')

        # fixme was a `elif` previous to TypeError.

        if category_list is None:
            form_validated_message('Category value validated!')
            insert_validation_categories(categories)
            db.session.commit()

        return redirect(url_for('budget.validation'))

    elif not categories_form.validate_on_submit():

        if categories_form.category_value.data:
            ValidationError(message=form_error_message('Category Value field only accepts letters and spaces.'))

        return redirect(url_for('budget.validation'))

    return render_template('budget/validation.html', validation_entries=validation_entries,
                           items_form=items_form,
                           categories_form=categories_form,
                           sources_form=sources_form,
                           accounts_form=accounts_form,
                           actions_form=actions_form,
                           reasons_form=reasons_form)


@bp.route('/validation/sources', methods=('GET', 'POST'))
@login_required
def validation_sources():
    validation_entries = {
        'validation_items': query_validation_items(),
        'validation_categories': query_validation_categories(),
        'validation_sources': query_validation_sources(),
        'validation_accounts': query_validation_savings_accounts(),
        'validation_action_types': query_validation_savings_action_types(),
        'validation_reasons': query_validation_savings_reason()
    }

    items_form = forms.AddValidationItems()
    categories_form = forms.AddValidationCategory()
    sources_form = forms.AddValidationSources()
    accounts_form = forms.AddValidationAccounts()
    actions_form = forms.AddValidationActions()
    reasons_form = forms.AddValidationReason()

    categories = query_validation_categories()
    category_set = [(x['categories']) for x in categories]
    items_form.category_value.choices = category_set

    if sources_form.is_submitted() and sources_form.validate_on_submit():

        sources = sources_form.source_value.data
        sources_list = get_validation_source(sources)

        if sources_list is not None and sources in sources_list:

            form_error_message(f'The value you chose for source: "{sources}" already exists')

        elif sources_list is None:
            form_validated_message('Source value validated!')
            insert_validation_sources(sources)
            db.session.commit()

        return redirect(url_for('budget.validation'))

    elif not sources_form.validate_on_submit():

        if sources_form.source_value.data:
            ValidationError(message=form_error_message('Sources Value field only accepts letters and spaces.'))

        return redirect(url_for('budget.validation'))

    return render_template('budget/validation.html', validation_entries=validation_entries,
                           items_form=items_form,
                           categories_form=categories_form,
                           sources_form=sources_form,
                           accounts_form=accounts_form,
                           actions_form=actions_form,
                           reasons_form=reasons_form)


@bp.route('/validation/accounts', methods=('GET', 'POST'))
@login_required
def validation_accounts():
    validation_entries = {
        'validation_items': query_validation_items(),
        'validation_categories': query_validation_categories(),
        'validation_sources': query_validation_sources(),
        'validation_accounts': query_validation_savings_accounts(),
        'validation_action_types': query_validation_savings_action_types(),
        'validation_reasons': query_validation_savings_reason()
    }

    items_form = forms.AddValidationItems()
    categories_form = forms.AddValidationCategory()
    sources_form = forms.AddValidationSources()
    accounts_form = forms.AddValidationAccounts()
    actions_form = forms.AddValidationActions()
    reasons_form = forms.AddValidationReason()

    categories = query_validation_categories()
    category_set = [(x['categories']) for x in categories]
    items_form.category_value.choices = category_set

    if accounts_form.is_submitted() and accounts_form.validate_on_submit():
        accounts = accounts_form.account_value.data

        accounts_list = get_validation_account(accounts)

        if accounts_list is not None and accounts in accounts_list:

            form_error_message(f'The value you chose for account: "{accounts}" already exists')

        elif accounts_list is None:
            form_validated_message('Account value validated!')
            insert_validation_accounts(accounts)
            db.session.commit()

        return redirect(url_for('budget.validation'))

    elif not accounts_form.validate_on_submit():

        if accounts_form.account_value.data:
            ValidationError(message=form_error_message('Account Value field only accepts letters and spaces.'))

        return redirect(url_for('budget.validation'))

    return render_template('budget/validation.html', validation_entries=validation_entries,
                           items_form=items_form,
                           categories_form=categories_form,
                           sources_form=sources_form,
                           accounts_form=accounts_form,
                           actions_form=actions_form,
                           reasons_form=reasons_form)


@bp.route('/validation/actions', methods=('GET', 'POST'))
@login_required
def validation_actions():
    validation_entries = {
        'validation_items': query_validation_items(),
        'validation_categories': query_validation_categories(),
        'validation_sources': query_validation_sources(),
        'validation_accounts': query_validation_savings_accounts(),
        'validation_action_types': query_validation_savings_action_types(),
        'validation_reasons': query_validation_savings_reason()
    }

    items_form = forms.AddValidationItems()
    categories_form = forms.AddValidationCategory()
    sources_form = forms.AddValidationSources()
    accounts_form = forms.AddValidationAccounts()
    actions_form = forms.AddValidationActions()
    reasons_form = forms.AddValidationReason()

    categories = query_validation_categories()
    category_set = [(x['categories']) for x in categories]
    items_form.category_value.choices = category_set

    if actions_form.is_submitted() and actions_form.validate_on_submit():

        actions = actions_form.action_value.data

        action_list = get_validation_actions(actions)

        if action_list is not None and actions in action_list:

            form_error_message(f'The value you chose for action: "{actions}" already exists')

        elif action_list is None:

            form_validated_message('Action value validated!')
            insert_validation_actions(actions)
            db.session.commit()

        return redirect(url_for('budget.validation'))

    elif not actions_form.validate_on_submit():

        if actions_form.action_value.data:
            ValidationError(message=form_error_message('Action Value field only accepts letters and spaces.'))

        return redirect(url_for('budget.validation'))

    return render_template('budget/validation.html', validation_entries=validation_entries,
                           items_form=items_form,
                           categories_form=categories_form,
                           sources_form=sources_form,
                           accounts_form=accounts_form,
                           actions_form=actions_form,
                           reasons_form=reasons_form)


@bp.route('/validation/reasons', methods=('GET', 'POST'))
@login_required
def validation_reasons():
    validation_entries = {
        'validation_items': query_validation_items(),
        'validation_categories': query_validation_categories(),
        'validation_sources': query_validation_sources(),
        'validation_accounts': query_validation_savings_accounts(),
        'validation_action_types': query_validation_savings_action_types(),
        'validation_reasons': query_validation_savings_reason()
    }

    items_form = forms.AddValidationItems()
    categories_form = forms.AddValidationCategory()
    sources_form = forms.AddValidationSources()
    accounts_form = forms.AddValidationAccounts()
    actions_form = forms.AddValidationActions()
    reasons_form = forms.AddValidationReason()

    categories = query_validation_categories()
    category_set = [(x['categories']) for x in categories]
    items_form.category_value.choices = category_set

    if reasons_form.is_submitted() and reasons_form.validate_on_submit():

        reasons = reasons_form.reason_value.data
        reasons_list = get_validation_reason(reasons)

        if reasons_list is not None and reasons in reasons_list:

            form_error_message(f'The value you chose for reason: "{reasons}" already exists')

        elif reasons_list is None:
            form_validated_message('Reason value validated!')
            insert_validation_reasons(reasons)
            db.session.commit()

        return redirect(url_for('budget.validation'))

    elif not reasons_form.validate_on_submit():

        if reasons_form.reason_value.data:
            ValidationError(message=form_error_message('Reason Value field only accepts letters and spaces.'))

        return redirect(url_for('budget.validation'))

    return render_template('budget/validation.html', validation_entries=validation_entries,
                           items_form=items_form,
                           categories_form=categories_form,
                           sources_form=sources_form,
                           accounts_form=accounts_form,
                           actions_form=actions_form,
                           reasons_form=reasons_form)


@bp.route('/new-utilities-entry', methods=('GET', 'POST'))
@login_required
def add_utilities_entry():
    user_id = current_user.get_id()
    utilities_form = forms.AddUtilitiesEntry()
    utilities_entries = query_utilities_entries()

    budget_sources = query_validation_sources()
    budget_sources_set = [(x['sources']) for x in budget_sources]
    utilities_form.utilities_budget_sources.choices = budget_sources_set

    table_counts = {
        'utilities_count': get_utilities_count()
    }

    date = utilities_form.utilities_date.data
    rent = utilities_form.utilities_rent.data
    energy = utilities_form.utilities_energy.data
    satellite = utilities_form.utilities_satellite.data
    maintenance = utilities_form.utilities_maintenance.data
    details = utilities_form.utilities_details.data
    budget_source = utilities_form.utilities_budget_sources.data

    if utilities_form.is_submitted() and utilities_form.validate_on_submit():
        form_validated_message('All values validated!')

        insert_utilities(user_id, date, rent, energy, satellite, maintenance, details, budget_source)
        db.session.commit()

        return redirect(url_for('budget.add_utilities_entry'))

    return render_template('budget/budget_entry/utilities.html', utilities_entries=utilities_entries,
                           utilities_form=utilities_form, table_counts=table_counts)


# TODO maybe make a better implementation of the Budget Entry Edit/Delete functionality by two different scopes:
#   1. The current model injects a HTML string when the query to the DataBase Model is made. Maybe something with
#   less cohesion can be made?
#   2. Add a general function that handles addition/deletion more dynamically.
#   i.e. eventually remove having 5 different "update" and "delete" functions for each budget entry.
# TODO ad is_validated() and or is_submitted() conditional in IF clause.
@bp.route('/utilities-update/<int:utility_id>', methods=('GET', 'POST'))
@login_required
def update_utilities_entry(utility_id):
    utility_update_form = forms.UpdateUtilitiesEntry()
    user_id = current_user.get_id()

    utilities_entry = query_utilities_entry(user_id, utility_id)

    budget_sources = query_validation_sources()
    sources_set = [(x['sources']) for x in budget_sources]
    utility_update_form.update_budget_sources.choices = sources_set

    if request.method == 'GET':

        utility_update_form.update_date.data = utilities_entry.utilities_date
        utility_update_form.update_rent.data = utilities_entry.utilities_rent_value
        utility_update_form.update_energy.data = utilities_entry.utilities_energy_value
        utility_update_form.update_satellite.data = utilities_entry.utilities_satellite_value
        utility_update_form.update_maintenance.data = utilities_entry.utilities_maintenance_value
        utility_update_form.update_details.data = utilities_entry.utilities_info
        utility_update_form.update_budget_sources.data = utilities_entry.budget_source

    if request.method == 'POST':

        date = utility_update_form.update_date.data
        rent = utility_update_form.update_rent.data
        energy = utility_update_form.update_energy.data
        satellite = utility_update_form.update_satellite.data
        maintenance = utility_update_form.update_maintenance.data
        details = utility_update_form.update_details.data
        source = utility_update_form.update_budget_sources.data

        update_utility_entry(utility_id, user_id, date, rent, energy, satellite, maintenance, details, source)

        return redirect(url_for('budget.add_utilities_entry'))

    return render_template('budget/budget_update/utilities.html', utilities_entry=utilities_entry,
                           utility_update_form=utility_update_form)


# fixme apparently the form accepts future dates.
@bp.route('/revenue-update/<int:revenue_id>', methods=('GET', 'POST'))
@login_required
def update_revenue_entries(revenue_id):
    revenue_update_form = forms.UpdateRevenueEntry()
    user_id = current_user.get_id()

    revenue_entry = query_revenue_entry(user_id, revenue_id)

    revenue_sources = query_validation_sources()
    sources_set = [(x['sources']) for x in revenue_sources]
    revenue_update_form.update_sources.choices = sources_set

    if request.method == 'GET':
        revenue_update_form.update_date.data = revenue_entry.revenue_date
        revenue_update_form.update_value.data = revenue_entry.revenue_value
        revenue_update_form.update_sources.data = revenue_entry.revenue_source

    if request.method == 'POST':
        date = revenue_update_form.update_date.data
        value = revenue_update_form.update_value.data
        source = revenue_update_form.update_sources.data

        update_revenue_entry(revenue_id, user_id, date, value, source)

        return redirect(url_for('budget.add_revenue_entry'))

    return render_template('budget/budget_update/revenue.html', revenue_entry=revenue_entry,
                           revenue_update_form=revenue_update_form)


@bp.route('/expense-update/<int:expense_id>', methods=('GET', 'POST'))
@login_required
def update_expense_entries(expense_id):
    expense_update_form = forms.UpdateExpenseEntry()
    user_id = current_user.get_id()

    expense_entry = query_expense_entry(user_id, expense_id)

    expense_sources = query_validation_sources()
    sources_set = [(x['sources']) for x in expense_sources]
    expense_update_form.update_source.choices = sources_set

    expense_items = query_validation_items()
    items_set = [(x['items']) for x in expense_items]
    expense_update_form.update_item.choices = items_set

    if request.method == 'GET':
        expense_update_form.update_date.data = expense_entry.expense_date
        expense_update_form.update_item.data = expense_entry.expense_item
        expense_update_form.update_value.data = expense_entry.expense_value
        expense_update_form.update_source.data = expense_entry.expense_source

    if request.method == 'POST':
        date = expense_update_form.update_date.data
        item = expense_update_form.update_item.data
        value = expense_update_form.update_value.data
        source = expense_update_form.update_source.data

        update_expense_entry(expense_id, user_id, date, item, value, source)

        return redirect(url_for('budget.add_expense_entry'))

    return render_template('budget/budget_update/expense.html', expense_entry=expense_entry,
                           expense_update_form=expense_update_form)


@bp.route('/saving-update/<int:saving_id>', methods=('GET', 'POST'))
@login_required
def update_saving_entries(saving_id):
    saving_update_form = forms.UpdateSavingsEntry()
    user_id = current_user.get_id()

    saving_entry = query_saving_entry(user_id, saving_id)

    saving_actions = query_validation_savings_action_types()
    actions_set = [(x['saving_action_type']) for x in saving_actions]
    saving_update_form.update_action.choices = actions_set

    saving_reasons = query_validation_savings_reason()
    reason_set = [(x['saving_reason']) for x in saving_reasons]
    saving_update_form.update_reason.choices = reason_set

    saving_accounts = query_validation_savings_accounts()
    account_set = [(x['saving_accounts']) for x in saving_accounts]
    saving_update_form.update_account.choices = account_set

    if request.method == 'GET':
        saving_update_form.update_date.data = saving_entry.saving_date
        saving_update_form.update_value.data = saving_entry.saving_value
        saving_update_form.update_account.data = saving_entry.saving_source
        saving_update_form.update_reason.data = saving_entry.saving_reason
        saving_update_form.update_action.data = saving_entry.saving_action

    if request.method == 'POST':
        date = saving_update_form.update_date.data
        value = saving_update_form.update_value.data
        account = saving_update_form.update_account.data
        reason = saving_update_form.update_reason.data
        action = saving_update_form.update_action.data

        update_saving_entry(saving_id, user_id, date, value, account, reason, action)

        return redirect(url_for('budget.add_savings_entry'))

    return render_template('budget/budget_update/saving.html', saving_entry=saving_entry,
                           saving_update_form=saving_update_form)


@bp.route('/utilities-delete/<int:utility_id>', methods=('POST', 'GET'))
@login_required
def delete_utilities_entry(utility_id):
    user_id = current_user.get_id()

    delete_utility_entry(utility_id, user_id)
    db.session.commit()

    return redirect(url_for('budget.add_utilities_entry'))


@bp.route('/revenue-delete/<int:revenue_id>', methods=('POST', 'GET'))
@login_required
def delete_revenue_entries(revenue_id):
    user_id = current_user.get_id()

    delete_revenue_entry(revenue_id, user_id)
    db.session.commit()

    return redirect(url_for('budget.add_revenue_entry'))


@bp.route('/expense-delete/<int:expense_id>', methods=('POST', 'GET'))
@login_required
def delete_expense_entries(expense_id):
    user_id = current_user.get_id()

    delete_expense_entry(expense_id, user_id)
    db.session.commit()

    return redirect(url_for('budget.add_expense_entry'))


@bp.route('/saving-delete/<int:saving_id>', methods=('POST', 'GET'))
@login_required
def delete_saving_entries(saving_id):
    user_id = current_user.get_id()

    delete_saving_entry(saving_id, user_id)
    db.session.commit()

    return redirect(url_for('budget.add_savings_entry'))
