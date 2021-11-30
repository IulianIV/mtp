from flask import Blueprint

bp = Blueprint('seo', __name__)

from app.seo import routes
