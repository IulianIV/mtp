from datetime import datetime
from hashlib import md5

from flask import url_for
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import login, db

# TODO Add permissions Table and migrate/upgrade
# TODO add last_seen logic
# TODO update ALL VARCHAR lengths. They are WAY too short now.

user_id_fk = 'user.id'
saving_sources_fk = 'saving_sources.sources'
fe_date_format = '%Y-%m-%d'


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_profile_id = db.relationship('UserProfile')
    budget_revenue_id = db.relationship('BudgetRevenue', lazy='dynamic')
    budget_saving_id = db.relationship('BudgetSaving', lazy='dynamic')
    budget_expense_id = db.relationship('BudgetExpense', lazy='dynamic')
    budget_utilities_id = db.relationship('BudgetUtilities', lazy='dynamic')
    url_decode_parse_id = db.relationship('UrlEncodeDecodeParse')
    username = db.Column(db.String(15), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(120), index=True, unique=True)
    posts = db.relationship('Post', lazy='dynamic')
    last_seen = db.Column(db.DateTime, default=datetime.utcnow())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def __repr__(self):
        return f'User: {self.username}, with id: {self.id}'


class UserProfile(db.Model):
    __tablename__ = 'user_profile'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey(user_id_fk), nullable=False, unique=True)
    bio = db.Column(db.String(12), unique=False, nullable=True)
    avatar = db.Column(db.String(256), unique=False, nullable=True)


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    title = db.Column(db.String(90), nullable=False, index=True)
    body = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'Post title: {self.title}'


class BudgetRevenue(db.Model):
    __tablename__ = 'budget_revenue'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey(user_id_fk))
    revenue_date = db.Column(db.Date, index=True, nullable=False, default=datetime.utcnow)
    revenue_value = db.Column(db.Float, nullable=False)
    revenue_source = db.Column(db.String(20), db.ForeignKey(saving_sources_fk), nullable=False)

    def __repr__(self):
        return f'Budget revenue ID: {self.id}'

    def to_dict(self):

        entry_date = self.revenue_date
        formatted_date = entry_date.strftime(fe_date_format)

        return {
            'id': self.id,
            'revenue_date': formatted_date,
            'revenue_value': self.revenue_value,
            'revenue_source': self.revenue_source,
            'entry_options': '<a href="'
                             + url_for('budget.update_revenue_entries', revenue_id=self.id) +
                             '"class="btn btn-primary">Edit</a>&nbsp;<a href="'
                             + url_for('budget.delete_revenue_entries', revenue_id=self.id) +
                             '" class="btn btn-danger">Delete</a>'
        }


class BudgetSaving(db.Model):
    __tablename__ = 'budget_saving'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey(user_id_fk))
    saving_date = db.Column(db.Date, index=True, nullable=False, default=datetime.utcnow)
    saving_value = db.Column(db.Float, nullable=False)
    saving_source = db.Column(db.String(20), db.ForeignKey('savings_accounts.saving_accounts'), nullable=False,
                              index=True)
    saving_reason = db.Column(db.String(20), db.ForeignKey('saving_reason.saving_reason'), nullable=False,
                              index=True)
    saving_action = db.Column(db.String(20), db.ForeignKey('savings_actions.saving_action_type'),
                              nullable=False, index=True)

    def __repr__(self):
        return f'Budget saving ID: {self.id}'

    def to_dict(self):

        entry_date = self.saving_date
        formatted_date = entry_date.strftime(fe_date_format)

        return {
            'id': self.id,
            'saving_date': formatted_date,
            'saving_value': self.saving_value,
            'saving_source': self.saving_source,
            'saving_reason': self.saving_reason,
            'saving_action': self.saving_action,
            'entry_options': '<a href="'
                             + url_for('budget.update_saving_entries', saving_id=self.id) +
                             '"class="btn btn-primary">Edit</a>&nbsp;<a href="'
                             + url_for('budget.delete_saving_entries', saving_id=self.id) +
                             '" class="btn btn-danger">Delete</a>'
        }


class BudgetExpense(db.Model):
    __tablename__ = 'budget_expense'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey(user_id_fk))
    expense_date = db.Column(db.Date, index=True, nullable=False, default=datetime.utcnow)
    expense_item = db.Column(db.String(20), db.ForeignKey('saving_items.items'), nullable=False)
    expense_value = db.Column(db.Float, nullable=False)
    expense_item_category = db.Column(db.String(20), db.ForeignKey('saving_categories.categories'),
                                      nullable=False)
    expense_source = db.Column(db.String(20), db.ForeignKey(saving_sources_fk), nullable=False)

    def __repr__(self):
        return f'Budget expense ID: {self.id}'

    def to_dict(self):

        entry_date = self.expense_date
        formatted_date = entry_date.strftime(fe_date_format)

        return {
            'id': self.id,
            'expense_date': formatted_date,
            'expense_item': self.expense_item,
            'expense_value': self.expense_value,
            'expense_item_category': self.expense_item_category,
            'expense_source': self.expense_source,
            'entry_options': '<a href="'
                             + url_for('budget.update_expense_entries', expense_id=self.id) +
                             '"class="btn btn-primary">Edit</a>&nbsp;<a href="'
                             + url_for('budget.delete_expense_entries', expense_id=self.id) +
                             '" class="btn btn-danger">Delete</a>'
        }


