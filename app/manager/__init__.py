from flask import Blueprint

tests_bp = Blueprint('manager-tests', __name__, cli_group=None, url_prefix='/manager')
