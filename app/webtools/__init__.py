from flask import Blueprint

bp = Blueprint('webtools', __name__, url_prefix='/web-tools')

from app.webtools import routes
