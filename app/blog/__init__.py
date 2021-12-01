from flask import Blueprint

bp = Blueprint('blog', __name__)

from app.blog import routes

# TODO revamp the Blog functionality.
#   show the posts specific to a blog not in a tabular form.
#   add more data tot he posts table
