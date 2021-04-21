import datetime
import sqlalchemy
from sqlalchemy import orm
# from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin

from app import db_session


class Comment(db_session.SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'comments'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    author = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey('users.id'))
    post_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey('posts.id'))
    text = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    pub_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                 default=datetime.datetime.now)
    user = orm.relation('User')
    post = orm.relation('Post')

    def __repr__(self):
        return f'<Comment> {self.id}'
