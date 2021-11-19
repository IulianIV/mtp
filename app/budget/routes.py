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


# Class object for handling multiple SQL queries, might be useful in cases where above code does not work
# fixme Accounts, Actions and Reason from validation seemingly do not record the values in the form


class BudgetDbConnector:
    def __init__(self):
        self.db = db
        self.db_queries = Query()
        self.db_inserts = Insert()

    @property
    def query_expense_entries(self):
        return self.db_queries.query_expense_entries()

    @property
    def query_revenue_entries(self):
        return self.db_queries.query_revenue_entries()

    @property
    def query_savings_entries(self):
        return self.db_queries.query_savings_entries()

    @property
    def query_utilities_entry(self):
        return self.db_queries.query_utilities_entries()

    @property
    def query_validation_items(self):
        return self.db_queries.query_validation_items()

    @property
    def query_validation_categories(self):
        return self.db_queries.query_validation_categories()

    @property
    def query_validation_savings_accounts(self):
        return self.db_queries.query_validation_savings_accounts()

    @property
    def query_validation_sources(self):
        return self.db_queries.query_validation_sources()

    @property
    def query_validation_savings_action_types(self):
        return self.db_queries.query_validation_savings_action_types()

    @property
    def query_validation_savings_reason(self):
        return self.db_queries.query_validation_savings_reason()

    def get_validation_item(self, item_value):
        return self.db_queries.get_validation_item(item_value)

    def get_validation_category(self, category_value):
        return self.db_queries.get_validation_category(category_value)

    def get_validation_source(self, source_value):
        return self.db_queries.get_validation_source(source_value)

    def get_validation_account(self, account_value):
        return self.db_queries.get_validation_account(account_value)

    def get_validation_actions(self, action_value):
        return self.db_queries.get_validation_actions(action_value)

    def get_validation_reason(self, reason_value):
        return self.db_queries.get_validation_reason(reason_value)

    def get_expense_count(self):
        return self.db_queries.get_expense_count()

    def get_revenue_count(self):
        return self.db_queries.get_revenue_count()

    def get_savings_count(self):
        return self.db_queries.get_savings_count()

    def get_validation_categories_count(self):
        return self.db_queries.get_validation_categories_count()

    def get_validation_items_count(self):
        return self.db_queries.get_validation_items_count()

    def get_validation_accounts_count(self):
        return self.db_queries.get_validation_accounts_count()

    def get_validation_reason_count(self):
        return self.db_queries.get_validation_reason_count()

    def get_validation_sources_count(self):
        return self.db_queries.get_validation_sources_count()

    def insert_expense(self, date, item, value, item_category, source):
        return self.db_inserts.insert_expense(date, item, value, item_category, source)

    def insert_revenue(self, date, revenue, source):
        return self.db_inserts.insert_revenue(date, revenue, source)

    def insert_savings(self, date, value, source, reason, action):
        return self.db_inserts.insert_savings(date, value, source, reason, action)

    def insert_utilities(self, date, rent, energy, satellite, maintenance, details):
        return self.db_inserts.insert_utilities(date, rent, energy, satellite, maintenance, details)

    def insert_validation_items(self, item, category):
        return self.db_inserts.insert_validation_items(item, category)

    def insert_validation_categories(self, categories):
        return self.db_inserts.insert_validation_categories(categories)

    def insert_validation_sources(self, sources):
        return self.db_inserts.insert_validation_sources(sources)

    def insert_validation_accounts(self, accounts):
        return self.db_inserts.insert_validation_accounts(accounts)

    def insert_validation_actions(self, actions):
        return self.db_inserts.insert_validation_actions(actions)

    def insert_validation_reasons(self, reasons):
        return self.db_inserts.insert_validation_reasons(reasons)


@bp.route('/')
@login_required
def summary():

    budget_connect = BudgetDbConnector()

    table_counts = {
        'expense_count': budget_connect.get_expense_count(),
        'revenue_count': budget_connect.get_revenue_count(),
        'savings_count': budget_connect.get_savings_count()
    }

    validation_counts = {
        'validation_categories': budget_connect.get_validation_categories_count(),
        'validation_items': budget_connect.get_validation_items_count(),
        'validation_accounts': budget_connect.get_validation_accounts_count(),
        'validation_reason': budget_connect.get_validation_reason_count(),
        'validation_sources': budget_connect.get_validation_sources_count()
    }

    return render_template('budget/summary.html', _object=budget_connect, table_counts=table_counts, validation_counts=validation_counts)


