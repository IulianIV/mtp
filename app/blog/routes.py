from flask import (
    redirect, render_template, request, url_for
)
from flask_login import current_user
from werkzeug.exceptions import abort

from app import db
from app.auth.routes import login_required
from app.blog import bp
from app.blog.forms import AddPost, UpdatePost
from app.manager.db.db_interrogations import Query, Insert, Update, Delete
from app.manager.protection import CustomCSRF
from app.manager.protection import form_validated_message, form_error_message

custom_protection = CustomCSRF()
db_queries = Query()
db_insert = Insert()
db_update = Update()
db_delete = Delete()

# TODO handle blog posts pagination. Maybe similar to the one introduced in the Budget App but with no tables.


# TODO show creator of post by username not by author_id
@bp.route('/')
def index():
    posts = db_queries.query_blog_posts()
    return render_template('blog/index.html', posts=posts, author_name=db_queries.get_username_from_post_author,
                           user=db_queries.get_user_from_post_author)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    create_post_form = AddPost()

    user_id = current_user.get_id()
    error = None

    # better-me improve the post creation functionality
    if create_post_form.is_submitted() and create_post_form.validate_on_submit():

        title = create_post_form.post_title.data
        body = create_post_form.post_body.data

        form_validated_message(f'Post with title {title} has been generated!')

        if not title:
            error = 'Title is required.'
        if error is not None:
            form_error_message(f'{error}')
        else:
            db_insert.insert_post(title, body, user_id)
            db.session.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html', create_post_form=create_post_form)


def get_post(post_id, check_author=True):
    user_id = current_user.get_id()

    post = db_queries.query_blog_post(post_id)

    if post is None:
        abort(404, f'Post id {post_id} doesnt exist.')
    if check_author and post.author_id != user_id:
        pass

    return post


@bp.route('/<int:post_id>/update', methods=('GET', 'POST'))
@login_required
def update(post_id):

    update_form = UpdatePost()

    post = get_post(post_id)

    # fixme find new method to show a preview of the previous
    #   posts` body. <textarea> does not seem to have this.

    if request.method == 'POST':

        title = update_form.update_title.data
        body = update_form.update_body.data

        db_update.update_post(title, body, post.id)

        return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post, update_form=update_form)


# better-me Add conditional that logged in user can only delete his own posts.
#   FE wise the button is not accessible but if they access by URL any post can be deleted.
@bp.route('/<int:post_id>/delete', methods=('POST', 'GET'))
@login_required
def delete(post_id):

    get_post(post_id)

    db_delete.delete_post(post_id)
    db.session.commit()

    return redirect(url_for('blog.index'))
