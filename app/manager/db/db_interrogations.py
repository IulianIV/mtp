from typing import NewType, Union

from sqlalchemy import and_, extract, func

from app.manager.db.models import *

# Type hinting
DateTime = NewType('DateTime', datetime)

current_month = datetime.now().month
current_year = datetime.now().year

"""
Database INSERT queries section
"""


def insert_user(username: str, email: str, password: str):
    user = User(username=username, email=email)
    user.set_password(password)
    return db.session.add(user)


def insert_expense(date: DateTime, item: str, value: str, item_category: str, source: str):
    return db.session.add(
        BudgetExpense(expense_date=date, expense_item=item, expense_value=value,
                      expense_item_category=item_category, expense_source=source))


def insert_revenue(date: DateTime, revenue: str, source: str):
    return db.session.add(
        BudgetRevenue(revenue_date=date, revenue_value=revenue, revenue_source=source))


def insert_savings(date: DateTime, value: str, source: str, reason: str, action: str):
    return db.session.add(
        BudgetSaving(saving_date=date, saving_value=value, saving_source=source, saving_reason=reason,
                     saving_action=action))


def insert_utilities(date: DateTime, rent: str, energy: str, satellite: str, maintenance: str, details: str):
    return db.session.add(
        BudgetUtilities(utilities_date=date, utilities_rent_value=rent, utilities_energy_value=energy,
                        utilities_satellite_value=satellite,
                        utilities_maintenance_value=maintenance, utilities_info=details))


def insert_validation_items(item: str, category: str):
    return db.session.add(
        ValidationSavingItems(items=item, category=category))


def insert_validation_categories(categories: str):
    return db.session.add(
        ValidationSavingCategories(categories=categories)
    )


def insert_validation_sources(sources: str):
    return db.session.add(
        ValidationSavingSources(sources=sources)
    )


def insert_validation_accounts(accounts: str):
    return db.session.add(ValidationSavingAccount(saving_accounts=accounts))


def insert_validation_actions(actions: str):
    return db.session.add(ValidationSavingAction(saving_action_type=actions))


def insert_validation_reasons(reasons: str):
    return db.session.add(ValidationSavingReason(saving_reason=reasons))


def insert_post(title: str, body: str, author_id: str):
    return db.session.add(Post(title=title, body=body, author_id=author_id))


def add_new_url(raw_url: str, encode_option: Union[str, None], encoding: Union[str, None]):
    return db.session.add(UrlEncodeDecodeParse(raw_url=raw_url, encode_option=encode_option,
                                               encoding=encoding))


"""
Database SELECT queries section
"""


def check_existing_user(username):
    user = User.query.filter_by(username=username).first()

    return user


def query_expense_entries() -> list:
    return BudgetExpense.query.order_by(BudgetExpense.expense_date.desc())


def query_revenue_entries() -> list:
    return BudgetRevenue.query.order_by(BudgetRevenue.revenue_date.desc())


def query_savings_entries() -> list:
    return BudgetSaving.query.order_by(BudgetSaving.saving_date.desc())


def query_validation_savings_reason():
    return db.session.query(ValidationSavingReason.saving_reason)


def query_utilities_entries() -> list:
    return BudgetUtilities.query.order_by(BudgetUtilities.utilities_date.desc())


def query_validation_items():
    return db.session.query(ValidationSavingItems.items)


def query_validation_categories():
    return db.session.query(ValidationSavingCategories.categories)


def query_validation_savings_accounts():
    return db.session.query(ValidationSavingAccount.saving_accounts)


def query_validation_sources():
    return db.session.query(ValidationSavingSources.sources)


def query_validation_savings_action_types():
    return db.session.query(ValidationSavingAction.saving_action_type)


def query_blog_post(post_id: str) -> str:
    return Post.query.filter_by(id=post_id).first()


def query_blog_posts() -> list:
    return Post.query.order_by(Post.created).all()


def get_username_from_post_author(post_author_id: int) -> str:
    return User.query.filter_by(id=post_author_id).first().username


def get_user_from_post_author(post_author_id: int) -> str:
    return User.query.filter_by(id=post_author_id).first()


def get_validation_item(item_value: str) -> str:
    return ValidationSavingItems.query.filter_by(items=item_value).first()


def get_validation_category(category_value: str) -> str:
    return ValidationSavingCategories.query.filter_by(categories=category_value).first()


def get_validation_source(source_value: str) -> str:
    return ValidationSavingSources.query.filter_by(sources=source_value).first()


def get_expense_count() -> int:
    return BudgetExpense.query.count()


def get_revenue_count() -> int:
    return BudgetRevenue.query.count()


def get_savings_count() -> int:
    return BudgetSaving.query.count()


