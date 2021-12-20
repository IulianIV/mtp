import random
from app import db
import sys
from flask.cli import with_appcontext
import click
from faker import Faker
from app.manager.db.models import *

FAKE_POSTS = 15
FAKE_REVENUE = random.randint(15, 55)
FAKE_SAVING = random.randint(3, 15)
FAKE_EXPENSE = random.randint(500, 1860)
FAKE_UTILITIES = random.randint(1, 12)
FAKE_VALIDATION = random.randint(5, 35)

# better-me Make the implementation more dynamic and client friendly.


@click.command('create-fake-posts')
@with_appcontext
def create_fake_posts(n):
    """Generate fake users."""
    faker = Faker()
    for i in range(n):
        post = Post(author_id=1,
                    created=faker.date(),
                    title=faker.paragraph(nb_sentences=1, varaible_nb_sentences=False),
                    body=faker.paragraph(nb_sentences=5, varaible_nb_sentences=True))
        db.session.add(post)
    db.session.commit()
    print(f'Added {n} fake users to the database.')


@click.command('create-fake-revenue')
@with_appcontext
def create_fake_revenue(n):
    """Generate fake revenue entries."""
    faker = Faker()
    for i in range(n):
        revenue = BudgetRevenue(revenue_date=faker.date(),
                                revenue_value=random.randint(850, 4500),
                                revenue_source=f'Account{random.randint(1, 5)}')
        db.session.add(revenue)
    db.session.commit()
    print(f'Added {n} fake revenues to the database.')


@click.command('create-fake-saving')
@with_appcontext
def create_fake_saving(n):
    """Generate fake savings entries."""
    faker = Faker()
    for i in range(n):
        saving = BudgetSaving(saving_date=faker.date(),
                              saving_value=random.randint(850, 4500),
                              saving_source=f'Account{random.randint(1, 5)}',
                              saving_reason=f'Reasons{random.randint(1, 5)}',
                              saving_action=f'Action{random.randint(1, 5)}')
        db.session.add(saving)
    db.session.commit()
    print(f'Added {n} fake saving to the database.')


@click.command('create-fake-expense')
@with_appcontext
def create_fake_expense(n):
    """Generate fake expense entries."""
    faker = Faker()
    for i in range(n):
        expense = BudgetExpense(expense_date=faker.date(),
                                expense_item=f'Item{random.randint(1, 5)}',
                                expense_value=random.randint(5, 560),
                                expense_item_category=f'Categ{random.randint(1, 5)}',
                                expense_source=f'Account{random.randint(1, 5)}')
        db.session.add(expense)
    db.session.commit()
    print(f'Added {n} fake expense to the database.')


@click.command('create-fake-utilities')
@with_appcontext
def create_fake_utilities(n):
    """Generate fake expense entries."""
    faker = Faker()
    for i in range(n):
        utility = BudgetUtilities(utilities_date=faker.date(),
                                  utilities_rent_value=random.randint(50, 250),
                                  utilities_energy_value=random.randint(50, 250),
                                  utilities_satellite_value=random.randint(50, 250),
                                  utilities_maintenance_value=random.randint(50, 250),
                                  utilities_info=faker.paragraph(nb_sentences=1, varaible_nb_sentences=False))
        db.session.add(utility)
    db.session.commit()
    print(f'Added {n} fake utility to the database.')


@click.command('create-fake-validation')
@with_appcontext
def create_fake_validation():
    gen_range = range(1, 5)

    for i in gen_range:
        saving_acc = ValidationSavingAccount(saving_accounts=f'Account{i}')
        db.session.add(saving_acc)

        saving_action = ValidationSavingAction(saving_action_type=f'Action{i}')
        db.session.add(saving_action)

        saving_categories = ValidationSavingCategories(categories=f'Categ{i}')
        db.session.add(saving_categories)

        saving_items = ValidationSavingItems(item=f'Item{i}', category=f'Categ{i}')
        db.session.add(saving_items)

        saving_reason = ValidationSavingReason(saving_reason=f'Reasons{i}')
        db.session.add(saving_reason)

        saving_sources = ValidationSavingSources(sources=f'Account{i}')
        db.session.add(saving_sources)
    db.session.commit()


if __name__ == '__main__':
    create_fake_validation()

