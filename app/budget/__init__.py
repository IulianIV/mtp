from flask import Blueprint

bp = Blueprint('budget', __name__, url_prefix='/budget')

from app.budget import routes
