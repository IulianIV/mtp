from flask import (
    redirect, render_template, request
)
from flask_login import current_user
from werkzeug.exceptions import abort

from app.auth.routes import login_required
from app.blog import bp
from app.blog.forms import AddPost, UpdatePost
from app.manager.db.db_interrogations import *
from app.manager.protection import CustomCSRF
from app.manager.protection import form_validated_message, form_error_message

custom_protection = CustomCSRF()


# TODO handle blog posts pagination. Maybe similar to the one introduced in the Budget App but with no tables.
@bp.route('/')
def index():
    posts = query_blog_posts()
    return render_template('blog/index.html', posts=posts, author_name=get_username_from_post_author,
                           user=get_user_from_post_author)


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
            insert_post(title, body, user_id)
            db.session.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html', create_post_form=create_post_form)


# fixme Fix logic when someone accesses an post URL with a non-existent ID
def get_post(author_id, post_id, check_author=True):
    user_id = current_user.get_id()

    post = query_blog_post(author_id, post_id)

    if post is None:
        abort(404, f'Post id {post_id} doesnt exist.')
    if check_author and post.author_id != user_id:
        pass

    return post


# TODO Check logic and functionality
@bp.route('/<int:post_id>/update', methods=('GET', 'POST'))
@login_required
def update(post_id):

    update_form = UpdatePost()
    user_id = current_user.get_id()

    post = get_post(user_id, post_id)

    # fixme find new method to show a preview of the previous
    #   posts` body. <textarea> does not seem to have this.

    if request.method == 'GET':
        update_form.update_body.data = post.body
        update_form.update_title.data = post.title

    if request.method == 'POST':

        title = update_form.update_title.data
        body = update_form.update_body.data

        update_post(user_id, title, body, post_id)

        return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post, update_form=update_form)


# better-me Add conditional that logged in user can only delete his own posts.
#   FE wise the button is not accessible but if they access by URL any post can be deleted.
@bp.route('/<int:post_id>/delete', methods=('POST', 'GET'))
@login_required
def delete(post_id):
    user_id = current_user.get_id()

    delete_post(user_id, post_id)
    db.session.commit()

    return redirect(url_for('blog.index'))