def get_utilities_count() -> int:
    return BudgetUtilities.query.count()


def get_validation_categories_count() -> int:
    return ValidationSavingCategories.query.count()


def get_validation_items_count() -> int:
    return ValidationSavingItems.query.count()


def get_validation_accounts_count() -> int:
    return ValidationSavingAccount.query.count()


def get_validation_reason_count() -> int:
    return ValidationSavingReason.query.count()


def get_validation_sources_count() -> int:
    return ValidationSavingSources.query.count()


def get_validation_account(account_value: str) -> str:
    return ValidationSavingAccount.query.filter_by(saving_accounts=account_value).first()


def get_validation_actions(action_value: str) -> str:
    return ValidationSavingAction.query.filter_by(saving_action_type=action_value).first()


def get_validation_reason(reason_value: str) -> str:
    return ValidationSavingReason.query.filter_by(saving_reason=reason_value).first()

    # PEP violation by comparing to None with equality operators, should be with 'is'
    #   but, sqlalchemy does not work with 'is' and only recognizes '==' and '!=' because
    #   it is using magic methods (operator overloading) to generate sql constructs


def get_parsed_urls():
    return UrlEncodeDecodeParse.query.filter(and_(UrlEncodeDecodeParse.encode_option == None,
                                                  UrlEncodeDecodeParse.encoding == None))


def get_current_month_data():
    budget_totals = {
        'revenue': BudgetRevenue.query.
            filter(extract('month', BudgetRevenue.revenue_date) == current_month).
            filter(extract('year', BudgetRevenue.revenue_date) == current_year).
            with_entities(BudgetRevenue.revenue_value).all(),
        'expense': BudgetExpense.query.
            filter(extract('month', BudgetExpense.expense_date) == current_month).
            filter(extract('year', BudgetExpense.expense_date) == current_year).
            with_entities(BudgetExpense.expense_value).all()
    }

    return budget_totals


def get_savings_data():
    savings_totals = {
        'ec': BudgetSaving.query.
            filter_by(saving_source='EC').all(),
        'ed': BudgetSaving.query.
            filter_by(saving_source='ED').all(),
        'if': BudgetSaving.query.
            filter_by(saving_source='IF').all(),
    }

    return savings_totals


"""
Raw database query - useful in tests.

SELECT
id, expense_date, SUM(expense_value),
GROUP_CONCAT(DISTINCT(expense_item)) AS Items,
GROUP_CONCAT(DISTINCT(expense_item_category)) AS Categories
FROM
budget_expense
WHERE strftime('%Y', expense_date) = '2018'
AND strftime('%m', expense_date) = '04'
GROUP BY expense_date

"""


def get_current_month_summary():
    current_month_summary = db.session. \
        query(BudgetExpense.id, BudgetExpense.expense_date, func.sum(BudgetExpense.expense_value),
              func.group_concat(BudgetExpense.expense_item.distinct()),
              func.group_concat(BudgetExpense.expense_item_category.distinct())). \
        filter(extract('month', BudgetExpense.expense_date) == current_month). \
        filter(extract('year', BudgetExpense.expense_date) == current_year). \
        group_by(BudgetExpense.expense_date)

    return current_month_summary


"""
SELECT
COUNT(id) AS 'Number of #',
expense_item_category as Category
FROM
budget_expense
WHERE strftime('%Y', expense_date) = '2020'
AND strftime('%m', expense_date) = '09'
GROUP BY expense_item_category
"""


def get_expense_count_by_category():
    category_count = db.session.query(func.count(BudgetExpense.id),
                                      BudgetExpense.expense_item_category). \
        filter(extract('month', BudgetExpense.expense_date) == current_month). \
        filter(extract('year', BudgetExpense.expense_date) == current_year). \
        group_by(BudgetExpense.expense_item_category)

    return category_count


"""
SELECT
COUNT(id) AS 'Number of #',
expense_item as Item
FROM
budget_expense
WHERE strftime('%Y', expense_date) = '2022'
AND strftime('%m', expense_date) = '01'
GROUP BY expense_item
"""


def get_expense_count_by_item():
    item_count = db.session.query(func.count(BudgetExpense.id),
                                  BudgetExpense.expense_item). \
        filter(extract('month', BudgetExpense.expense_date) == current_month). \
        filter(extract('year', BudgetExpense.expense_date) == current_year). \
        group_by(BudgetExpense.expense_item)

    return item_count


"""
Database UPDATE queries section
"""


def update_post(title: str, body: str, post_id: str):
    post = Post.query.filter_by(id=post_id).first()
    post.title = title
    post.body = body

    db.session.commit()


"""
Database DELETE queries section
"""


def delete_post(post_id: str):
    Post.query.filter_by(id=post_id).delete()

    db.session.commit()
