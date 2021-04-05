from flask import Flask, render_template, redirect
from flask_login import current_user, LoginManager
from data import db_session
from data.users import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'barter_shop_secret_key'

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


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)

if __name__ == '__main__':
    main()