@bp.route('/new-expense-entry', methods=('GET', 'POST'))
@login_required
def add_expense_entry():
    budget_connect = BudgetDbConnector()
    expense_form = forms.AddExpenseEntry()

    items = budget_connect.query_validation_items
    items_set = [x['items'] for x in items]
    expense_form.expense_item.choices = items_set

    item_categories = budget_connect.query_validation_categories
    item_categories_set = [x['categories'] for x in item_categories]
    expense_form.expense_category.choices = item_categories_set

    sources = budget_connect.query_validation_sources
    sources_set = [x['sources'] for x in sources]
    expense_form.expense_source.choices = sources_set

    if expense_form.is_submitted() and expense_form.validate_on_submit():

        date = expense_form.expense_date.data
        item = expense_form.expense_item.data
        value = expense_form.expense_value.data
        item_category = expense_form.expense_category.data
        source = expense_form.expense_source.data

        form_validated_message('All values validated!')

        budget_connect.insert_expense(date, item, value, item_category, source)
        db.session.commit()

        return redirect(url_for('budget.add_expense_entry'))

    return render_template('budget/expense.html', expense_form=expense_form, _object=budget_connect)


@bp.route('/new-revenue-entry', methods=('GET', 'POST'))
@login_required
def add_revenue_entry():
    budget_connect = BudgetDbConnector()
    revenue_form = forms.AddRevenueEntry()

    sources = budget_connect.query_validation_sources
    sources_set = [x['sources'] for x in sources]
    revenue_form.revenue_source.choices = sources_set

    if revenue_form.is_submitted() and revenue_form.validate_on_submit():

        date = revenue_form.revenue_date.data
        revenue = revenue_form.revenue_value.data
        source = revenue_form.revenue_source.data

        form_validated_message('All values validated!')

        budget_connect.insert_revenue(date, revenue, source)
        db.session.commit()

        return redirect(url_for('budget.add_revenue_entry'))

    return render_template('budget/revenue.html', revenue_form=revenue_form, _object=budget_connect)


@bp.route('/new-savings-entry', methods=('GET', 'POST'))
@login_required
def add_savings_entry():
    savings_form = forms.AddSavingsEntry()
    budget_connect = BudgetDbConnector()

    sources = budget_connect.query_validation_sources
    sources_set = [x['sources'] for x in sources]
    savings_form.savings_source.choices = sources_set

    reasons = budget_connect.query_validation_savings_reason
    reasons_set = [x['saving_reason'] for x in reasons]
    savings_form.savings_reason.choices = reasons_set

    actions = budget_connect.query_validation_savings_action_types
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

            budget_connect.insert_savings(date, value, source, reason, action)
            db.session.commit()
            return redirect(url_for('budget.add_savings_entry'))

        return redirect(url_for('budget.add_savings_entry'))

    return render_template('budget/savings.html', savings_form=savings_form, _object=budget_connect)


@bp.route('/validation', methods=('GET', 'POST'))
@login_required
def validation():
    budget_connect = BudgetDbConnector()

    items_form = forms.AddValidationItems()
    categories_form = forms.AddValidationCategory()
    sources_form = forms.AddValidationSources()
    accounts_form = forms.AddValidationAccounts()
    actions_form = forms.AddValidationActions()
    reasons_form = forms.AddValidationReason()

    categories = budget_connect.query_validation_categories
    category_set = [(x['categories']) for x in categories]
    items_form.category_value.choices = category_set

    return render_template('budget/validation.html', _object=budget_connect,
                           items_form=items_form,
                           categories_form=categories_form,
                           sources_form=sources_form,
                           accounts_form=accounts_form,
                           actions_form=actions_form,
                           reasons_form=reasons_form)


@bp.route('/validation/items', methods=('GET', 'POST'))
@login_required
def validation_items():
    budget_connect = BudgetDbConnector()

    items_form = forms.AddValidationItems()
    categories_form = forms.AddValidationCategory()
    sources_form = forms.AddValidationSources()
    accounts_form = forms.AddValidationAccounts()
    actions_form = forms.AddValidationActions()
    reasons_form = forms.AddValidationReason()

    categories = budget_connect.query_validation_categories
    category_set = [(x['categories']) for x in categories]
    items_form.category_value.choices = category_set

    if items_form.is_submitted() and items_form.validate_on_submit():

        item = items_form.item_value.data
        category = items_form.category_value.data

        item_list = budget_connect.get_validation_item(item)

        if item_list is not None and item in item_list:

            form_error_message(f'The value you chose for item: "{item}" already exists')

        elif item_list is None:

            form_validated_message('Item value validated!')
            budget_connect.insert_validation_items(item, category)
            db.session.commit()

        return redirect(url_for('budget.validation'))

    elif not items_form.validate_on_submit():

        if items_form.item_value.data:
            ValidationError(message=form_error_message('Item Value field only accepts letters and spaces.'))

        return redirect(url_for('budget.validation'))

    return render_template('budget/validation.html', _object=budget_connect,
                           items_form=items_form,
                           categories_form=categories_form,
                           sources_form=sources_form,
                           accounts_form=accounts_form,
                           actions_form=actions_form,
                           reasons_form=reasons_form)


