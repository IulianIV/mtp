from datetime import datetime
from typing import Union

from sqlalchemy import and_, extract, func

from app import db
from app.manager.db.models import (
    User, UrlEncodeDecodeParse, BudgetExpense, BudgetRevenue, BudgetUtilities,
    BudgetSaving, ValidationSavingSources, ValidationSavingAccount, ValidationSavingReason, ValidationSavingItems,
    ValidationSavingAction, ValidationSavingCategories, Post, GTMContainers, PermissionRoles, RoleRules, BudgetRecurrent

)

current_month = datetime.now().month
current_year = datetime.now().year

# TODO Try to find a way to include them in more dynamic functions. Maybe circle back to classes in some cases?

"""
Database INSERT queries section
"""


def insert_user(username: str, email: str, password: str, user_role: str):
    user = User(username=username, email=email, user_role=user_role)
    user.set_password(password)
    return db.session.add(user)


def insert_expense(user: int, date: datetime, item: str, value: str, source: str):
    item_category = ValidationSavingItems.query.filter_by(items=item).first().category

    return db.session.add(
        BudgetExpense(user_id=user, expense_date=date, expense_item=item, expense_value=value,
                      expense_item_category=item_category, expense_source=source))


def insert_revenue(user: int, date: datetime, revenue: str, source: str):
    return db.session.add(
        BudgetRevenue(user_id=user, revenue_date=date, revenue_value=revenue, revenue_source=source))


def insert_savings(user: int, date: datetime, value: str, source: str, reason: str, action: str):
    return db.session.add(
        BudgetSaving(user_id=user, saving_date=date, saving_value=value, saving_source=source, saving_reason=reason,
                     saving_action=action))


def insert_utilities(user: int, date: datetime, rent: str, energy: str, satellite: str, maintenance: str, details: str,
                     budget_source: str):
    return db.session.add(
        BudgetUtilities(user_id=user, utilities_date=date, utilities_rent_value=rent, utilities_energy_value=energy,
                        utilities_satellite_value=satellite,
                        utilities_maintenance_value=maintenance, utilities_info=details, budget_source=budget_source))


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


def insert_post(title: str, body: str, author_id: str, post_image_name: Union[None, str]):
    return db.session.add(Post(title=title, body=body, author_id=author_id, post_image_name=post_image_name))


def add_new_url(user: int, raw_url: str, encode_option: Union[str, None], encoding: Union[str, None]):
    return db.session.add(UrlEncodeDecodeParse(user_id=user, raw_url=raw_url, encode_option=encode_option,
                                               encoding=encoding))


def insert_gtm_container(user: int, container_id: str, container_data: bytes):
    return db.session.add(GTMContainers(user_id=user, container_id=container_id,
                                        container_data=container_data, is_active=False))


def insert_recurrent_payment(user, recurrent_name: str, recurrent_value: str, recurrent_status: bool,
                             recurrent_date: datetime):
    return db.session.add(
        BudgetRecurrent(user_id=user, recurrent_name=recurrent_name, recurrent_status=recurrent_status,
                        recurrent_value=recurrent_value, recurrent_date=recurrent_date))


def send_recurrent_pay(user, date: datetime, recurrent_name: str, value: str):

    category_exists = ValidationSavingCategories.query.filter_by(categories='Subscriptions').first()

    if not category_exists:
        insert_validation_categories('Subscriptions')

    source_exists = ValidationSavingItems.query.filter_by(items=recurrent_name).first()
    
    if not source_exists:
        insert_validation_items(recurrent_name, 'Subscriptions')
        
    if category_exists and source_exists:
        insert_expense(user, date, recurrent_name, value, 'Bank')

        return db.session.commit()


def create_new_role(role_name: str, role_rules: list):

    db.session.add(PermissionRoles(role_name=role_name))

    for rule in role_rules:
        db.session.add(RoleRules(role_name=role_name, role_rule=rule))

    return db.session.commit()


"""
Database SELECT queries section
"""


def get_existing_user_by_username(username):
    user = User.query.filter_by(username=username).first()

    return user


def get_existing_user_by_id(user_id: int):
    user = User.query.filter_by(id=user_id).first()

    return user


def get_all_users():

    all_users = User.query.all()

    return all_users


def query_expense_entries(user_id: int):
    return BudgetExpense.query.filter_by(user_id=user_id).order_by(BudgetExpense.expense_date.desc())


def query_revenue_entries(user_id: int):
    return BudgetRevenue.query.filter_by(user_id=user_id).order_by(BudgetRevenue.revenue_date.desc())


