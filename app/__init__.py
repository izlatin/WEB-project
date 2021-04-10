from flask_login import current_user, LoginManager, login_user
from flask_oauthlib.provider import OAuth2Provider
from authlib.integrations.sqla_oauth2 import (
    create_query_client_func,
    create_save_token_func,
    create_revocation_endpoint,
    create_bearer_token_validator,
)
from authlib.oauth2.rfc6749 import grants
from authlib.oauth2.rfc7636 import CodeChallenge
from sqlalchemy.sql.functions import user
from flask_dropzone import Dropzone
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
import os

from . import db_session

db_session.global_init('barter.db')
db_session.global_init("barter.db")
photos = None

login_manager = LoginManager()

db_sess = db_session.create_session()


@login_manager.user_loader
def load_user(userid):
    return db_sess.query(User).get(userid)

def config_oauth(app):
    authorization.init_app(app)

    # support all grants
    authorization.register_grant(grants.ImplicitGrant)
    authorization.register_grant(grants.ClientCredentialsGrant)
    authorization.register_grant(AuthorizationCodeGrant, [CodeChallenge(required=True)])
    authorization.register_grant(PasswordGrant)
    authorization.register_grant(RefreshTokenGrant)

    # support revocation
    revocation_cls = create_revocation_endpoint(db_sess, OAuth2Token)
    authorization.register_endpoint(revocation_cls)

    # protect resource
    bearer_cls = create_bearer_token_validator(db_sess, OAuth2Token)
    require_oauth.register_token_validator(bearer_cls())

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config['SECRET_KEY'] = 'b@rter_2hop_secre3_key'
    app.config['TESTING'] = False

    from .routes import auth, main_page, oauth2
    app.register_blueprint(main_page.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(oauth2.bp)
    
    # init auth and oauth
    login_manager.init_app(app)
    config_oauth(app)
    # register login views
    login_manager.blueprint_login_views = {
        'main': '/',
    }
    login_manager.unauthorized_handler(lambda: redirect(url_for('auth.login')))
    
    return app
