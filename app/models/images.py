import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from app import db_session


class Image(db_session.SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'image'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    image_id = sqlalchemy.Column('image_id', sqlalchemy.Integer)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    post_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('posts.id'))
    # image = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    start_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                   default=datetime.datetime.now)
    user = orm.relation('User')
    post = orm.relation('Post')

    def __repr__(self):
        return f'<Image> by {self.user.name} {self.user.surname}'

