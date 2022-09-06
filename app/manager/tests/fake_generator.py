import random

import click
from faker import Faker
from flask import (
    redirect, render_template, request, url_for
)
from flask_login import current_user

from app.manager.helpers import login_required, user_roles
from app.manager import tests_bp
from app.manager.db.db_interrogations import *
from app.manager.helpers import form_validated_message, form_error_message, check_range
from app.manager.tests.forms import AddFakes
from app.webtools.routes import encodings


# TODO Validation for ranges added. Research if custom validation through WTForms would be better. Whilst with this
#   you learned about decorators
# TODO Add date-time choice for test value insertion
# TODO Convert Form Range field to Int field or string field. Or at least STRIP field and permit only
#   certain types of data.

@tests_bp.route('/tests/fake-data-generator', methods=('GET', 'POST'))
@user_roles(permitted_roles=['admin'])
@login_required
def add_fakes():
    fake_form = AddFakes()

    fake_form.fake_choices.choices = ['Fake Users', 'Fake Posts', 'Fake Revenue', 'Fake Saving',
                                      'Fake Expense', 'Fake Utilities', 'Fake Validation', 'Fake URLs']

    if request.method == 'POST':
        if fake_form.is_submitted() and fake_form.fake_choices.data != 'Fake URLs':
            fake_choice = fake_form.fake_choices.data
            fake_number = fake_form.fake_number.data

            choice_func_map = {
                'Fake Users': create_fake_users,
                'Fake Posts': create_fake_posts,
                'Fake Revenue': create_fake_revenue,
                'Fake Saving': create_fake_saving,
                'Fake Expense': create_fake_expense,
                'Fake Utilities': create_fake_utilities,
                'Fake Validation': create_fake_validation
            }

            fake_data = choice_func_map[fake_choice](fake_number)
            if not fake_data:
                return redirect(url_for('manager-tests.add_fakes'))

            form_validated_message(f'Successfully added {fake_data} {fake_choice}')

            return redirect(url_for('manager-tests.add_fakes'))

        if fake_form.is_submitted() and fake_form.fake_choices.data == 'Fake URLs':
            fake_choice = fake_form.fake_choices.data
            fake_range = fake_form.fake_number.data
            fake_utm = fake_form.have_params.data
            fake_params = fake_form.randomized_params.data

            if fake_form.is_submitted() and fake_utm and fake_params:
                form_error_message('Either one or None checkboxes must be selected. Selection of both is not possible.')

                return redirect(url_for('manager-tests.add_fakes'))

            choice_func_map = {
                'Fake URLs': create_fake_urls
            }

            fake_data = choice_func_map[fake_choice](fake_range, fake_utm, fake_params)

            form_validated_message(f'Successfully added {fake_data} URLs')

            return redirect(url_for('manager-tests.add_fakes'))

    return render_template('manager/tests/fake_generator.html', fake_form=fake_form)


def create_fake_users(users_num: int):
    """Generate fake users."""
    faker = Faker()

    for i in range(int(users_num)):
        user = User(username=faker.first_name(), email=faker.email())
        user.set_password(faker.bothify(text='??###'))
        db.session.add(user)
    db.session.commit()
    print(f'Added {users_num} fake users to the database.')
    return users_num


# fixme upon using current_user.get_id() to post on behalf of logged user, CLI usage is bugged.
@check_range
def create_fake_posts(posts_range: str):
    """Generate fake posts."""
    faker = Faker()
    posts_range = posts_range.split('-')
    gen_num = random.randint(int(posts_range[0]), int(posts_range[1]))

    if current_user.get_id():
        user_id = current_user.get_id()
    else:
        user_id = 1

    for i in range(gen_num):
        post = Post(author_id=user_id,
                    title=faker.paragraph(nb_sentences=1, variable_nb_sentences=False),
                    body=faker.paragraph(nb_sentences=5, variable_nb_sentences=True))
        db.session.add(post)
    db.session.commit()

    return gen_num


