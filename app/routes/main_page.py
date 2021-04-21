import time
from functools import wraps

from flask import render_template, Blueprint, redirect, flash, request, url_for
from flask_login import current_user, login_user
import asyncio
import base64
from pathlib import Path
import os

from flask_login.utils import login_required
from sqlalchemy import desc, or_, and_

from app import db_sess, storage
from app.models import Post, User, Comment, Pair, Image
from app.forms import PostForm, CommentForm, EditCommentForm

from PIL import Image as PILImage
from io import BytesIO
from os import mkdir
from flask_cloudy import FileStorage, Object

bp = Blueprint('main', __name__)


def async_action(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapped


@bp.route('/')
@bp.route('/index')
def index():
    posts = db_sess.query(Post).filter(Post.archived == False).order_by(desc(Post.start_date)).all()
    data = []
    for post in posts:
        images = db_sess.query(Image).filter_by(post_id=post.id).all()
        urls = []
        for image in images:
            image_obj = storage.get(f'image-{post.id}-{image.image_id}.png')
            if image_obj and isinstance(image_obj, Object):
                urls.append(image_obj.url)

        data.append([post, urls])
    return render_template('index.html', posts=data)


@bp.route("/create_post", methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if request.method == "POST":
        post = Post()
        post.title = request.form.get("title")
        post.description = request.form.get("description")
        post.tags = request.form.get("tags")
        post.creator = current_user.id
        current_user.posts.append(post)
        db_sess.merge(current_user)
        db_sess.commit()
        db_sess.flush()

        for i, base64_image in enumerate(request.form.get('images').split()):
            image = Image()
            image.user_id = current_user.id
            image.post_id = post.id
            image.image_id = i

            db_sess.add(image)
            db_sess.commit()
            db_sess.flush()

            image_stream = BytesIO(base64.b64decode(base64_image[22:]))
            storage.upload(FileStorage(image_stream, filename=f'image-{post.id}-{image.image_id}.png'))

        db_sess.commit()
        return redirect('/')
    return render_template('add_post.html', title='Создание объявления',
                           form=form)


@bp.route('/profile/my_posts')
def my_posts():
    posts = db_sess.query(Post).filter(
        Post.creator == current_user.id).order_by(desc(Post.start_date)).all()
    images = list(map(lambda x: x.image.split(), posts))
    data = []
    for i in range(len(images)):
        data.append([posts[i], images[i]])
    return render_template('my_posts.html', posts=data)


@bp.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    form = PostForm()
    post = db_sess.query(Post).filter(
        Post.id == post_id).first()
    if request.method == "POST":
        post.title = request.form.get("title")
        post.description = request.form.get("description")
        post.tags = request.form.get("tags")
        post.creator = current_user.id

        current_user.posts.append(post)
        db_sess.merge(current_user)
        db_sess.commit()
        image_num = db_sess.query(Image).filter(Image.post_id == post_id).count()
        for url in request.form.get('images_deleted').split():
            image_id = int(url.split("/")[-1].split('.')[0].split('-')[-1])
            db_sess.query(Image).filter(Image.post_id == post_id, Image.image_id == image_id).delete()
            os.remove(f'images/{url.split("/")[-1]}')
        for i, base64_image in enumerate(request.form.get('images').split()):
            image = Image()
            image.user_id = current_user.id
            image.post_id = post.id
            image.image_id = i + image_num

            db_sess.add(image)
            db_sess.commit()
            db_sess.flush()

            image_stream = BytesIO(base64.b64decode(base64_image[22:]))
            storage.upload(FileStorage(image_stream, filename=f'image-{post.id}-{image.image_id}.png'))

        db_sess.commit()
        return redirect('/')

    images = db_sess.query(Image).filter_by(post_id=post.id).all()
    urls = []
    for i, image in enumerate(images):
        image_file = storage.get(f'image-{post.id}-{image.image_id}.png')
        if image_file:
            urls.append([i, image_file.url])
    form.title.data = post.title
    form.description.data = post.description
    form.tags.data = post.tags
    return render_template('edit_post.html', form=form, post=post, images=urls)


@bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post(post_id):
    cur_post = db_sess.query(Post).filter(Post.id == post_id).first()

    replies_num = db_sess.query(Pair).filter(Pair.original == post_id).count()
    # replies_ids = [item.reply for item in replies]
    # replies = db_sess.query(Post).filter(Post.id in replies_ids)

    images = db_sess.query(Image).filter_by(post_id=post_id)
    comment_form = CommentForm()
    post_comments = db_sess.query(Comment).filter(Comment.post_id == cur_post.id).order_by(Comment.pub_date)
    authors = db_sess.query(User).all()
    authors_ids = {}
    for author in authors:
        authors_ids[author.id] = f'{author.name} {author.surname}'
    if comment_form.validate_on_submit():
        comment = Comment()
        comment.author = current_user.id
        comment.text = comment_form.text.data
        cur_post.comments.append(comment)
        db_sess.merge(cur_post)
        db_sess.commit()
        return redirect(f'/post/{post_id}')
    images = db_sess.query(Image).filter(Image.post_id == post_id).all()
    urls = []
    for i, image in enumerate(images):
        image_file = storage.get(f'image-{post_id}-{image.image_id}.png')
        if image_file:
            urls.append([i, image_file.url])
    return render_template('post.html', post=cur_post, images=urls, replies_num=replies_num,
                           comment_form=comment_form, comments=post_comments, authors=authors_ids)


@bp.route('/post_after_edited')
@async_action
async def post_after_edited():
    await asyncio.sleep(2)
    return redirect('/index')


@bp.route('/post_after_created')
def post_after_created():
    time.sleep(0.2)
    return redirect('/index')


@bp.route('/delete_post/<int:post_id>')
def delete_post(post_id):
    db_sess.query(Image).filter_by(post_id=post_id).delete()
    db_sess.query(Comment).filter(Comment.post_id == post_id).delete()
    db_sess.query(Post).filter(Post.id == post_id).delete()
    db_sess.query(Pair).filter((Pair.original == post_id) | (Pair.reply == post_id)).delete()
    db_sess.commit()
    return redirect('/index')


@bp.route('/delete_comment/<int:comment_id>')
def delete_comment(comment_id):
    post_id = db_sess.query(Comment).filter(Comment.id == comment_id).first().post_id
    db_sess.query(Comment).filter(Comment.id == comment_id).delete()
    db_sess.commit()
    return redirect(f'/post/{post_id}')


@bp.route('/edit_comment/<int:comment_id>', methods=["GET", "POST"])
def edit_comment(comment_id):
    form = EditCommentForm()
    comment = db_sess.query(Comment).filter(Comment.id == comment_id).first()
    # form.text.data = comment.text
    if form.validate_on_submit():
        cur_post = db_sess.query(Post).filter(Post.id == comment.post_id).first()
        post_id = cur_post.id
        comment.text = form.text.data
        cur_post.comments.append(comment)
        db_sess.merge(cur_post)
        db_sess.commit()
        return redirect(f'/post/{post_id}')
    return render_template('edit_comment.html', form=form, comment=comment)


@bp.route('/propose_barter/<int:post_id>', methods=['GET', 'POST'])
def propose_barter(post_id):
    form = PostForm()
    reply_to = db_sess.query(Post).filter(Post.id == post_id).first()
    images = db_sess.query(Image).filter(Image.post_id == post_id).all()
    urls = []
    for i, image in enumerate(images):
        image_file = storage.get(f'image-{post_id}-{image.image_id}.png')
        if image_file:
            urls.append([i, image_file.url])
    pair = Pair()
    if request.method == "POST":
        post = Post()
        post.title = request.form.get("title")
        post.description = request.form.get("description")
        post.tags = request.form.get("tags")
        post.creator = current_user.id
        current_user.posts.append(post)
        db_sess.merge(current_user)
        db_sess.commit()
        db_sess.flush()

        for i, base64_image in enumerate(request.form.get('images').split()):
            image = Image()
            image.user_id = current_user.id
            image.post_id = post.id
            image.image_id = i

            db_sess.add(image)
            db_sess.commit()
            db_sess.flush()

            image_stream = BytesIO(base64.b64decode(base64_image[22:]))
            storage.upload(FileStorage(image_stream, filename=f'image-{post.id}-{image.image_id}.png'))

        db_sess.commit()
        pair.original = reply_to.id
        pair.reply = post.id
        db_sess.merge(pair)
        db_sess.commit()
        return redirect('/')
    return render_template('propose_barter.html', title='Предложить обмен', form=form,
                           images=urls, reply_to=reply_to)


@bp.route('/post_after_proposed')
def post_after_proposed():
    time.sleep(0.2)
    return redirect('/index')


@bp.route('/post/<int:post_id>/replies')
def post_replies(post_id):
    cur_post = db_sess.query(Post).filter(Post.id == post_id).first()

    replies = db_sess.query(Pair).filter(Pair.original == post_id)
    replies_ids = [item.reply for item in replies]
    posts = []
    for id in replies_ids:
        q = db_sess.query(Post).filter(Post.id == id).order_by(desc(Post.start_date)).all()
        for p in q:
            posts.append(p)
    posts.sort(key=lambda x: x.start_date, reverse=True)
    data = []
    for item in posts:
        urls = []
        images = db_sess.query(Image).filter(Image.post_id == item.id).all()
        for i, image in enumerate(images):
            image_file = storage.get(f'image-{post_id}-{image.image_id}.png')
            if image_file:
                urls.append([i, image_file.url])
        data.append([item, urls])
    return render_template('post_replies.html', replies=data)


@bp.route('/profile/archive')
def archive():
    archived = db_sess.query(Post).filter(Post.archived, Post.creator == current_user.id).all()
    images = list(map(lambda x: x.image.split(), archived))
    data = []
    for i in range(len(images)):
        data.append([archived[i], images[i]])
    return render_template('archive.html', posts=data)
    images = cur_post.image.split()
    return render_template('post_replies.html', post=cur_post, images=images, replies_num=replies_num)


@bp.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        return render_template('search.html')

    if 'search_input' not in request.form:
        return redirect(url_for('.index'))

    keywords = request.form['search_input'].split()
    search_keywords_title = []
    search_keywords_description = []
    for keyword in keywords:
        search_keywords_title.append(Post.title.like('%' + keyword + '%'))
        search_keywords_description.append(Post.description.like('%' + keyword + '%'))

    posts = db_sess.query(Post).filter(
        or_(*search_keywords_title,
            *search_keywords_description)
    ).all()
    data = []
    for post in posts:
        images = db_sess.query(Image).filter_by(post_id=post.id).all()
        urls = []
        for image in images:
            image_obj = storage.get(f'image-{post.id}-{image.image_id}.png')
            if image_obj and isinstance(image_obj, Object):
                urls.append(image_obj.url)

        data.append([post, urls])
    return render_template('index.html', posts=data)


@bp.route('/api_info')
def api_info():
    return render_template('api_info.html')
