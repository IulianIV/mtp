import random

from faker import Faker

from app import with_appcontext
from app.manager.db.models import *
from app.manager.tests import bp

FAKE_POSTS = 15
FAKE_REVENUE = random.randint(15, 55)
FAKE_SAVING = random.randint(3, 15)
FAKE_EXPENSE = random.randint(500, 1860)
FAKE_UTILITIES = random.randint(1, 12)
FAKE_VALIDATION = random.randint(5, 35)

# better-me Make the implementation more dynamic and cli friendly.
# better-me grab user values as arguments.
# TODO rename sub-app.
# TODO create a faker for URLs. There is fake.url() also add condition for URL parameters random generation.
#   Either by passing random set of known params (e.g. UTM) or completely random where it generates an arbitrary
#   number of parameters (randomized) and corresponding values (randomized)
# TODO add cli.arguments if needed and cli.options where can be used.


@bp.cli.command('create-fake-posts')
def create_fake_posts():
    """Generate fake posts."""
    faker = Faker()
    for i in range(FAKE_POSTS):
        post = Post(author_id=1, title=faker.paragraph(nb_sentences=1, variable_nb_sentences=False),
                    body=faker.paragraph(nb_sentences=5, variable_nb_sentences=True))
        db.session.add(post)
    db.session.commit()
    print(f'Added {FAKE_POSTS} fake posts to the database.')


@bp.cli.command('create-fake-revenue')
def create_fake_revenue():
    """Generate fake revenue entries."""
    faker = Faker()
    for i in range(FAKE_REVENUE):
        revenue = BudgetRevenue(revenue_value=random.randint(850, 4500),
                                revenue_source=f'Account{random.randint(1, 5)}')
        db.session.add(revenue)
    db.session.commit()
    print(f'Added {FAKE_REVENUE} fake revenues to the database.')


@bp.cli.command('create-fake-saving')
def create_fake_saving():
    """Generate fake savings entries."""
    faker = Faker()
    for i in range(FAKE_SAVING):
        saving = BudgetSaving(saving_value=random.randint(850, 4500),
                              saving_source=f'Account{random.randint(1, 5)}',
                              saving_reason=f'Reasons{random.randint(1, 5)}',
                              saving_action=f'Action{random.randint(1, 5)}')
        db.session.add(saving)
    db.session.commit()
    print(f'Added {FAKE_SAVING} fake saving to the database.')


@bp.cli.command('create-fake-expense')
def create_fake_expense():
    """Generate fake expense entries."""
    faker = Faker()
    for i in range(FAKE_EXPENSE):
        expense = BudgetExpense(expense_item=f'Item{random.randint(1, 5)}',
                                expense_value=random.randint(5, 560),
                                expense_item_category=f'Categ{random.randint(1, 5)}',
                                expense_source=f'Account{random.randint(1, 5)}')
        db.session.add(expense)
    db.session.commit()
    print(f'Added {FAKE_EXPENSE} fake expense to the database.')


@bp.cli.command('create-fake-utilities')
def create_fake_utilities():
    """Generate fake expense entries."""
    faker = Faker()
    for i in range(FAKE_UTILITIES):
        utility = BudgetUtilities(utilities_rent_value=random.randint(50, 250),
                                  utilities_energy_value=random.randint(50, 250),
                                  utilities_satellite_value=random.randint(50, 250),
                                  utilities_maintenance_value=random.randint(50, 250),
                                  utilities_info=faker.paragraph(nb_sentences=1, variable_nb_sentences=False))
        db.session.add(utility)
    db.session.commit()
    print(f'Added {FAKE_UTILITIES} fake utility to the database.')


@bp.cli.command('create-fake-validation')
def create_fake_validation():
    """ Generate fake validation entries across all validation tables """
    gen_range = range(1, 5)

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
    print(f'Added 5 validation entries across all tables.')


@bp.cli.command('fake-all')
@with_appcontext
def fake_all():
    """ Automatically populate the whole database with fake data. """
    create_fake_validation()
    create_fake_posts()
    create_fake_utilities()
    create_fake_expense()
    create_fake_revenue()
    create_fake_saving()
    print('Successfully populated the database with fake data!')
