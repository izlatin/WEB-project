from flask.blueprints import Blueprint
from flask import url_for, flash, current_app
from flask.globals import request, session
from flask.templating import render_template
from flask_login import login_manager, login_user, current_user, logout_user, login_required
from werkzeug.exceptions import abort
from werkzeug.utils import redirect
from werkzeug.security import check_password_hash
import datetime

from app.forms import login_form, register_form
from app.models import Post, User
from app.forms import PostForm, EditProfileForm, ChangePasswordForm
from app import db_sess

bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = login_form.LoginForm()
    if not form.validate_on_submit():
        return render_template('login.html', form=form)

    user = db_sess.query(User).filter_by(email=form.email.data).first()
    if user and user.check_password(form.password.data):
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')

        return redirect(next_page or url_for('main.index'))

    # say that validation failed
    if user:
        flash("Wrong password")
    else:
        flash("User doesn't exist")
    return render_template('login.html', form=form)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect('/')

    form = register_form.RegisterForm()
    if not form.validate_on_submit():
        # flash('The form is incorrect')
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

    login_user(user, remember=form.remember_me.data)
    return redirect('/')


@bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/profile')
def profile():
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    posts = db_sess.query(Post).filter(Post.creator == current_user.id).count()
    return render_template("profile.html", user=user, posts_num=posts)


@bp.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    form = EditProfileForm()
    if form.validate_on_submit():
        user.name = form.name.data
        user.surname = form.surname.data
        user.age = form.age.data
        user.modified_date = datetime.datetime.now()
        db_sess.merge(user)
        db_sess.commit()
        return redirect('/profile')
    return render_template("edit_profile.html", user=user, form=form)


@bp.route('/profile/change_password', methods=['GET', 'POST'])
def change_password():
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    form = ChangePasswordForm()
    if not form.validate_on_submit():
        return render_template('change_password.html', form=form, user=user)

    checked = user.check_password(form.old_password.data)
    if checked and form.new_password.data == form.repeat_password.data:
        user.set_password(form.new_password.data)
        db_sess.merge(user)
        db_sess.commit()
        return redirect('/profile')
    elif not checked:
        flash('Incorrect old password')
        return render_template('change_password.html', form=form, user=user)
    else:
        flash('Passwords do not match')
        return render_template('change_password.html', form=form, user=user)
