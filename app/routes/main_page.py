import time

from flask import render_template, Blueprint, redirect, flash, request, url_for
from flask_login import current_user, login_user
import datetime
import base64


from flask_login.utils import login_required
from sqlalchemy import desc

from app import db_sess
from app.models import Post, User, Comment, Pair
from app.forms import PostForm, CommentForm, EditCommentForm

bp = Blueprint('main', __name__)


@bp.route('/')
@bp.route('/index')
def index():
    posts = db_sess.query(Post).filter(Post.archived == False).order_by(desc(Post.start_date)).all()
    images = list(map(lambda x: x.image.split(), posts))
    data = []
    for i in range(len(images)):
        data.append([posts[i], images[i]])
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
        post.image = request.form.get("images")
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
    if request.method == "POST":
        post.title = request.form.get("title")
        post.description = request.form.get("description")
        post.tags = request.form.get("tags")
        post.creator = current_user.id
        # TODO for mls_dmitry - solve images saving
        post.image = request.form.get("images")
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

    replies_num = db_sess.query(Pair).filter(Pair.original == post_id).count()
    # replies_ids = [item.reply for item in replies]
    # replies = db_sess.query(Post).filter(Post.id in replies_ids)

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
    return render_template('post.html', post=cur_post, images=images, replies_num=replies_num,
                           comment_form=comment_form, comments=post_comments, authors=authors_ids)


@bp.route('/post_after_edited')
def post_after_edited():
    return redirect('/index')


@bp.route('/post_after_created')
def post_after_created():
    time.sleep(0.2)
    return redirect('/index')


@bp.route('/delete_post/<int:post_id>')
def delete_post(post_id):
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
        print(comment.text)
        cur_post.comments.append(comment)
        db_sess.merge(cur_post)
        db_sess.commit()
        return redirect(f'/post/{post_id}')
    return render_template('edit_comment.html', form=form, comment=comment)


@bp.route('/propose_barter/<int:post_id>', methods=['GET', 'POST'])
def propose_barter(post_id):
    form = PostForm()
    reply_to = db_sess.query(Post).filter(Post.id == post_id).first()
    images = reply_to.image.split()
    pair = Pair()
    if request.method == "POST":
        post = Post()
        post.title = request.form.get("title")
        post.description = request.form.get("description")
        post.tags = request.form.get("tags")
        post.creator = current_user.id
        post.image = request.form.get("images")
        current_user.posts.append(post)
        db_sess.merge(current_user)
        db_sess.commit()
        db_sess.flush()
        pair.original = reply_to.id
        pair.reply = post.id
        db_sess.merge(pair)
        db_sess.commit()
        return redirect('/')
    return render_template('propose_barter.html', title='Предложить обмен', form=form,
                           images=images, reply_to=reply_to)


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
    images = list(map(lambda x: x.image.split(), posts))
    data = []
    for i in range(len(images)):
        data.append([posts[i], images[i]])
    return render_template('post_replies.html', replies=data)


@bp.route('/profile/archive')
def archive():
    archived = db_sess.query(Post).filter(Post.archived, Post.creator == current_user.id).all()
    images = list(map(lambda x: x.image.split(), archived))
    data = []
    for i in range(len(images)):
        data.append([archived[i], images[i]])
    return render_template('archive.html', posts=data)