class BudgetUtilities(db.Model):
    __tablename__ = 'budget_utilities'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey(user_id_fk))
    utilities_date = db.Column(db.Date, index=True, nullable=False, default=datetime.utcnow)
    utilities_rent_value = db.Column(db.Float, nullable=False)
    utilities_energy_value = db.Column(db.Float, nullable=False)
    utilities_satellite_value = db.Column(db.Float, nullable=False)
    utilities_maintenance_value = db.Column(db.Float, nullable=False)
    utilities_info = db.Column(db.Text, nullable=False)
    budget_source = db.Column(db.String(20), db.ForeignKey(saving_sources_fk))

    def __repr__(self):
        return f'Budget utilities id: {self.id}'

    def to_dict(self):

        entry_date = self.utilities_date
        formatted_date = entry_date.strftime(fe_date_format)

        return {
            'id': self.id,
            'utilities_date': formatted_date,
            'utilities_rent_value': self.utilities_rent_value,
            'utilities_energy_value': self.utilities_energy_value,
            'utilities_satellite_value': self.utilities_satellite_value,
            'utilities_maintenance_value': self.utilities_maintenance_value,
            'utilities_info': self.utilities_info,
            'budget_source': self.budget_source,
            'entry_options': '<a href="'
                             + url_for('budget.update_utilities_entry', utility_id=self.id) +
                             '"class="btn btn-primary">Edit</a>&nbsp;<a href="'
                             + url_for('budget.delete_utilities_entry', utility_id=self.id) +
                             '" class="btn btn-danger">Delete</a>'
        }


class ValidationSavingAccount(db.Model):
    __tablename__ = 'savings_accounts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    saving_accounts = db.Column(db.String(10), nullable=False, unique=True)
    budget_saving_id = db.relationship('BudgetSaving')

    def __repr__(self):
        return f'Saving account id: {self.id}'


class ValidationSavingAction(db.Model):
    __tablename__ = 'savings_actions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    saving_action_type = db.Column(db.String(10), nullable=False, unique=True)
    budget_saving_id = db.relationship('BudgetSaving')

    def __repr__(self):
        return f'Saving action id: {self.id}'


class ValidationSavingCategories(db.Model):
    __tablename__ = 'saving_categories'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    categories = db.Column(db.String(20), nullable=False, unique=True)
    budget_expense_id = db.relationship('BudgetExpense')
    validation_saving_item_id = db.relationship('ValidationSavingItems')

    def __repr__(self):
        return f'Saving categories id: {self.id}'


class ValidationSavingItems(db.Model):
    __tablename__ = 'saving_items'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    budget_expense_id = db.relationship('BudgetExpense')
    category = db.Column(db.String(20), db.ForeignKey('saving_categories.categories'), nullable=False)
    items = db.Column(db.String(45), nullable=False, unique=True)

    def __repr__(self):
        return f'Saving items: {self.id}'


class ValidationSavingReason(db.Model):
    __tablename__ = 'saving_reason'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    saving_reason = db.Column(db.String(25), nullable=False, unique=True)
    budget_saving_id = db.relationship('BudgetSaving')

    def __repr__(self):
        return f'Saving reason id: {self.id}'


class ValidationSavingSources(db.Model):
    __tablename__ = 'saving_sources'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sources = db.Column(db.String(10), nullable=False, unique=True)
    budget_revenue_id = db.relationship('BudgetRevenue')
    budget_expense_id = db.relationship('BudgetExpense')
    budget_utilities_id = db.relationship('BudgetUtilities')

    def __repr__(self):
        return f'Saving sources id: {self.id}'


class UrlEncodeDecodeParse(db.Model):
    __tablename__ = 'url_encode_decode_parse'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey(user_id_fk))
    url_date = db.Column(db.Date, index=True, nullable=False, default=datetime.utcnow)
    raw_url = db.Column(db.String(1000), nullable=False)
    encode_option = db.Column(db.String(10))
    encoding = db.Column(db.String(10))

    def __repr__(self):
        return f'URL with id {self.id} is: {self.raw_url}'