def query_savings_entries(user_id: int):
    return BudgetSaving.query.filter_by(user_id=user_id).order_by(BudgetSaving.saving_date.desc())


def query_validation_savings_reason():
    return db.session.query(ValidationSavingReason.saving_reason)


def query_utilities_entries(user_id: int):
    return BudgetUtilities.query.filter_by(user_id=user_id).order_by(BudgetUtilities.utilities_date.desc())


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


def query_blog_post(author: str, post_id: str):
    return Post.query.filter_by(author_id=author, id=post_id).first()


def query_blog_posts():
    return Post.query.order_by(Post.created).all()


def get_username_from_post_author(post_author_id: int):
    return User.query.filter_by(id=post_author_id).first().username


def get_user_from_post_author(post_author_id: int):
    return User.query.filter_by(id=post_author_id).first()


def get_validation_item(item_value: str):
    return ValidationSavingItems.query.filter_by(items=item_value).first()


def get_validation_category(category_value: str):
    return ValidationSavingCategories.query.filter_by(categories=category_value).first()


def get_validation_source(source_value: str):
    return ValidationSavingSources.query.filter_by(sources=source_value).first()


def get_expense_count(user_id: int):
    return BudgetRevenue.query.filter_by(user_id=user_id).count()


def get_revenue_count(user_id: int):
    return BudgetRevenue.query.filter_by(user_id=user_id).count()


def get_savings_count(user_id: int):
    return BudgetSaving.query.filter_by(user_id=user_id).count()


def get_utilities_count(user_id: int):
    return BudgetUtilities.query.filter_by(user_id=user_id).count()


def get_validation_categories_count():
    return ValidationSavingCategories.query.count()


def get_validation_items_count():
    return ValidationSavingItems.query.count()


def get_validation_accounts_count():
    return ValidationSavingAccount.query.count()


def get_validation_reason_count():
    return ValidationSavingReason.query.count()


def get_validation_sources_count():
    return ValidationSavingSources.query.count()


def get_validation_account(account_value: str):
    return ValidationSavingAccount.query.filter_by(saving_accounts=account_value).first()


def get_validation_actions(action_value: str):
    return ValidationSavingAction.query.filter_by(saving_action_type=action_value).first()


def get_validation_reason(reason_value: str):
    return ValidationSavingReason.query.filter_by(saving_reason=reason_value).first()

    # PEP violation by comparing to None with equality operators, should be with 'is'
    #   but, sqlalchemy does not work with 'is' and only recognizes '==' and '!=' because
    #   it is using magic methods (operator overloading) to generate sql constructs


def get_parsed_urls(user_id: int):
    return UrlEncodeDecodeParse.query.filter_by(user_id=user_id).filter(and_(UrlEncodeDecodeParse.encode_option == None,
                                                                             UrlEncodeDecodeParse.encoding == None))


def get_current_month_data(user: int):
    budget_totals = {
        'revenue': BudgetRevenue.query.
            filter_by(user_id=user).
            filter(extract('month', BudgetRevenue.revenue_date) == current_month).
            filter(extract('year', BudgetRevenue.revenue_date) == current_year).
            with_entities(BudgetRevenue.revenue_value).all(),
        'expense': BudgetExpense.query.
            filter_by(user_id=user).
            filter(extract('month', BudgetExpense.expense_date) == current_month).
            filter(extract('year', BudgetExpense.expense_date) == current_year).
            with_entities(BudgetExpense.expense_value).all()
    }

    return budget_totals


def get_current_month_mandatory_expense(user: int):
    rent_utilities_total = sum(db.session.query(func.sum(BudgetUtilities.utilities_rent_value),
                                                func.sum(BudgetUtilities.utilities_satellite_value),
                                                func.sum(BudgetUtilities.utilities_energy_value),
                                                func.sum(BudgetUtilities.utilities_maintenance_value)).
                               filter_by(user_id=user).
                               filter(extract('month', BudgetUtilities.utilities_date) == current_month).
                               filter(extract('year', BudgetUtilities.utilities_date) == current_year).all()[0])

    return rent_utilities_total


# fixme THIS might not be correct. Currently it only reports POSITIVE saving additions and ignores WITHDRAWALS
def get_savings_data(user: int):
    savings_totals = {
        'ec': BudgetSaving.query.
            filter_by(user_id=user).
            filter_by(saving_source='EC').filter_by(saving_action='deposit').all(),
        'ed': BudgetSaving.query.
            filter_by(user_id=user).
            filter_by(saving_source='ED').filter_by(saving_action='deposit').all(),
        'if': BudgetSaving.query.
            filter_by(user_id=user).
            filter_by(saving_source='IF').filter_by(saving_action='deposit').all(),
    }

    return savings_totals


