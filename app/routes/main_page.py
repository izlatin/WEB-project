from flask import render_template, Blueprint, redirect, flash, session, request, url_for
from flask_login import current_user

from app import db_session, photos, db_sess
from app.models import Post
from app.forms import PostForm

main = Blueprint('main', __name__)
post_form = None
post_id = 0

@main.route('/')
@main.route('/index')
def index():
    return render_template('index.html')


@main.route('/add_images', methods=['GET', 'POST'])
def results():
    global post_form, post_id
    post = db_sess.query(Post).filter(Post.id == post_id).first()
    files = [f'/static/images/{post_id}/{i}' for i in post.images.split()]

    if "file_urls" not in session:
        session['file_urls'] = []
        # list to hold our uploaded image urls
    file_urls = session['file_urls']
    if 'submit' in request.form:
        return 'loch'
    elif request.method == 'POST':
        post = db_sess.query(Post).filter(Post.id == post_id).first()
        file_obj = request.files
        for f in file_obj:
            file = request.files.get(f)
            post.images += f' {file.filename}'
            db_sess.merge(current_user)
            db_sess.commit()
            # save the file with to our photos folder
            filename = photos.save(
                file,
                name=file.filename,
                folder=str(post_id)
            )

            # append image urls
            file_urls.append(photos.url(filename))

        session['file_urls'] = file_urls
        return "uploading..."

    return render_template('results.html', file_urls=files, form=post_form)


@main.route("/create_post", methods=['GET', 'POST'])
def create_post():
    global post_form, post_id
    post_form = PostForm()

    if not current_user.is_authenticated:
        return redirect('/login')
    if post_form.validate_on_submit():
        db_sess = db_session.create_session()
        post = Post()
        post.title = post_form.title.data
        post.description = post_form.description.data
        post.images = ''
        post.tags = post_form.tags.data
        post.creator = current_user.id
        current_user.posts.append(post)
        db_sess.merge(current_user)
        db_sess.commit()
        post_id = db_sess.query(Post).all()[-1].id
        return redirect(f'/add_images')
    return render_template('add_post.html', title='Создание объявления',
                           form=post_form)
