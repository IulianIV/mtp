from app import db

# TODO add class abstraction and type hints to classes - the software cohesion is very low.
#   too many responsibilities are given to a single class


class Insert:

    def __init__(self):
        self.db = db

    def insert_expense(self, date, item, value, item_category, source):
        return self.db.session.add(
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
            'utilities_satellite_value, utilities_maintenance_value, utilities_info)'
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

    def insert_post(self, title, body, user_id):
        return self.db.execute(
            'INSERT INTO post (title, body, author_id)'
            ' VALUES (?, ?, ?)',
            (title, body, user_id)
        )


class Query:

    def __init__(self):
        self.db = db

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

    def query_blog_post(self, post_id):
        return self.db.execute(
            'SELECT p.id, title, body, created, author_id, username'
            ' FROM post p JOIN user u ON p.author_id = u.id'
            ' WHERE p.id = ?',
            (post_id,)
        ).fetchone()

    def query_blog_posts(self):
        return self.db.execute(
            'SELECT p.id, title, body, created, author_id, username'
            ' FROM post p JOIN user u ON p.author_id = u.id'
            ' ORDER BY created DESC'
        ).fetchall()

    def get_validation_item(self, item_value):
        return self.db.execute(
            'SELECT items'
            ' FROM validation_items'
            ' WHERE items = ?',
            (item_value,)
        ).fetchone()

    def get_validation_category(self, category_value):
        return self.db.execute(
            'SELECT categories'
            ' FROM validation_categories'
            ' WHERE categories = ?',
            (category_value,)
        ).fetchone()

    def get_validation_source(self, source_value):
        return self.db.execute(
            'SELECT sources'
            ' FROM validation_sources'
            ' WHERE sources = ?',
            (source_value,)
        ).fetchone()

    def get_expense_count(self):
        return self.db.execute('SELECT count(*) FROM budget_expense').fetchone()

    def get_revenue_count(self):
        return self.db.execute('SELECT count(*) FROM budget_revenue').fetchone()

    def get_savings_count(self):
        return self.db.execute('SELECT count(*) FROM budget_savings').fetchone()

    def get_validation_categories_count(self):
        return self.db.execute('SELECT count(*) FROM validation_categories').fetchone()

    def get_validation_items_count(self):
        return self.db.execute('SELECT count(*) FROM validation_items').fetchone()

    def get_validation_accounts_count(self):
        return self.db.execute('SELECT count(*) FROM validation_savings_accounts').fetchone()

    def get_validation_reason_count(self):
        return self.db.execute('SELECT count(*) FROM validation_savings_reason').fetchone()

    def get_validation_sources_count(self):
        return self.db.execute('SELECT count(*) FROM validation_sources').fetchone()

    def get_validation_account(self, account_value):
        return self.db.execute(
            'SELECT savings_accounts'
            ' FROM validation_savings_accounts'
            ' WHERE savings_accounts = ?',
            (account_value,)
        ).fetchone()

    def get_validation_actions(self, action_value):
        return self.db.execute(
            'SELECT savings_action_types'
            ' FROM validation_savings_action_types'
            ' WHERE savings_action_types = ?',
            (action_value,)
        ).fetchone()

    def get_validation_reason(self, reason_value):
        return self.db.execute(
            'SELECT savings_reason'
            ' FROM validation_savings_reason'
            ' WHERE savings_reason = ?',
            (reason_value,)
        ).fetchone()


class Update:

    def __init__(self):
        self.db = db

    def update_post(self, title, body, post_id):
        return self.db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, post_id)
            )


class Delete:

    def __init__(self):
        self.db = db

    def delete_post(self, post_id):
        return self.db.execute('DELETE FROM post WHERE id = ?', (post_id,))