@bp.route('/validation/category', methods=('GET', 'POST'))
@login_required
def validation_categories():
    budget_connect = BudgetDbConnector()

    items_form = forms.AddValidationItems()
    categories_form = forms.AddValidationCategory()
    sources_form = forms.AddValidationSources()
    accounts_form = forms.AddValidationAccounts()
    actions_form = forms.AddValidationActions()
    reasons_form = forms.AddValidationReason()

    categories = budget_connect.query_validation_categories
    category_set = [(x['categories']) for x in categories]
    items_form.category_value.choices = category_set

    if categories_form.is_submitted() and categories_form.validate_on_submit():
        categories = categories_form.category_value.data

        category_list = budget_connect.get_validation_category(categories)

        # fixme repair the login. ATM it throws an TypeError: argument of type 'ValidationSavingCategories' is not iterable

        # if category_list is not None and categories in category_list:
        #
        #     form_error_message(f'The value you chose for category: "{categories}" already exists')

        # fixme was a `elif` previous to TypeError.

        if category_list is None:
            form_validated_message('Category value validated!')
            budget_connect.insert_validation_categories(categories)
            db.session.commit()

        return redirect(url_for('budget.validation'))

    elif not categories_form.validate_on_submit():

        if categories_form.category_value.data:
            ValidationError(message=form_error_message('Category Value field only accepts letters and spaces.'))

        return redirect(url_for('budget.validation'))

    return render_template('budget/validation.html', _object=budget_connect,
                           items_form=items_form,
                           categories_form=categories_form,
                           sources_form=sources_form,
                           accounts_form=accounts_form,
                           actions_form=actions_form,
                           reasons_form=reasons_form)


@bp.route('/validation/sources', methods=('GET', 'POST'))
@login_required
def validation_sources():
    budget_connect = BudgetDbConnector()

    items_form = forms.AddValidationItems()
    categories_form = forms.AddValidationCategory()
    sources_form = forms.AddValidationSources()
    accounts_form = forms.AddValidationAccounts()
    actions_form = forms.AddValidationActions()
    reasons_form = forms.AddValidationReason()

    categories = budget_connect.query_validation_categories
    category_set = [(x['categories']) for x in categories]
    items_form.category_value.choices = category_set

    if sources_form.is_submitted() and sources_form.validate_on_submit():

        sources = sources_form.source_value.data
        sources_list = budget_connect.get_validation_source(sources)

        if sources_list is not None and sources in sources_list:

            form_error_message(f'The value you chose for source: "{sources}" already exists')

        elif sources_list is None:
            form_validated_message('Source value validated!')
            budget_connect.insert_validation_sources(sources)
            db.session.commit()

        return redirect(url_for('budget.validation'))

    elif not sources_form.validate_on_submit():

        if sources_form.source_value.data:
            ValidationError(message=form_error_message('Sources Value field only accepts letters and spaces.'))

        return redirect(url_for('budget.validation'))

    return render_template('budget/validation.html', _object=budget_connect,
                           items_form=items_form,
                           categories_form=categories_form,
                           sources_form=sources_form,
                           accounts_form=accounts_form,
                           actions_form=actions_form,
                           reasons_form=reasons_form)


@bp.route('/validation/accounts', methods=('GET', 'POST'))
@login_required
def validation_accounts():
    budget_connect = BudgetDbConnector()

    items_form = forms.AddValidationItems()
    categories_form = forms.AddValidationCategory()
    sources_form = forms.AddValidationSources()
    accounts_form = forms.AddValidationAccounts()
    actions_form = forms.AddValidationActions()
    reasons_form = forms.AddValidationReason()

    categories = budget_connect.query_validation_categories
    category_set = [(x['categories']) for x in categories]
    items_form.category_value.choices = category_set

    if accounts_form.is_submitted() and accounts_form.validate_on_submit():
        accounts = accounts_form.account_value.data

        accounts_list = budget_connect.get_validation_account(accounts)

        if accounts_list is not None and accounts in accounts_list:

            form_error_message(f'The value you chose for account: "{accounts}" already exists')

        elif accounts_list is None:
            form_validated_message('Account value validated!')
            budget_connect.insert_validation_accounts(accounts)
            db.session.commit()

        return redirect(url_for('budget.validation'))

    elif not accounts_form.validate_on_submit():

        if accounts_form.account_value.data:
            ValidationError(message=form_error_message('Account Value field only accepts letters and spaces.'))

        return redirect(url_for('budget.validation'))

    return render_template('budget/validation.html', _object=budget_connect,
                           items_form=items_form,
                           categories_form=categories_form,
                           sources_form=sources_form,
                           accounts_form=accounts_form,
                           actions_form=actions_form,
                           reasons_form=reasons_form)


