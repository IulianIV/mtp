import random

import click
from faker import Faker

from app.manager.db.models import *
from app.manager.tests import bp
from app.webtools.routes import encodings

FAKE_POSTS = 15
FAKE_REVENUE = '15-55'
FAKE_SAVING = '3-15'
FAKE_EXPENSE = '500-1860'
FAKE_UTILITIES = '1-12'
FAKE_VALIDATION = 5

# TODO implement a web interface for test units such as the ones below.


@bp.cli.command('create-fake-posts')
@click.argument('posts_number')
def create_fake_posts(posts_number):
    """Generate fake posts."""
    faker = Faker()
    for i in range(int(posts_number)):
        post = Post(author_id=1, title=faker.paragraph(nb_sentences=1, variable_nb_sentences=False),
                    body=faker.paragraph(nb_sentences=5, variable_nb_sentences=True))
        db.session.add(post)
    db.session.commit()
    print(f'Added {posts_number} fake posts to the database.')


@bp.cli.command('create-fake-revenue')
@click.argument('revenue_range')
def create_fake_revenue(revenue_range: str):
    """Generate fake revenue entries."""
    revenue_range = revenue_range.split('-')
    gen_num = random.randint(int(revenue_range[0]), int(revenue_range[1]))

    for i in range(gen_num):
        revenue = BudgetRevenue(revenue_value=random.randint(850, 4500),
                                revenue_source=f'Account{random.randint(1, 5)}')
        db.session.add(revenue)
    db.session.commit()
    print(f'Added {gen_num} fake revenues to the database.')


@bp.cli.command('create-fake-saving')
@click.argument('saving_range')
def create_fake_saving(saving_range: str):
    """Generate fake savings entries."""
    saving_range = saving_range.split('-')
    gen_num = random.randint(int(saving_range[0]), int(saving_range[1]))

    for i in range(gen_num):
        saving = BudgetSaving(saving_value=random.randint(850, 4500),
                              saving_source=f'Account{random.randint(1, 5)}',
                              saving_reason=f'Reasons{random.randint(1, 5)}',
                              saving_action=f'Action{random.randint(1, 5)}')
        db.session.add(saving)
    db.session.commit()
    print(f'Added {gen_num} fake saving to the database.')


@bp.cli.command('create-fake-expense')
@click.argument('expense_range')
def create_fake_expense(expense_range: str):
    """Generate fake expense entries."""
    expense_range = expense_range.split('-')
    gen_num = random.randint(int(expense_range[0]), int(expense_range[1]))

    for i in range(gen_num):
        expense = BudgetExpense(expense_item=f'Item{random.randint(1, 5)}',
                                expense_value=random.randint(5, 560),
                                expense_item_category=f'Categ{random.randint(1, 5)}',
                                expense_source=f'Account{random.randint(1, 5)}')
        db.session.add(expense)
    db.session.commit()
    print(f'Added {gen_num} fake expense to the database.')


@bp.cli.command('create-fake-utilities')
@click.argument('utilities_range')
def create_fake_utilities(utilities_range: str):
    """Generate fake expense entries."""
    utilities_range = utilities_range.split('-')
    gen_num = random.randint(int(utilities_range[0]), int(utilities_range[1]))

    faker = Faker()
    for i in range(gen_num):
        utility = BudgetUtilities(utilities_rent_value=random.randint(50, 250),
                                  utilities_energy_value=random.randint(50, 250),
                                  utilities_satellite_value=random.randint(50, 250),
                                  utilities_maintenance_value=random.randint(50, 250),
                                  utilities_info=faker.paragraph(nb_sentences=1, variable_nb_sentences=False))
        db.session.add(utility)
    db.session.commit()
    print(f'Added {gen_num} fake utility to the database.')


@bp.cli.command('create-fake-validation')
@click.argument('validation_entries')
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


@bp.cli.command('create-fake-urls')
@click.argument('urls_num')
@click.argument('url_params', required=False)
@click.argument('randomized_params', required=False)
def create_fake_urls(urls_num: int, url_params: bool = False, randomized_params: bool = False):
    """Generate fake expense entries."""
    faker = Faker()
    encode_option = ['encode', 'decode']

    if not url_params and not randomized_params:

        for i in range(int(urls_num)):
            url_decode_encode = UrlEncodeDecodeParse(raw_url=faker.uri(),
                                                     encode_option=encode_option[random.randint(0, 1)],
                                                     encoding=encodings[random.randint(1, len(encodings))])
            db.session.add(url_decode_encode)
        db.session.commit()
        print(f'Added {urls_num} fake urls to the database with no parameters.')

    if url_params and not randomized_params:

        for i in range(int(urls_num)):
            random_utm = faker.bothify(text='utm_source=????&utm_medium=?????&utm_campaign=????_####&utm_content=?????')
            url_decode_encode = UrlEncodeDecodeParse(raw_url=f'{faker.uri()}?{random_utm}',
                                                     encode_option=None,
                                                     encoding=None)
            db.session.add(url_decode_encode)
        db.session.commit()
        print(f'Added {urls_num} fake urls to the database with fake UTM parameters.')

    if url_params and randomized_params:

        for i in range(int(urls_num)):
            random_utm = faker.bothify(text='???_???=????&??????=?????&###_????=????_####&????###=?????')
            url_decode_encode = UrlEncodeDecodeParse(raw_url=f'{faker.uri()}?{random_utm}',
                                                     encode_option=None,
                                                     encoding=None)
            db.session.add(url_decode_encode)
        db.session.commit()
        print(f'Added {urls_num} fake urls to the database with fake parameters and fake values.')