def get_current_month_summary(user: int):
    current_month_summary = db.session. \
        query(BudgetExpense.id, BudgetExpense.expense_date, func.sum(BudgetExpense.expense_value),
              func.group_concat(BudgetExpense.expense_item.distinct()),
              func.group_concat(BudgetExpense.expense_item_category.distinct())). \
        filter_by(user_id=user). \
        filter(extract('month', BudgetExpense.expense_date) == current_month). \
        filter(extract('year', BudgetExpense.expense_date) == current_year). \
        group_by(BudgetExpense.expense_date)

    return current_month_summary


def get_expense_count_by_category(user: int):
    category_count = db.session.query(func.count(BudgetExpense.id),
                                      BudgetExpense.expense_item_category). \
        filter_by(user_id=user). \
        filter(extract('month', BudgetExpense.expense_date) == current_month). \
        filter(extract('year', BudgetExpense.expense_date) == current_year). \
        group_by(BudgetExpense.expense_item_category)

    return category_count


def get_expense_count_by_item(user: int):
    item_count = db.session.query(func.count(BudgetExpense.id),
                                  BudgetExpense.expense_item). \
        filter_by(user_id=user). \
        filter(extract('month', BudgetExpense.expense_date) == current_month). \
        filter(extract('year', BudgetExpense.expense_date) == current_year). \
        group_by(BudgetExpense.expense_item)

    return item_count


def get_validation_saving_sources():
    return ValidationSavingSources.query.order_by(ValidationSavingSources.sources).all()


def get_validation_saving_accounts():
    return ValidationSavingAccount.query.order_by(ValidationSavingAccount.saving_accounts).all()


def get_validation_saving_reasons():
    return ValidationSavingReason.query.order_by(ValidationSavingReason.saving_reason).all()


def get_validation_saving_action():
    return ValidationSavingAction.query.order_by(ValidationSavingAction.saving_action_type).all()


def get_validation_saving_items():
    return ValidationSavingItems.query.order_by(ValidationSavingItems.items).all()


def query_utilities_entry(user_id: str, utility_id: str):
    return BudgetUtilities.query.filter_by(user_id=user_id, id=utility_id).first()


def query_revenue_entry(user_id: str, revenue_id: str):
    return BudgetRevenue.query.filter_by(user_id=user_id, id=revenue_id).first()


def query_expense_entry(user_id: str, expense_id: str):
    return BudgetExpense.query.filter_by(user_id=user_id, id=expense_id).first()


def query_saving_entry(user_id: str, saving_id: str):
    return BudgetSaving.query.filter_by(user_id=user_id, id=saving_id).first()


def check_current_month_data(user: int):
    current_month_revenue = BudgetRevenue.query.filter_by(user_id=user). \
        filter(extract('month', BudgetRevenue.revenue_date) == current_month). \
        filter(extract('year', BudgetRevenue.revenue_date) == current_year).first()

    current_month_expense = BudgetExpense.query.filter_by(user_id=user). \
        filter(extract('month', BudgetExpense.expense_date) == current_month). \
        filter(extract('year', BudgetExpense.expense_date) == current_year).first()

    if not current_month_revenue or not current_month_expense:
        return False
    else:
        return True


def get_active_gtm_container(user_id: int):
    return GTMContainers.query.filter_by(user_id=user_id, is_active=True).first()


def gtm_container_exists(user_id: int, container_id: str):
    if GTMContainers.query.filter_by(user_id=user_id, container_id=container_id).first():
        return True
    else:
        return False


def get_gtm_containers(user_id: int):
    return GTMContainers.query.filter_by(user_id=user_id).order_by(GTMContainers.container_id).all()


def get_recurrent_payments(user_id: int):
    return BudgetRecurrent.query.filter_by(user_id=user_id).order_by(BudgetRecurrent.recurrent_name).all()


def get_user_role_rules(user_id: int):

    user = User.query.filter_by(id=user_id).first()
    user_role = user.user_role

    role_rules = RoleRules.query.filter_by(role_name=user_role).group_by(RoleRules.role_rule).all()

    return role_rules


def get_all_roles():

    roles = PermissionRoles.query.all()

    return roles


"""
Database UPDATE queries section
"""


def update_post(user: int, title: str, body: str, post_id: str, image_name: Union[None, str]):
    post = Post.query.filter_by(id=post_id, author_id=user).first()
    post.title = title
    post.body = body
    post.post_image_name = image_name

    db.session.commit()


