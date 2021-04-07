from flask.blueprints import Blueprint
from flask import url_for, flash, current_app
from flask.globals import request, session
from flask.templating import render_template
from flask_login import login_manager, login_user, current_user, logout_user, login_required
from werkzeug.exceptions import abort
from werkzeug.utils import redirect
from werkzeug.security import check_password_hash

from app.forms import login_form, register_form
from app.models import User
from app import db_sess

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('.account'))
    
    form = login_form.LoginForm()
    if not form.validate_on_submit():
        flash('The form is incorrect')
        return render_template('login.html', form=form)
    
    user = db_sess.query(User).filter_by(email=form.email.data).first()
    if user and user.check_password(form.password.data):
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        
        return redirect(next_page or url_for('main.index'))
    
    # say that validation failed
    flash("User doesn't exist")
    return render_template('login.html', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('.account'))
    
    form = register_form.RegisterForm()
    if not form.validate_on_submit():
        flash('The form is incorrect')
        return render_template('register.html', form=form)
    
    user = db_sess.query(User).filter_by(email=form.email.data).first()
    if user:
        flash('User with this email is alredy registered')
        return render_template('register.html', form=form)
    
    user = User(
        email=form.email.data,
        surname=form.surname.data,
        name=form.name.data,
        age=form.age.data,
        )
    
    user.set_password(form.password.data)
    try:
        db_sess.add(user)
    except Exception:
        session.rollback()
    else:
        db_sess.commit()
    
    return redirect(url_for('.login'))
    

@auth.route('/account', methods=['GET'])
@login_required
def account():
    return 'account'
