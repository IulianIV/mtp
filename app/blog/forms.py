from flask_wtf import FlaskForm
from wtforms.fields import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class AddPost(FlaskForm):
    post_title = StringField('Post title', validators=[DataRequired()])
    post_body = TextAreaField('Post body', validators=[DataRequired()])
    submit_post = SubmitField()


class UpdatePost(FlaskForm):
    update_title = StringField('Post title', validators=[DataRequired()])
    update_body = TextAreaField('Post body', validators=[DataRequired()])
    submit_update = SubmitField()
