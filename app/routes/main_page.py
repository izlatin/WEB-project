from flask import render_template, Blueprint, redirect, flash
from flask_login import current_user, login_user
import datetime
import base64


from flask_login.utils import login_required

from app import db_sess
from app.models import Post, User
from app.forms import PostForm, EditProfileForm, ChangePasswordForm

bp = Blueprint('main', __name__)


@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html', posts=db_sess.query(Post).all())


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
        post.image = base64.b64encode(form.images.data[0].read()).decode('ascii')
        current_user.posts.append(post)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('add_post.html', title='Создание объявления',
                           form=form)
