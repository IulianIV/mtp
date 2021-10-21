from app import db
from app.manager.db.models import *

# TODO add class abstraction and type hints to classes - the software cohesion is very low.
#   too many responsibilities are given to a single class


class Insert:

    def __init__(self):
        self.db = db

    def insert_expense(self, date, item, value, item_category, source):
        return self.db.session.add(
            BudgetExpense(date=date, item=item, value=value, item_category=item_category, source=source))

    def insert_revenue(self, date, revenue, source):
        return self.db.session.add(
            BudgetRevenue(date=date, revenue=revenue, source=source))

    def insert_savings(self, date, value, source, reason, action):
        return self.db.session.add(
            BudgetSaving(date=date, value=value, source=source, reason=reason, action=action))

    def insert_utilities(self, date, rent, energy, satellite, maintenance, details):
        return self.db.session.add(
            BudgetUtilities(date=date, rent=rent, energy=energy, satellite=satellite, maintenance=maintenance, details=details))

    def insert_validation_items(self, item, category):
        return self.db.session.add(
            ValidationSavingItems(item=item, category=category))

    def insert_validation_categories(self, categories):
        return self.db.session.add(
            ValidationSavingCategories(categories=categories)
        )

    def insert_validation_sources(self, sources):
        return self.db.session.add(
            ValidationSavingSources(sources=sources)
        )

    def insert_validation_accounts(self, accounts):
        return self.db.session.add(ValidationSavingAccount(accounts=accounts))

    def insert_validation_actions(self, actions):
        return self.db.session.add(ValidationSavingAction(action=actions))

    def insert_validation_reasons(self, reasons):
        return self.db.session.add(ValidationSavingReason(reasons=reasons))

    def insert_post(self, title, body, user_id):
        return self.db.session.add(Post(title=title, body=body, user_id=user_id))


class Query:

    def __init__(self):
        self.db = db

    @staticmethod
    def query_expense_entries():
        return BudgetExpense.expense_date.asc()

    @staticmethod
    def query_validation_savings_reason():
        return ValidationSavingReason.query.all()

    @staticmethod
    def query_revenue_entries():
        return BudgetRevenue.query.all()

    @staticmethod
    def query_savings_entries():
        return BudgetSaving.saving_date.asc()

    @staticmethod
    def query_utilities_entries():
        return BudgetUtilities.id.asc()

    @staticmethod
    def query_validation_items():
        return ValidationSavingItems.query.all()

    @staticmethod
    def query_validation_categories():
        return ValidationSavingCategories.query.all()

    @staticmethod
    def query_validation_savings_accounts():
        return ValidationSavingAccount.query.all()

    @staticmethod
    def query_validation_sources():
        return ValidationSavingSources.query.all()

    @staticmethod
    def query_validation_savings_action_types():
        return ValidationSavingAction.query.all()

    @staticmethod
    def query_blog_post(post_id):
        return Post.query.filter_by(post_id=post_id).first()

    @staticmethod
    def query_blog_posts():
        return Post.created.desc()

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
        return BudgetSaving.query.coun()

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
        return ValidationSavingAccount.query.filter_by(savings_accounts=account_value).first()

    @staticmethod
    def get_validation_actions(action_value):
        return ValidationSavingAction.query.filter_by(savings_action_types=action_value)

    @staticmethod
    def get_validation_reason(reason_value):
        return ValidationSavingReason.query.filter_by(savings_reason=reason_value).first()


class Update:

    def __init__(self):
        self.db = db

    def update_post(self, title, body, post_id):

        post = Post.query.filter_by(id=post_id)
        post.title = title
        post.body = body

        return self.db.session.commit()


class Delete:

    def __init__(self):
        self.db = db

    @staticmethod
    def delete_post(post_id):
        return Post.query.filter_by(id=post_id).delete()