@check_range
def create_fake_revenue(revenue_range: str):
    """Generate fake revenue entries."""
    saving_sources = get_validation_saving_sources()
    revenue_range = revenue_range.split('-')
    gen_num = random.randint(int(revenue_range[0]), int(revenue_range[1]))
    if current_user.get_id():
        user_id = current_user.get_id()
    else:
        user_id = 1

    for i in range(gen_num):
        revenue = BudgetRevenue(user_id=user_id, revenue_value=random.randint(850, 4500),
                                revenue_source=saving_sources[random.randint(0, len(saving_sources)-1)].sources)
        db.session.add(revenue)
    db.session.commit()
    print(f'Added {gen_num} fake revenues to the database.')
    return gen_num


@check_range
def create_fake_saving(saving_range: str):
    """Generate fake savings entries."""
    saving_range = saving_range.split('-')
    gen_num = random.randint(int(saving_range[0]), int(saving_range[1]))
    saving_sources = get_validation_saving_accounts()
    saving_reasons = get_validation_saving_reasons()
    saving_actions = get_validation_saving_action()

    if current_user.get_id():
        user_id = current_user.get_id()
    else:
        user_id = 1

    for i in range(gen_num):
        saving = BudgetSaving(user_id=user_id, saving_value=random.randint(850, 4500),
                              saving_source=saving_sources[random.randint(0, len(saving_sources)-1)].saving_accounts,
                              saving_reason=saving_reasons[random.randint(0, len(saving_reasons)-1)].saving_reason,
                              saving_action=saving_actions[random.randint(0, len(saving_actions)-1)].saving_action_type)
        db.session.add(saving)
    db.session.commit()
    print(f'Added {gen_num} fake saving to the database.')
    return gen_num


@check_range
def create_fake_expense(expense_range: str):
    """Generate fake expense entries."""
    expense_range = expense_range.split('-')
    gen_num = random.randint(int(expense_range[0]), int(expense_range[1]))
    validation_items_categories = get_validation_saving_items()
    saving_sources = get_validation_saving_sources()
    random_int = random.randint(0, len(validation_items_categories)-1)

    if current_user.get_id():
        user_id = current_user.get_id()
    else:
        user_id = 1

    for i in range(gen_num):
        expense = BudgetExpense(user_id=user_id,
                                expense_item=validation_items_categories[random_int].items,
                                expense_value=random.randint(5, 560),
                                expense_item_category=validation_items_categories[random_int].category,
                                expense_source=saving_sources[random.randint(0, len(saving_sources)-1)].sources)
        db.session.add(expense)
    db.session.commit()
    print(f'Added {gen_num} fake expense to the database.')
    return gen_num


@check_range
def create_fake_utilities(utilities_range: str):
    """Generate fake expense entries."""
    utilities_range = utilities_range.split('-')
    gen_num = random.randint(int(utilities_range[0]), int(utilities_range[1]))
    saving_sources = get_validation_saving_sources()

    if current_user.get_id():
        user_id = current_user.get_id()
    else:
        user_id = 1

    faker = Faker()
    for i in range(gen_num):
        utility = BudgetUtilities(user_id=user_id,
                                  utilities_rent_value=random.randint(50, 250),
                                  utilities_energy_value=random.randint(50, 250),
                                  utilities_satellite_value=random.randint(50, 250),
                                  utilities_maintenance_value=random.randint(50, 250),
                                  utilities_info=faker.paragraph(nb_sentences=1, variable_nb_sentences=False),
                                  budget_source=saving_sources[random.randint(0, len(saving_sources)-1)].sources)
        db.session.add(utility)
    db.session.commit()
    print(f'Added {gen_num} fake utility to the database.')
    return gen_num


