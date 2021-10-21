from flask import (
    redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from app.blog.forms import AddPost, UpdatePost
from app.manager.protection import form_validated_message, form_error_message
from app.manager.protection import CustomCSRF
from app.auth.routes import login_required
from app import db
from app.manager.db.db_interrogations import Query, Insert, Update, Delete
from app.blog import bp
from flask_login import current_user

custom_protection = CustomCSRF()


# TODO fix the template login info grabbing problem across all templates


class BlogDbConnector:
    def __init__(self):
        self.db_queries = Query()
        self.db_insert = Insert()
        self.db_update = Update()
        self.db_delete = Delete()

    @property
    def query_blog_posts(self):
        return self.db_queries.query_blog_posts()

    def query_blog_post(self, post_id):
        return self.db_queries.query_blog_post(post_id)

    def insert_post(self, title, body, user_id):
        return self.db_insert.insert_post(title, body, user_id)

    def update_post(self, title, body, post_id):
        return self.db_update.update_post(title, body, post_id)

    def delete_post(self, post_id):
        return self.db_delete.delete_post(post_id)


@bp.route('/')
def index():
    blog_connect = BlogDbConnector()

    posts = blog_connect.query_blog_posts
    return render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    blog_connect = BlogDbConnector()
    create_post_form = AddPost()

    user_id = current_user.get_id()
    error = None

    if request.method == 'POST':

        # better-me improve the functionality
        if create_post_form.is_submitted() and create_post_form.validate_on_submit():

            title = create_post_form.post_title.data
            body = create_post_form.post_body.data

            form_validated_message(f'Post with title {title} has been generated!')

            if not title:
                error = 'Title is required.'
            if error is not None:
                form_error_message(f'{error}')
            else:
                blog_connect.insert_post(title, body, user_id)
                db.commit()
                return redirect(url_for('app.index'))

    return render_template('mtp/create.html', create_post_form=create_post_form)


def get_post(post_id, check_author=True):
    blog_connect = BlogDbConnector()
    user_id = current_user.get_id()

    post = blog_connect.query_blog_post(post_id)

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(post_id))
    if check_author and post.author_id != user_id:
        abort(403)

    return post


@bp.route('/<int:post_id>/update', methods=('GET', 'POST'))
@login_required
def update(post_id):
    blog_connect = BlogDbConnector()

    update_form = UpdatePost()

    post = get_post(post_id)

    # fixme find new method to show a preview of the previous
    #   posts` body. <textarea> does not seem to have this.

    if request.method == 'POST':

        title = update_form.update_title.data
        body = update_form.update_body.data

        blog_connect.update_post(title, body, post['id'])

        return redirect(url_for('mtp.index'))

    return render_template('mtp/update.html', post=post, update_form=update_form)


@bp.route('/<int:post_id>/delete', methods=('POST', 'GET'))
@login_required
def delete(post_id):
    blog_connect = BlogDbConnector()

    get_post(post_id)

    blog_connect.delete_post(post_id)
    db.commit()

    return redirect(url_for('mtp.index'))


# better-me find a new place for these views
@bp.route('/error-page/401', methods=('GET',))
@login_required
def error_401():
    pass
    return render_template('401.html')


@bp.route('/error-page/404', methods=('GET',))
@login_required
def error_404():
    pass
    return render_template('404.html')


@bp.route('/error-page/500', methods=('GET',))
@login_required
def error_500():
    pass
    return render_template('500.html')
