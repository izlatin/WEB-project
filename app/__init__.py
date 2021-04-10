import os
# TODO ONLY for DEBUG to allow http requests instead of https
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

from flask import Flask, render_template, redirect, url_for
from flask_login import current_user, LoginManager, login_user

from authlib.integrations.flask_oauth2 import (
    AuthorizationServer,
    ResourceProtector,
)
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

from . import db_session

db_session.global_init('barter.db')

login_manager = LoginManager()

db_sess = db_session.create_session()

from app.models import User
from app.models import OAuth2Client, OAuth2Token, OAuth2AuthorizationCode


class AuthorizationCodeGrant(grants.AuthorizationCodeGrant):
    TOKEN_ENDPOINT_AUTH_METHODS = [
        'client_secret_basic',
        'client_secret_post',
        'none',
    ]

    def save_authorization_code(self, code, request):
        code_challenge = request.data.get('code_challenge')
        code_challenge_method = request.data.get('code_challenge_method')
        auth_code = OAuth2AuthorizationCode(
            code=code,
            client_id=request.client.client_id,
            redirect_uri=request.redirect_uri,
            scope=request.scope,
            user_id=request.user.id,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
        )
        db_sess.session.add(auth_code)
        db_sess.session.commit()
        return auth_code

    def query_authorization_code(self, code, client):
        auth_code = db_sess.query(OAuth2AuthorizationCode).filter_by(
            code=code, client_id=client.client_id).first()
        if auth_code and not auth_code.is_expired():
            return auth_code

    def delete_authorization_code(self, authorization_code):
        db_sess.session.delete(authorization_code)
        db_sess.session.commit()

    def authenticate_user(self, authorization_code):
        return db_sess.query(User).get(authorization_code.user_id)


class PasswordGrant(grants.ResourceOwnerPasswordCredentialsGrant):
    def authenticate_user(self, username, password):
        user = db_sess.query(User).filter_by(email=username).first()
        if user is not None and user.check_password(password):
            return user


class RefreshTokenGrant(grants.RefreshTokenGrant):
    def authenticate_refresh_token(self, refresh_token):
        token = db_sess.query(OAuth2Token).filter_by(refresh_token=refresh_token).first()
        if token and token.is_refresh_token_active():
            return token

    def authenticate_user(self, credential):
        return db_sess.query(User).get(credential.user_id)

    def revoke_old_credential(self, credential):
        credential.revoked = True
        db_sess.session.add(credential)
        db_sess.session.commit()
        
query_client = create_query_client_func(db_sess, OAuth2Client)
save_token = create_save_token_func(db_sess, OAuth2Token)
authorization = AuthorizationServer(
    query_client=query_client,
    save_token=save_token,
)
require_oauth = ResourceProtector()

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
