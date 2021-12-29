from typing import NewType, Union

from app.manager.db.models import *

# Type hinting
DateTime = NewType('DateTime', datetime)


class Insert:

    def __init__(self):
        self.db = db

    def insert_user(self, username: str, email: str, password: str):
        user = User(username=username, email=email)
        user.set_password(password)
        return self.db.session.add(user)

    def insert_expense(self, date: DateTime, item: str, value: str, item_category: str, source: str):
        return self.db.session.add(
            BudgetExpense(expense_date=date, expense_item=item, expense_value=value,
                          expense_item_category=item_category, expense_source=source))

    def insert_revenue(self, date: DateTime, revenue: str, source: str):
        return self.db.session.add(
            BudgetRevenue(revenue_date=date, revenue_value=revenue, revenue_source=source))

    def insert_savings(self, date: DateTime, value: str, source: str, reason: str, action: str):
        return self.db.session.add(
            BudgetSaving(saving_date=date, saving_value=value, saving_source=source, saving_reason=reason,
                         saving_action=action))

    def insert_utilities(self, date: DateTime, rent: str, energy: str, satellite: str, maintenance: str, details: str):
        return self.db.session.add(
            BudgetUtilities(utilities_date=date, utilities_rent_value=rent, utilities_energy_value=energy,
                            utilities_satellite_value=satellite,
                            utilities_maintenance_value=maintenance, utilities_info=details))

    def insert_validation_items(self, item: str, category: str):
        return self.db.session.add(
            ValidationSavingItems(items=item, category=category))

    def insert_validation_categories(self, categories: str):
        return self.db.session.add(
            ValidationSavingCategories(categories=categories)
        )

    def insert_validation_sources(self, sources: str):
        return self.db.session.add(
            ValidationSavingSources(sources=sources)
        )

    def insert_validation_accounts(self, accounts: str):
        return self.db.session.add(ValidationSavingAccount(saving_accounts=accounts))

    def insert_validation_actions(self, actions: str):
        return self.db.session.add(ValidationSavingAction(saving_action_type=actions))

    def insert_validation_reasons(self, reasons: str):
        return self.db.session.add(ValidationSavingReason(saving_reason=reasons))

    def insert_post(self, title: str, body: str, author_id: str):
        return self.db.session.add(Post(title=title, body=body, author_id=author_id))

    def add_new_url(self, raw_url: str, encode_option: Union[str, None], encoding: Union[str, None]):
        return self.db.session.add(UrlEncodeDecodeParse(raw_url=raw_url, encode_option=encode_option,
                                                        encoding=encoding))


class Query:

    def __init__(self):
        self.db = db

    @staticmethod
    def check_existing_user(username):
        user = User.query.filter_by(username=username).first()

        return user

    @staticmethod
    def query_expense_entries() -> list:
        return BudgetExpense.query.order_by(BudgetExpense.expense_date.desc())

    @staticmethod
    def query_revenue_entries() -> list:
        return BudgetRevenue.query.order_by(BudgetRevenue.revenue_date.desc())

    @staticmethod
    def query_savings_entries() -> list:
        return BudgetSaving.query.order_by(BudgetSaving.saving_date.desc())

    @staticmethod
    def query_validation_savings_reason():
        return db.session.query(ValidationSavingReason.saving_reason)

    @staticmethod
    def query_utilities_entries() -> list:
        return BudgetUtilities.query.order_by(BudgetUtilities.utilities_date.desc())

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
    def query_blog_post(post_id: str) -> str:
        return Post.query.filter_by(id=post_id).first()

    @staticmethod
    def query_blog_posts() -> list:
        return Post.query.order_by(Post.created).all()

    @staticmethod
    def get_username_from_post_author(post_author_id: int) -> str:
        return User.query.filter_by(id=post_author_id).first().username

    @staticmethod
    def get_user_from_post_author(post_author_id: int) -> str:
        return User.query.filter_by(id=post_author_id).first()

    @staticmethod
    def get_validation_item(item_value: str) -> str:
        return ValidationSavingItems.query.filter_by(items=item_value).first()

    @staticmethod
    def get_validation_category(category_value: str) -> str:
        return ValidationSavingCategories.query.filter_by(categories=category_value).first()

    @staticmethod
    def get_validation_source(source_value: str) -> str:
        return ValidationSavingSources.query.filter_by(sources=source_value).first()

    @staticmethod
    def get_expense_count() -> int:
        return BudgetExpense.query.count()

    @staticmethod
    def get_revenue_count() -> int:
        return BudgetRevenue.query.count()

    @staticmethod
    def get_savings_count() -> int:
        return BudgetSaving.query.count()

    @staticmethod
    def get_utilities_count() -> int:
        return BudgetUtilities.query.count()

    @staticmethod
    def get_validation_categories_count() -> int:
        return ValidationSavingCategories.query.count()

    @staticmethod
    def get_validation_items_count() -> int:
        return ValidationSavingItems.query.count()

    @staticmethod
    def get_validation_accounts_count() -> int:
        return ValidationSavingAccount.query.count()

    @staticmethod
    def get_validation_reason_count() -> int:
        return ValidationSavingReason.query.count()

    @staticmethod
    def get_validation_sources_count() -> int:
        return ValidationSavingSources.query.count()

    @staticmethod
    def get_validation_account(account_value: str) -> str:
        return ValidationSavingAccount.query.filter_by(saving_accounts=account_value).first()

    @staticmethod
    def get_validation_actions(action_value: str) -> str:
        return ValidationSavingAction.query.filter_by(saving_action_type=action_value).first()

    @staticmethod
    def get_validation_reason(reason_value: str) -> str:
        return ValidationSavingReason.query.filter_by(saving_reason=reason_value).first()


class Update:

    def __init__(self):
        self.db = db

    def update_post(self, title: str, body: str, post_id: str):

        post = Post.query.filter_by(id=post_id).first()
        post.title = title
        post.body = body

        self.db.session.commit()


class Delete:

    def __init__(self):
        self.db = db

    def delete_post(self, post_id: str):
        Post.query.filter_by(id=post_id).delete()

        self.db.session.commit()


class BudgetQueries:

    def __init__(self):
        self.db = db
