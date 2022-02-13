from flask_wtf import FlaskForm

from wtforms.fields import StringField, TextAreaField, SubmitField, HiddenField
from wtforms.validators import DataRequired

# TODO add a post title 30 char limit
# TODO add a post body 255 char limit


class AddPost(FlaskForm):
    post_title = StringField('Title', validators=[DataRequired()])
    post_body = TextAreaField('Body', validators=[DataRequired()])
    image_uuid = HiddenField('Image UUID', validators=[DataRequired()])
    submit_post = SubmitField()


class UpdatePost(FlaskForm):
    update_title = StringField('Update title', validators=[DataRequired()])
    update_body = TextAreaField('Update body', validators=[DataRequired()])
    submit_update = SubmitField()
