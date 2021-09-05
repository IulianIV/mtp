from mtp.db_manager.db import get_db


class Insert:

    def __init__(self):
        self.db = get_db()

    def insert_expense(self, date, item, value, item_category, source):
        return self.db.execute(
            'INSERT INTO budget_expense (expense_date, expense_item, '
            'expense_value, expense_item_category, expense_source)'
            'VALUES (?, ?, ?, ?, ?)', (date, item, value, item_category, source)
        )

    def insert_revenue(self, date, revenue, source):
        return self.db.execute(
                'INSERT INTO budget_revenue (revenue_date, revenue_value, revenue_source)'
                'VALUES (?, ?, ?)', (date, revenue, source)
            )

    def insert_savings(self, date, value, source, reason, action):
        return self.db.execute(
                'INSERT INTO budget_savings (savings_date, savings_value, savings_source,'
                'savings_reason, savings_action) VALUES (?, ?, ?, ?, ?)',
                (date, value, source, reason, action)
            )

    def insert_utilities(self, date, rent, energy, satellite, maintenance, details):
        return self.db.execute(
            'INSERT INTO budget_utilities (utilities_date, utilities_rent_value, utilities_energy_value,'
            'utilities_satellite_value, utilities_maintenance_value, utilities_info)',
            'VALUES (?, ?, ?, ?, ?, ?)',
            (date, rent, energy, satellite, maintenance, details)
        )

    def insert_validation_items(self, item, category):
        return self.db.execute(
                     'INSERT INTO validation_items (items,category)'
                     ' VALUES (?,?)',
                     (item, category)
                 )

    def insert_validation_categories(self, categories):
        return self.db.execute(
            'INSERT INTO validation_categories (categories) VALUES (?)',
            (categories,)
        )

    def insert_validation_sources(self, sources):
        return self.db.execute(
                    'INSERT INTO validation_sources (sources)'
                    ' VALUES (?)',
                    (sources,)
        )

    def insert_validation_accounts(self, accounts):
        return self.db.execute(
                    'INSERT INTO validation_savings_accounts'
                    ' (savings_accounts) VALUES (?)',
                    (accounts,)
        )

    def insert_validation_actions(self, actions):
        return self.db.execute(
                    'INSERT INTO validation_savings_action_types (savings_action_types) VALUES (?)',
                    (actions,)
        )

    def insert_validation_reasons(self, reasons):
        return self.db.execute(
                    'INSERT INTO validation_savings_reason (savings_reason) VALUES (?)',
                    (reasons,)
        )


class Query:

    def __init__(self):
        self.db = get_db()

    def query_expense_entries(self):
        return self.db.execute(
            'SELECT id, expense_date, expense_item, expense_value, expense_item_category, expense_source'
            ' FROM budget_expense '
            'ORDER BY expense_date ASC'
        )

    def query_validation_savings_reason(self):
        return self.db.execute(
            'SELECT id,savings_reason'
            ' FROM validation_savings_reason'
        )

    def query_revenue_entries(self):
        return self.db.execute(
            'SELECT id, revenue_date, revenue_value, revenue_source'
            ' FROM budget_revenue '
        )

    def query_savings_entries(self):
        return self.db.execute(
            'SELECT id, savings_date,savings_value, savings_source, savings_reason, savings_action'
            ' FROM budget_savings '
            'ORDER BY savings_date ASC'
        )

    def query_utilities_entries(self):
        return self.db.execute(
            'SELECT id, utilities_date, utilities_rent_value, utilities_energy_value, utilities_satellite_value,'
            'utilities_maintenance_value, utilities_info '
            ' FROM budget_utilities '
            'ORDER BY id ASC'
        )

    def query_validation_items(self):
        return self.db.execute(
            'SELECT id,items'
            ' FROM validation_items'
        )

    def query_validation_categories(self):
        return self.db.execute(
            'SELECT id,categories'
            ' FROM validation_categories'
        )

    def query_validation_savings_accounts(self):
        return self.db.execute(
            'SELECT id,savings_accounts'
            ' FROM validation_savings_accounts'
        )

    def query_validation_sources(self):
        return self.db.execute(
            'SELECT id,sources'
            ' FROM validation_sources'
        )

    def query_validation_savings_action_types(self):
        return self.db.execute(
            'SELECT id,savings_action_types'
            ' FROM validation_savings_action_types'
        )
