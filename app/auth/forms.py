from flask_wtf import FlaskForm

from wtforms.fields import PasswordField, StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired, EqualTo


class LoginForm(FlaskForm):
    # better-me consider the possibility to add Form names such as "Username" as a parameter
    #   to the Form Field instantiation
    # TODO add action="" and novalidate to all forms. novalidate to let validation be done server side
    #   action="" when needed, if the forms needs to be sent to a different URL. if empty sends to current URL.
    # TODO add validators back
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('remember me')
    submit = SubmitField()


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_retype = PasswordField('Retype password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField()
