from flask import Flask, render_template, redirect
from flask_login import current_user, LoginManager, login_user
from flask_oauthlib.provider import OAuth2Provider

from . import db_session
from .models.user import User

db_session.global_init("barter.db")

login_manager = LoginManager()
oauth = OAuth2Provider()

db_sess = db_session.create_session()
@login_manager.user_loader
def load_user(user_id):
    return db_sess.query(models.User).get(user_id)


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config['SECRET_KEY'] = 'b@rter_2hop_secre3_key'    
    app.config['TESTING'] = False
    
    from .routes import auth, main_page    
    app.register_blueprint(main_page.main)
    app.register_blueprint(auth.auth)
    
    # init auth and oauth
    login_manager.init_app(app)
    oauth.init_app(app)
    
    # register login views
    login_manager.blueprint_login_views = {
        'main': '/',
    }
    return app

    



