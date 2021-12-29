from flask_wtf import FlaskForm

from wtforms.fields import PasswordField, StringField, BooleanField, SubmitField, EmailField
from wtforms.validators import DataRequired, EqualTo


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('remember me')
    submit = SubmitField()


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_retype = PasswordField('Retype password', validators=[DataRequired(), EqualTo('password')])
    email = EmailField('e-mail', validators=[DataRequired()])
    submit = SubmitField()
