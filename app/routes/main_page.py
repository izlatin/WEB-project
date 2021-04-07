# from app import app
from flask import render_template, Blueprint, redirect
from flask_login import current_user
from app.models.posts import PostForm, Post
from app import db_session


main_page = Blueprint('main_main', __name__)


@main_page.route('/')
@main_page.route('/index')
def index():
    return render_template('index.html')
    # return 'index'


@main_page.route('/login')
def login():
    return 'login'


@main_page.route('/register')
def sign_up():
    return 'register'


@main_page.route("/create_post", methods=['GET', 'POST'])
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        post = Post()
        post.title = form.title.data
        post.description = form.description.data
        post.tags = form.tags.data
        post.creator = current_user.id
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('add_post.html', title='Создание объявления',
                           form=form)