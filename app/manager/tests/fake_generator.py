import random
import click
from faker import Faker
from flask import (
    redirect, render_template, request, url_for
)
from app.manager.db.models import *
from app.manager import tests_bp
from app.manager.protection import form_validated_message, form_error_message
from app.auth.routes import login_required
from app.webtools.routes import encodings
from app.manager.tests.forms import AddFakes

FAKE_POSTS = 15
FAKE_REVENUE = '15-55'
FAKE_SAVING = '3-15'
FAKE_EXPENSE = '500-1860'
FAKE_UTILITIES = '1-12'
FAKE_VALIDATION = 5


# better-me add validation for ranges
@tests_bp.route('/tests/fake-data-generator', methods=('GET', 'POST'))
@login_required
def add_fakes():
    fake_form = AddFakes()

    fake_form.fake_choices.choices = ['Fake Posts', 'Fake Revenue', 'Fake Saving', 'Fake Expense', 'Fake Utilities', 'Fake Validation', 'Fake URLs']

    if request.method == 'POST':
        if fake_form.is_submitted() and fake_form.fake_choices.data != 'Fake URLs':
            fake_choice = fake_form.fake_choices.data
            fake_range = fake_form.fake_number.data

            choice_func_map = {
                'Fake Posts': create_fake_posts,
                'Fake Revenue': create_fake_revenue,
                'Fake Saving': create_fake_saving,
                'Fake Expense': create_fake_expense,
                'Fake Utilities': create_fake_utilities,
                'Fake Validation': create_fake_validation
            }

            fake_data = choice_func_map[fake_choice](fake_range)

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

            form_validated_message(f'Successfully added {fake_data}')

            return redirect(url_for('manager-tests.add_fakes'))

    return render_template('manager/tests/fake_generator.html', fake_form=fake_form)


def create_fake_posts(posts_range: str):
    """Generate fake posts."""
    faker = Faker()
    posts_range = posts_range.split('-')
    gen_num = random.randint(int(posts_range[0]), int(posts_range[1]))

    for i in range(gen_num):
        post = Post(author_id=1, title=faker.paragraph(nb_sentences=1, variable_nb_sentences=False),
                    body=faker.paragraph(nb_sentences=5, variable_nb_sentences=True))
        db.session.add(post)
    db.session.commit()
    print(f'Added {gen_num} fake posts to the database.')
    return gen_num


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
    return gen_num


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
    return gen_num


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
    return gen_num


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
    return gen_num


# fix-me throws IntegrityError. It tries to input data as "accountX" (X being i value) whilst "accountX" already exists
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


# better-me even though it works, this does not cover the both True values selection situation. Create some escape conditional.
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
    if not url_params and randomized_params:

        for i in range(int(urls_num)):
            random_utm = faker.bothify(text='???_???=????&??????=?????&###_????=????_####&????###=?????')
            url_decode_encode = UrlEncodeDecodeParse(raw_url=f'{faker.uri()}?{random_utm}',
                                                     encode_option=None,
                                                     encoding=None)
            db.session.add(url_decode_encode)
        db.session.commit()
        print(f'Added {urls_num} fake urls to the database with fake parameters and fake values.')

    return urls_num


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
