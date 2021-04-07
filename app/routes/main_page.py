# from app import app
from flask import render_template, Blueprint, redirect
from flask_login import current_user, login_user

page = Blueprint('page', __name__)

from models import Post, PostForm, User, LoginForm
from app import db_session


@page.route('/')
@page.route('/index')
def index():
    return render_template('index.html')
    # return 'index'


@page.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@page.route('/register')
def sign_up():
    return 'register'


@page.route("/create_post", methods=['GET', 'POST'])
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        post = Post()
        post.title = form.title.data
        post.description = form.description.data
        post.tags = form.tags.data
        post.creator = current_user.id
        current_user.posts.append(post)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('add_post.html', title='Создание объявления',
                           form=form)