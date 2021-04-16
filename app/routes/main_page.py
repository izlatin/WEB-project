from flask import render_template, Blueprint, redirect, flash, request
from flask_login import current_user, login_user
import datetime
import base64


from flask_login.utils import login_required
from sqlalchemy import desc

from app import db_sess
from app.models import Post, User, Comment
from app.forms import PostForm, CommentForm

bp = Blueprint('main', __name__)


@bp.route('/')
@bp.route('/index')
def index():
    posts = db_sess.query(Post).order_by(desc(Post.start_date)).all()
    images = list(map(lambda x: x.image.split(), posts))
    data = []
    for i in range(len(images)):
        data.append([posts[i], images[i]])
    return render_template('index.html', posts=data)


@bp.route("/create_post", methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        # db_sess = db_session.create_session()
        post = Post()
        post.title = form.title.data
        post.description = form.description.data
        post.tags = form.tags.data
        post.creator = current_user.id
        post.image = ''
        for image in form.images.data:
            print(image)
            post.image += base64.b64encode(image.read()).decode('ascii') + ' '
        current_user.posts.append(post)
        db_sess.merge(current_user)
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
    try:
        link = request.form.get('images')
        print(len(link.split()))
        if link:
            post.image = link
            post.description = request.form.get('desc')
            current_user.posts.append(post)
            db_sess.merge(current_user)
            db_sess.commit()
            print('yeah')
            return redirect('/')
    except Exception:
        pass
    if form.validate_on_submit():
        print('ha')
        post.title = form.title.data
        post.description = form.description.data
        post.tags = form.tags.data
        for image in form.images.data:
            print(image)
            post.image += base64.b64encode(image.read()).decode('ascii') + ' '
        current_user.posts.append(post)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    images = [[i, post.image.split()[i - 1]] for i in range(1, len(post.image.split()) + 1)]
    form.title.data = post.title
    form.description.data = post.description
    form.tags.data = post.tags
    return render_template('edit_post.html', form=form, post=post, images=images)


@bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post(post_id):
    cur_post = db_sess.query(Post).filter(Post.id == post_id).first()
    images = cur_post.image.split()
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
    return render_template('post.html', post=cur_post, images=images,
                           comment_form=comment_form, comments=post_comments, authors=authors_ids)