@bp.route('/validation/actions', methods=('GET', 'POST'))
@login_required
def validation_actions():
    budget_connect = BudgetDbConnector()

    items_form = forms.AddValidationItems()
    categories_form = forms.AddValidationCategory()
    sources_form = forms.AddValidationSources()
    accounts_form = forms.AddValidationAccounts()
    actions_form = forms.AddValidationActions()
    reasons_form = forms.AddValidationReason()

    categories = budget_connect.query_validation_categories
    category_set = [(x['categories']) for x in categories]
    items_form.category_value.choices = category_set

    if actions_form.is_submitted() and actions_form.validate_on_submit():

        actions = actions_form.action_value.data

        action_list = budget_connect.get_validation_actions(actions)

        if action_list is not None and actions in action_list:

            form_error_message(f'The value you chose for action: "{actions}" already exists')

        elif action_list is None:

            form_validated_message('Action value validated!')
            budget_connect.insert_validation_actions(actions)
            db.session.commit()

        return redirect(url_for('budget.validation'))

    elif not actions_form.validate_on_submit():

        if actions_form.action_value.data:
            ValidationError(message=form_error_message('Action Value field only accepts letters and spaces.'))

        return redirect(url_for('budget.validation'))

    return render_template('budget/validation.html', _object=budget_connect,
                           items_form=items_form,
                           categories_form=categories_form,
                           sources_form=sources_form,
                           accounts_form=accounts_form,
                           actions_form=actions_form,
                           reasons_form=reasons_form)


@bp.route('/validation/reasons', methods=('GET', 'POST'))
@login_required
def validation_reasons():
    budget_connect = BudgetDbConnector()

    items_form = forms.AddValidationItems()
    categories_form = forms.AddValidationCategory()
    sources_form = forms.AddValidationSources()
    accounts_form = forms.AddValidationAccounts()
    actions_form = forms.AddValidationActions()
    reasons_form = forms.AddValidationReason()

    categories = budget_connect.query_validation_categories
    category_set = [(x['categories']) for x in categories]
    items_form.category_value.choices = category_set

    if reasons_form.is_submitted() and reasons_form.validate_on_submit():

        reasons = reasons_form.reason_value.data
        reasons_list = budget_connect.get_validation_reason(reasons)

        if reasons_list is not None and reasons in reasons_list:

            form_error_message(f'The value you chose for reason: "{reasons}" already exists')

        elif reasons_list is None:
            form_validated_message('Reason value validated!')
            budget_connect.insert_validation_reasons(reasons)
            db.session.commit()

        return redirect(url_for('budget.validation'))

    elif not reasons_form.validate_on_submit():

        if reasons_form.reason_value.data:
            ValidationError(message=form_error_message('Reason Value field only accepts letters and spaces.'))

        return redirect(url_for('budget.validation'))

    return render_template('budget/validation.html', _object=budget_connect,
                           items_form=items_form,
                           categories_form=categories_form,
                           sources_form=sources_form,
                           accounts_form=accounts_form,
                           actions_form=actions_form,
                           reasons_form=reasons_form)


@bp.route('/new_utilities_entry', methods=('GET', 'POST'))
@login_required
def add_utilities_entry():
    budget_connect = BudgetDbConnector()
    utilities_form = forms.AddUtilitiesEntry()

    date = utilities_form.utilities_date.data
    rent = utilities_form.utilities_rent.data
    energy = utilities_form.utilities_energy.data
    satellite = utilities_form.utilities_satellite.data
    maintenance = utilities_form.utilities_maintenance.data
    details = utilities_form.utilities_details.data

    if utilities_form.is_submitted() and utilities_form.validate_on_submit():

        form_validated_message('All values validated!')

        budget_connect.insert_utilities(date, rent, energy, satellite, maintenance, details)
        db.session.commit()

        return redirect(url_for('budget.add_utilities_entry'))

    return render_template('budget/utilities.html', _object=budget_connect, utilities_form=utilities_form)


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
