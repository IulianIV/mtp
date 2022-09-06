from flask import Blueprint

bp = Blueprint('permissions', __name__, url_prefix='/permissions')

from app.manager.permissions import routes
