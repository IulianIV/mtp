from flask import request, send_from_directory, render_template

from app import current_app
from app.auth.routes import login_required
from app.seo import bp
from app.seo.gtmspy import GTMSpy

model_gtm_id = 'GTM-T7MRFWX'


@bp.route('/gtm-spy', methods=('GET', 'POST'))
def gtm_spy():

    spy = GTMSpy(model_gtm_id)
    container_url = spy.url
    macro_func = spy.get_functions(spy.tags)
    print(macro_func)
    print(spy.container)
    print(container_url)

    return render_template('seo/gtm_spy.html', model_gtm_path=container_url)


@bp.route('/robots.txt')
@bp.route('/sitemap.xml')
def static_from_root():
    return send_from_directory(current_app.static_folder, request.path[1:])


@bp.route('/error/401')
@login_required
def error_401():
    pass
    return render_template('errors/401.html'), 404


@bp.route('/error/404', methods=('GET',))
@login_required
def error_404():
    pass
    return render_template('errors/404.html')


@bp.route('/error/500', methods=('GET',))
@login_required
def error_500():
    pass
    return render_template('errors/500.html')
