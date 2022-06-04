from flask import (
    redirect, render_template, request, url_for
)
from flask_login import current_user

from app import db
from app.auth.routes import login_required
from app.blog import bp
from app.blog.forms import AddPost, UpdatePost
from app.manager.db.db_interrogations import (
    query_blog_posts, get_username_from_post_author, get_user_from_post_author, insert_post, query_blog_post,
    update_post, delete_post
)
from app.manager.helpers import form_validated_message, form_error_message, CustomCSRF, app_endpoints, \
    delete_post_image, post_image_rename

custom_protection = CustomCSRF()
blog_index_entrypoint = app_endpoints['blog_index']
login_endpoint = app_endpoints['login']


@bp.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for(login_endpoint))
    posts = query_blog_posts()
    return render_template('blog/index.html', posts=posts, author_name=get_username_from_post_author,
                           user=get_user_from_post_author)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    create_post_form = AddPost()

    user_id = current_user.get_id()
    error = None

    if request.method == 'POST':

        if create_post_form.is_submitted() and create_post_form.validate_on_submit():

            title = create_post_form.post_title.data
            body = create_post_form.post_body.data
            image_uuid = create_post_form.image_uuid.data

            if image_uuid != '':
                image_name = post_image_rename(image_uuid)
            else:
                image_name = None

            if not title:
                error = 'Title is required.'
            if error is not None:
                form_error_message(f'{error}')
            else:
                insert_post(title, body, user_id, image_name)
                db.session.commit()
                form_validated_message(f'Post with title {title} has been generated!')
        return redirect(url_for(blog_index_entrypoint))
    return render_template('blog/create.html', create_post_form=create_post_form)


@bp.route('/<int:post_id>/update', methods=('GET', 'POST'))
@login_required
def update(post_id):
    update_form = UpdatePost()
    user_id = current_user.get_id()

    post = query_blog_post(user_id, post_id)

    if request.method == 'GET':
        update_form.update_body.data = post.body
        update_form.update_title.data = post.title

    if request.method == 'POST':
        title = update_form.update_title.data
        body = update_form.update_body.data
        image_uuid = update_form.image_uuid.data

        if image_uuid != '':
            image_name = post_image_rename(image_uuid)
        else:
            image_name = None

        current_post_image = post.post_image_name

        if current_post_image and image_name is not None:
            delete_post_image(current_post_image)
            update_post(user_id, title, body, post_id, image_name)
        elif current_post_image is None and image_name is not None:
            update_post(user_id, title, body, post_id, image_name)
        else:
            update_post(user_id, title, body, post_id, current_post_image)

        return redirect(url_for(blog_index_entrypoint))

    return render_template('blog/update.html', post=post, update_form=update_form)


@bp.route('/<int:post_id>/delete', methods=('POST', 'GET'))
@login_required
def delete(post_id):
    user_id = current_user.get_id()

    post = query_blog_post(user_id, post_id)

    delete_post_image(post.post_image_name)

    delete_post(user_id, post_id)
    db.session.commit()

    return redirect(url_for(blog_index_entrypoint))
