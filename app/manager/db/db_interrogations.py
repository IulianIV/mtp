from app.manager.db.models import *

# TODO add class abstraction and type hints to classes - the software cohesion is very low.
#   too many responsibilities are given to a single class


class Insert:

    def __init__(self):
        self.db = db

    def insert_expense(self, date, item, value, item_category, source):
        return self.db.session.add(
            BudgetExpense(expense_date=date, expense_item=item, expense_value=value, expense_item_category=item_category, expense_source=source))

    def insert_revenue(self, date, revenue, source):
        return self.db.session.add(
            BudgetRevenue(revenue_date=date, revenue_value=revenue, revenue_source=source))

    def insert_savings(self, date, value, source, reason, action):
        return self.db.session.add(
            BudgetSaving(saving_date=date, saving_value=value, saving_source=source, saving_reason=reason, saving_action=action))

    def insert_utilities(self, date, rent, energy, satellite, maintenance, details):
        return self.db.session.add(
            BudgetUtilities(utilities_date=date, utilities_rent_value=rent, utilities_energy_value=energy, utilities_satellite_value=satellite, utilities_maintenance_value=maintenance, utilities_info=details))

    def insert_validation_items(self, item, category):
        return self.db.session.add(
            ValidationSavingItems(items=item, category=category))

    def insert_validation_categories(self, categories):
        return self.db.session.add(
            ValidationSavingCategories(categories=categories)
        )

    def insert_validation_sources(self, sources):
        return self.db.session.add(
            ValidationSavingSources(sources=sources)
        )

    def insert_validation_accounts(self, accounts):
        return self.db.session.add(ValidationSavingAccount(saving_accounts=accounts))

    def insert_validation_actions(self, actions):
        return self.db.session.add(ValidationSavingAction(saving_action_type=actions))

    def insert_validation_reasons(self, reasons):
        return self.db.session.add(ValidationSavingReason(saving_reason=reasons))

    def insert_post(self, title, body, author_id):
        return self.db.session.add(Post(title=title, body=body, author_id=author_id))


class Query:

    def __init__(self):
        self.db = db

    @staticmethod
    def query_expense_entries():
        return BudgetExpense.query.order_by(BudgetExpense.expense_date.desc())

    @staticmethod
    def query_revenue_entries():
        return BudgetRevenue.query.order_by(BudgetRevenue.revenue_date.desc())

    @staticmethod
    def query_savings_entries():
        return BudgetSaving.query.order_by(BudgetSaving.saving_date.desc())

    @staticmethod
    def query_validation_savings_reason():
        return db.session.query(ValidationSavingReason.saving_reason)

    @staticmethod
    def query_utilities_entries():
        return db.session.query(BudgetUtilities.id.asc())

    @staticmethod
    def query_validation_items():
        return db.session.query(ValidationSavingItems.items)

    @staticmethod
    def query_validation_categories():
        return db.session.query(ValidationSavingCategories.categories)

    @staticmethod
    def query_validation_savings_accounts():
        return db.session.query(ValidationSavingAccount.saving_accounts)

    @staticmethod
    def query_validation_sources():
        return db.session.query(ValidationSavingSources.sources)

    @staticmethod
    def query_validation_savings_action_types():
        return db.session.query(ValidationSavingAction.saving_action_type)

    @staticmethod
    def query_blog_post(post_id):
        return Post.query.filter_by(id=post_id).first()

    @staticmethod
    def query_blog_posts():
        return Post.query.order_by(Post.created).all()

    @staticmethod
    def get_validation_item(item_value):
        return ValidationSavingItems.query.filter_by(items=item_value).first()

    @staticmethod
    def get_validation_category(category_value):
        return ValidationSavingCategories.query.filter_by(categories=category_value).first()

    @staticmethod
    def get_validation_source(source_value):
        return ValidationSavingSources.query.filter_by(sources=source_value).first()

    @staticmethod
    def get_expense_count():
        return BudgetExpense.query.count()

    @staticmethod
    def get_revenue_count():
        return BudgetRevenue.query.count()

    @staticmethod
    def get_savings_count():
        return BudgetSaving.query.count()

    @staticmethod
    def get_validation_categories_count():
        return ValidationSavingCategories.query.count()

    @staticmethod
    def get_validation_items_count():
        return ValidationSavingItems.query.count()

    @staticmethod
    def get_validation_accounts_count():
        return ValidationSavingAccount.query.count()

    @staticmethod
    def get_validation_reason_count():
        return ValidationSavingReason.query.count()

    @staticmethod
    def get_validation_sources_count():
        return ValidationSavingSources.query.count()

    @staticmethod
    def get_validation_account(account_value):
        return ValidationSavingAccount.query.filter_by(saving_accounts=account_value).first()

    @staticmethod
    def get_validation_actions(action_value):
        return ValidationSavingAction.query.filter_by(saving_action_type=action_value).first()

    @staticmethod
    def get_validation_reason(reason_value):
        return ValidationSavingReason.query.filter_by(saving_reason=reason_value).first()


class Update:

    def __init__(self):
        self.db = db

    def update_post(self, title, body, post_id):

        post = Post.query.filter_by(id=post_id).first()
        post.title = title
        post.body = body

        self.db.session.commit()


class Delete:

    def __init__(self):
        self.db = db

    def delete_post(self, post_id):
        Post.query.filter_by(id=post_id).delete()

        self.db.session.commit()
