from flask import Blueprint

bp = Blueprint('mtp', __name__)

from app.blog import routes
