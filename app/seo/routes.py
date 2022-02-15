from flask import request, send_from_directory, render_template

from app import current_app, Config
from app.auth.routes import login_required
from app.manager.helpers import download_gtm_container_from_url, get_container_url, check_for_script
from app.seo import bp
from app.seo.gtmspy import GTMSpy

model_gtm_id = 'GTM-T7MRFWX'


@bp.route('/gtm-spy', methods=('GET', 'POST'))
def gtm_spy():

    if check_for_script(model_gtm_id):
        print('GTM Script for given ID already exists.')
    else:
        download_gtm_container_from_url(Config.GTM_SPY_UPLOAD_PATH, model_gtm_id)

    test = GTMSpy(model_gtm_id)
    print(test)

    for function in test.macros():
        print(function)

    for tag in test.tags():
        print(tag)

    for predicate in test.predicates():
        print(predicate)

    for rule in test.rules():
        print(rule)

    return render_template('seo/gtm_spy.html', model_gtm_path=get_container_url(model_gtm_id))


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
