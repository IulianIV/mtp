from flask import Blueprint

bp = Blueprint('mrk', __name__, url_prefix='/marketing')

from app.mrk import routes
