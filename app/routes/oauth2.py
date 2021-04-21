import time

from flask import redirect, request, redirect, url_for, render_template, jsonify
from flask.blueprints import Blueprint
from flask_login.utils import login_required, current_user, logout_user
from werkzeug.security import gen_salt
from authlib.integrations.flask_oauth2 import current_token
from authlib.oauth2 import OAuth2Error

from app.models import User
from app.models import OAuth2Client
from app import authorization, require_oauth

from app import db_sess

bp = Blueprint('oauth2', __name__, url_prefix='/oauth')


def split_by_crlf(s):
    return [v for v in s.splitlines() if v]


@bp.route('/logout')
def logout():
    logout_user()
    return redirect('/')


@bp.route('/create_client', methods=['GET', 'POST'])
@login_required
def create_client():
    if request.method == 'GET':
        return render_template('create_client.html')

    client_id = gen_salt(24)
    client_id_issued_at = int(time.time())
    client = OAuth2Client(
        client_id=client_id,
        client_id_issued_at=client_id_issued_at,
        user_id=current_user.id,
    )

    form = request.form
    client_metadata = {
        "client_name": form["client_name"],
        "client_uri": form["client_uri"],
        "grant_types": split_by_crlf(form["grant_type"]),
        "redirect_uris": split_by_crlf(form["redirect_uri"]),
        "response_types": split_by_crlf(form["response_type"]),
        "scope": form["scope"],
        "token_endpoint_auth_method": form["token_endpoint_auth_method"]
    }
    client.set_client_metadata(client_metadata)

    if form['token_endpoint_auth_method'] == 'none':
        client.client_secret = ''
    else:
        client.client_secret = gen_salt(48)

    db_sess.add(client)
    db_sess.commit()
    return redirect('/')


@bp.route('/authorize', methods=['GET', 'POST'])
def authorize():
    if request.method == 'GET':
        try:
            grant = authorization.validate_consent_request(
                end_user=current_user)
        except OAuth2Error as error:
            return error.error
        return render_template(
            'authorize.html', user=current_user, grant=grant)
    if not current_user and 'email' in request.form:
        email = request.form.get('email')
        user = db_sess.query(User).filter_by(email=email).first()
    if request.form['confirm']:
        grant_user = user
    else:
        grant_user = None
    return authorization.create_authorization_response(grant_user=grant_user)


@bp.route('/token', methods=['POST'])
def issue_token():
    return authorization.create_token_response()


@bp.route('/revoke', methods=['POST'])
def revoke_token():
    return authorization.create_endpoint_response('revocation')


@bp.route('/me')
@require_oauth('profile')
def api_me():
    user = current_token.user
    return jsonify(id=user.id, email=user.email)
