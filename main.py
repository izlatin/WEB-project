from flask import Flask, render_template, redirect
from flask_login import current_user, LoginManager
from data import db_session
from data.users import User
from data.posts import Post, PostForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'barter_shop_secret_key'
app.config['UPLOAD_FOLDER'] = r'/static/images'

login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init("db/barter.db")
    # db_sess = db_session.create_session()

    app.run()


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    return 'login'


@app.route('/register')
def sign_up():
    return 'register'


@app.route("/create_post", methods=['GET', 'POST'])
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


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


if __name__ == '__main__':
    main()