def update_utility_entry(entry_id: int, user: int, date: datetime, rent_value: int, energy_value: int,
                         satellite_value: int, maintenance_value: int, details: str, source: str):
    entry = BudgetUtilities.query.filter_by(id=entry_id, user_id=user).first()
    entry.utilities_date = date
    entry.utilities_rent_value = rent_value
    entry.utilities_energy_value = energy_value
    entry.utilities_satellite_value = satellite_value
    entry.utilities_maintenance_value = maintenance_value
    entry.utilities_info = details
    entry.budget_source = source

    db.session.commit()


def update_revenue_entry(entry_id: int, user: int, date: datetime, value: int, source: str):
    entry = BudgetRevenue.query.filter_by(id=entry_id, user_id=user).first()
    entry.revenue_date = date
    entry.revenue_value = value
    entry.revenue_source = source

    db.session.commit()


def update_expense_entry(entry_id: int, user: int, date: datetime, item: str, value: int, source: str):
    entry = BudgetExpense.query.filter_by(id=entry_id, user_id=user).first()
    entry.expense_date = date
    entry.expense_item = item
    entry.expense_value = value
    entry.expense_source = source

    item_category = ValidationSavingItems.query.filter_by(items=item).first().category

    entry.expense_item_category = item_category

    db.session.commit()


def update_saving_entry(entry_id: int, user: int, date: datetime, value: int, account: str, reason: str, action: str):
    entry = BudgetSaving.query.filter_by(id=entry_id, user_id=user).first()
    entry.saving_date = date
    entry.saving_value = value
    entry.saving_source = account
    entry.saving_reason = reason
    entry.saving_action = action

    db.session.commit()


def set_gtm_container_active(user_id: int, container_id: str):
    container = GTMContainers.query.filter_by(user_id=user_id, container_id=container_id).first()
    container.is_active = True

    db.session.commit()


def set_gtm_container_inactive(user_id: int, container_id: str):
    container = GTMContainers.query.filter_by(user_id=user_id, container_id=container_id).first()
    container.is_active = False

    db.session.commit()


def inactivate_all_gtm_containers(user_id: int):
    containers = GTMContainers.query.filter_by(user_id=user_id).all()

    for container in containers:
        container.is_active = False

    db.session.commit()


def update_gtm_container_data(user_id: int, container_id: str, container_data):
    container = GTMContainers.query.filter_by(user_id=user_id, container_id=container_id).first()

    container.container_data = container_data

    db.session.commit()


def update_gtm_container_source(user_id: int, container_id: str, container_source: str):
    container = GTMContainers.query.filter_by(user_id=user_id, container_id=container_id).first()

    container.container_source = container_source

    db.session.commit()


def update_recurrent_name(recurrent_id: int, new_name: str):

    recurrent = BudgetRecurrent.query.filter_by(id=recurrent_id).first()

    recurrent.recurrent_name = new_name

    db.session.commit()


def disable_recurrent_entry(recurrent_id: int):

    current_recurrent = BudgetRecurrent.query.filter_by(id=recurrent_id).first()
    current_recurrent.recurrent_status = 0


def update_permissions_role(user_id: str, new_role: str):
    user = User.query.filter_by(id=user_id).first()

    user.user_role = new_role

    db.session.commit()


"""
Database DELETE queries section
"""


def delete_post(user: int, post_id: str):
    Post.query.filter_by(author_id=user, id=post_id).delete()

    db.session.commit()


def delete_utility_entry(entry_id: int, user: int):
    BudgetUtilities.query.filter_by(id=entry_id, user_id=user).delete()

    db.session.commit()


def delete_revenue_entry(entry_id: int, user: int):
    BudgetRevenue.query.filter_by(id=entry_id, user_id=user).delete()

    db.session.commit()


def delete_expense_entry(entry_id: int, user: int):
    BudgetExpense.query.filter_by(id=entry_id, user_id=user).delete()

    db.session.commit()


def delete_saving_entry(entry_id: int, user: int):
    BudgetSaving.query.filter_by(id=entry_id, user_id=user).delete()

    db.session.commit()


"""
Database combo queries section
"""


def insert_and_disable_recurrent(recurrent_id: int, user, new_name: int, new_value: int, new_status: bool,
                                 new_date: datetime):

    current_recurrent = BudgetRecurrent.query.filter_by(id=recurrent_id).first()
    current_recurrent.recurrent_status = 0

    db.session.add(
        BudgetRecurrent(user_id=user, recurrent_name=new_name, recurrent_status=new_status,
                        recurrent_value=new_value, recurrent_date=new_date))

    return db.session.commit()
