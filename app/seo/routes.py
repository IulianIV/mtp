from flask import request, send_from_directory
from app.seo import bp
from app import current_app


@bp.route('/robots.txt')
@bp.route('/sitemap.xml')
def static_from_root():
    return send_from_directory(current_app.static_folder, request.path[1:])
