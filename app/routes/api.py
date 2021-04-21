from flask.blueprints import Blueprint
from flask import jsonify
from app.models import Post, User, Comment, Image
from app import db_sess, storage
from sqlalchemy import or_

bp = Blueprint('api', __name__)


@bp.route('/api/post/<int:id>')
def api_post(id):
    post = db_sess.query(Post).filter(Post.id == id).first()
    return jsonify(
        {
            'post':
                post.to_dict(only=('title', 'description', 'tags', 'archived',
                                   'start_date', 'end_date', 'user.name', "user.surname"))
        }
    )


@bp.route('/api/comments/<int:post_id>')
def api_comments(post_id):
    comments = db_sess.query(Comment).filter(Post.id == post_id).all()
    return jsonify(
        {
            'comments':
                [item.to_dict(only=('user.name', 'user.surname', 'post_id', 'text', 'text',
                                    'pub_date')) for item in comments]
        }
    )


@bp.route('/api/search/<string:keywords>')
def api_search(keywords):
    keywords = keywords.split('_')
    search_keywords_title = []
    search_keywords_description = []
    for keyword in keywords:
        search_keywords_title.append(Post.title.like('%' + keyword + '%'))
        search_keywords_description.append(Post.description.like('%' + keyword + '%'))

    posts = db_sess.query(Post).filter(
        or_(*search_keywords_title,
            *search_keywords_description)
    ).all()
    return jsonify(
        {
            'posts':
                [item.to_dict(only=('title', 'description', 'tags', 'archived',
                                    'start_date', 'end_date', 'user.name', "user.surname")) for item in posts]
        }
    )