def create_fake_validation(validation_entries: int):
    """ Generate fake validation entries across all validation tables """
    gen_range = range(1, int(validation_entries))

    for i in gen_range:
        saving_acc = ValidationSavingAccount(saving_accounts=f'Account{i}')
        db.session.add(saving_acc)

        saving_action = ValidationSavingAction(saving_action_type=f'Action{i}')
        db.session.add(saving_action)

        saving_categories = ValidationSavingCategories(categories=f'Categ{i}')
        db.session.add(saving_categories)

        saving_items = ValidationSavingItems(items=f'Item{i}', category=f'Categ{i}')
        db.session.add(saving_items)

        saving_reason = ValidationSavingReason(saving_reason=f'Reasons{i}')
        db.session.add(saving_reason)

        saving_sources = ValidationSavingSources(sources=f'Account{i}')
        db.session.add(saving_sources)
    db.session.commit()
    print(f'Added {validation_entries} validation entries across all tables.')
    return validation_entries


# better-me even though it works, this does not cover the both True values selection situation. Create some escape
#  conditional.
def create_fake_urls(urls_num: int, url_params: bool = False, randomized_params: bool = False):
    """Generate fake expense entries."""
    faker = Faker()
    encode_option = ['encode', 'decode']

    if current_user.get_id():
        user_id = current_user.get_id()
    else:
        user_id = 1

    if not url_params and not randomized_params:

        for i in range(int(urls_num)):
            url_decode_encode = UrlEncodeDecodeParse(user_id=user_id,
                                                     raw_url=faker.uri(),
                                                     encode_option=encode_option[random.randint(0, 1)],
                                                     encoding=encodings[random.randint(0, len(encodings)-1)])
            db.session.add(url_decode_encode)
        db.session.commit()
        print(f'Added {urls_num} fake urls to the database with no parameters.')
    if url_params and not randomized_params:

        for i in range(int(urls_num)):
            random_utm = faker.bothify(text='utm_source=????&utm_medium=?????&utm_campaign=????_####&utm_content=?????')
            url_decode_encode = UrlEncodeDecodeParse(user_id=user_id,
                                                     raw_url=f'{faker.uri()}?{random_utm}',
                                                     encode_option=None,
                                                     encoding=None)
            db.session.add(url_decode_encode)
        db.session.commit()
        print(f'Added {urls_num} fake urls to the database with fake UTM parameters.')
    if not url_params and randomized_params:

        for i in range(int(urls_num)):
            random_utm = faker.bothify(text='???_???=????&??????=?????&###_????=????_####&????###=?????')
            url_decode_encode = UrlEncodeDecodeParse(user_id=user_id,
                                                     raw_url=f'{faker.uri()}?{random_utm}',
                                                     encode_option=None,
                                                     encoding=None)
            db.session.add(url_decode_encode)
        db.session.commit()
        print(f'Added {urls_num} fake urls to the database with fake parameters and fake values.')

    return urls_num


@tests_bp.cli.command('create-fake-users')
@click.argument('users_num')
def cli_create_fake_users(users_num: int):
    create_fake_users(users_num)


@tests_bp.cli.command('create-fake-posts')
@click.argument('posts_range')
def cli_create_fake_posts(posts_range: str):
    create_fake_posts(posts_range)


@tests_bp.cli.command('create-fake-revenue')
@click.argument('revenue_range')
def cli_create_fake_revenue(revenue_range: str):
    create_fake_revenue(revenue_range)


@tests_bp.cli.command('create-fake-saving')
@click.argument('saving_range')
def cli_create_fake_saving(saving_range: str):
    create_fake_saving(saving_range)


@tests_bp.cli.command('create-fake-expense')
@click.argument('expense_range')
def cli_create_fake_expense(expense_range: str):
    create_fake_expense(expense_range)


@tests_bp.cli.command('create-fake-utilities')
@click.argument('utilities_range')
def cli_create_fake_utilities(utilities_range: str):
    create_fake_utilities(utilities_range)


@tests_bp.cli.command('create-fake-validation')
@click.argument('validation_entries')
def cli_create_fake_validation(validation_entries: int):
    create_fake_validation(validation_entries)


@tests_bp.cli.command('create-fake-urls')
@click.argument('urls_num')
@click.argument('url_params', required=False)
@click.argument('randomized_params', required=False)
def cli_create_fake_urls(urls_num: int, url_params: bool = False, randomized_params: bool = False):
    create_fake_urls(urls_num, url_params, randomized_params)
