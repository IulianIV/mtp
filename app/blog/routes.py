from flask import (
    redirect, render_template, request, url_for
)
from flask_login import current_user
from werkzeug.exceptions import abort

from app import db
from app.auth.routes import login_required
from app.blog import bp
from app.blog.forms import AddPost, UpdatePost
from app.manager.db.db_interrogations import (
    query_blog_posts, get_username_from_post_author, get_user_from_post_author, insert_post, query_blog_post,
    update_post, delete_post
)
from app.manager.helpers import form_validated_message, form_error_message, CustomCSRF, app_endpoints

custom_protection = CustomCSRF()
blog_index_entrypoint = app_endpoints['blog_index']


# TODO add edited info. New field in database and update on edit/save
# TODO handle blog posts pagination. Maybe similar to the one introduced in the Budget App but with no tables.
# TODO Add Post Carousel. Split each slide to 4 posts.
#   Show Arrows and Indicators. Indicators should be as many slides there are.
# TODO if you want to add filtering/sorting the above proposed carousel implementation might not be so good.
# TODO add Post Image upload functionality. Upload images by button, drag-and-drop.
#   preview images after upload. When creating a post have a default image shown. On hover show a greyed watermark
#   suggesting you can upload. Show a thumbnail that says you can upload.
#   upon upload store physically in folder. If the picture is changed delete old one and replace with new.
#   if on image selection they change mind and what to upload a different one, what is the solution?
#   how can the image be previewed as is without it being uploaded?
# TODO add image edit/replace functionality to edit post.
# TODO add data base query that on post creation add a image path file, if default send directly to default image.
# TODO add database query to delete post image after post is deleted.
# TODO add helper functions for image_naming, image_move do right folder, image_query, image_clean
#   and a function to make sure there are no duplicates.
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
    if request.method == 'POST':

        if create_post_form.is_submitted() and create_post_form.validate_on_submit():

            title = create_post_form.post_title.data
            body = create_post_form.post_body.data
            image_uuid = create_post_form.image_uuid.data

            image_name = image_uuid + ".jpg"

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

    if request.method == 'GET':
        update_form.update_body.data = post.body
        update_form.update_title.data = post.title

    if request.method == 'POST':
        title = update_form.update_title.data
        body = update_form.update_body.data

        update_post(user_id, title, body, post_id)

        return redirect(url_for(blog_index_entrypoint))

    return render_template('blog/update.html', post=post, update_form=update_form)


# better-me Add conditional that logged in user can only delete his own posts.
#   FE wise the button is not accessible but if they access by URL any post can be deleted.
@bp.route('/<int:post_id>/delete', methods=('POST', 'GET'))
@login_required
def delete(post_id):
    user_id = current_user.get_id()

    delete_post(user_id, post_id)
    db.session.commit()

    return redirect(url_for(blog_index_entrypoint))
