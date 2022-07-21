from flask import Blueprint

bp = Blueprint('mrk', __name__)

from app.mrk import routes
