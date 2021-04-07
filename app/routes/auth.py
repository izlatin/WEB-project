from flask.blueprints import Blueprint
from flask import url_for, flash
from flask.globals import request
from flask.templating import render_template
from flask_login import login_manager, login_user, current_user, logout_user, login_required
from werkzeug.exceptions import abort
from werkzeug.utils import redirect
from werkzeug.security import check_password_hash

from forms import login_form, register_form
from models import User

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('.account'))
    
    form = login_form.LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            
            return redirect(next_page or url_for('main.index'))
        
    # say that validation failed
    flash('Wrong username or password')
    return render_template('login.html', form=form)

@auth.route('/register')
def register():
    if current_user.is_authenticated:
        return redirect(url_for('.account'))
    
    form = register_form.RegisterForm()
    if not form.validate_on_submit():
        flash('The form is incorrect')
        return render_template('register.html', form=form)
    
    

@auth.route('/account')
@login_required
def account():
    return 'account'