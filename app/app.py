from flask import Flask, render_template, redirect
from flask_login import current_user, LoginManager
from flask_oauthlib.provider import OAuth2Provider

from models import User
import db_session
from routes import auth, main_page

app = Flask(__name__, template_folder='templates', static_folder='static')

app.register_blueprint(main_page.main_page)
app.config['SECRET_KEY'] = 'barter_shop_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
oauth = OAuth2Provider(app)

login_manager.blueprint_login_views = {
    'page': '/',
    'main_page': '/',
}

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


def main():
    
    db_session.global_init("barter.db")
    # db_sess = db_session.create_session()
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)


if __name__ == '__main__':
    main()

