from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'User: {self.username}, with id: {self.id}'


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created = db.Column(db.Date, index=True, nullable=False, default=datetime.utcnow)
    title = db.Column(db.String(90), nullable=False)
    body = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'Post title: {self.title}'


class BudgetRevenue(db.Model):
    __tablename__ = 'budget_revenue'
    id = db.Column(db.Integer, primary_key=True)
    revenue_date = db.Column(db.Date, index=True, nullable=False, default=datetime.utcnow)
    revenue_value = db.Column(db.Float, nullable=False)
    revenue_source = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f'Budget revenue ID: {self.id}'


class BudgetSaving(db.Model):
    __tablename__ = 'budget_saving'
    id = db.Column(db.Integer, primary_key=True)
    saving_date = db.Column(db.Date, index=True, nullable=False, default=datetime.utcnow)
    saving_value = db.Column(db.Float, nullable=False)
    saving_source = db.Column(db.String(20), nullable=False)
    saving_reason = db.Column(db.String(20), nullable=False)
    saving_action = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f'Budget saving ID: {self.id}'


class BudgetExpense(db.Model):
    __tablename__ = 'budget_expense'
    id = db.Column(db.Integer, primary_key=True)
    expense_date = db.Column(db.Date, index=True, nullable=False, default=datetime.utcnow)
    expense_item = db.Column(db.String(20), nullable=False)
    expense_value = db.Column(db.Float, nullable=False)
    expense_item_category = db.Column(db.String(20), nullable=False)
    # fixme implement a way to add foreign keys: the previous implementation throws error
    #   foreign_keys=[BudgetRevenue.revenue_source, BudgetSaving.saving_source]
    expense_source = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f'Budget expense ID: {self.id}'

    def to_dict(self):

        entry_date = self.expense_date
        formatted_date = entry_date.strftime('%Y-%m-%d')

        return {
            'id': self.id,
            'expense_date': formatted_date,
            'expense_item': self.expense_item,
            'expense_value': self.expense_value,
            'expense_item_category': self.expense_item_category,
            'expense_source': self.expense_source

        }


class BudgetUtilities(db.Model):
    __tablename__ = 'budget_utilities'
    id = db.Column(db.Integer, primary_key=True)
    utilities_date = db.Column(db.Date, index=True, nullable=False, default=datetime.utcnow)
    utilities_rent_value = db.Column(db.Float, nullable=False)
    utilities_energy_value = db.Column(db.Float, nullable=False)
    utilities_satellite_value = db.Column(db.Float, nullable=False)
    utilities_maintenance_value = db.Column(db.Float, nullable=False)
    utilities_info = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'Budget utilities id: {self.id}'


class ValidationSavingAccount(db.Model):
    __tablename__ = 'savings_accounts'
    id = db.Column(db.Integer, primary_key=True)
    saving_accounts = db.Column(db.String(10), nullable=False, unique=True)

    def __repr__(self):
        return f'Saving account id: {self.id}'


class ValidationSavingAction(db.Model):
    __tablename__ = 'savings_actions'
    id = db.Column(db.Integer, primary_key=True)
    saving_action_type = db.Column(db.String(10), nullable=False, unique=True)

    def __repr__(self):
        return f'Saving action id: {self.id}'


class ValidationSavingCategories(db.Model):
    __tablename__ = 'saving_categories'
    id = db.Column(db.Integer, primary_key=True)
    categories = db.Column(db.String(20), nullable=False, unique=True)

    def __repr__(self):
        return f'Saving categories id: {self.id}'


class ValidationSavingItems(db.Model):
    __tablename__ = 'saving_items'
    id = db.Column(db.Integer, primary_key=True)
    items = db.Column(db.String(20), nullable=False, unique=True)
    category = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f'Saving items: {self.id}'


class ValidationSavingReason(db.Model):
    __tablename__ = 'saving_reason'
    id = db.Column(db.Integer, primary_key=True)
    saving_reason = db.Column(db.String(25), nullable=False, unique=True)

    def __repr__(self):
        return f'Saving reason id: {self.id}'


class ValidationSavingSources(db.Model):
    __tablename__ = 'saving_sources'
    id = db.Column(db.Integer, primary_key=True)
    sources = db.Column(db.String(10), nullable=False, unique=True)

    def __repr__(self):
        return f'Saving sources id: {self.id}'
