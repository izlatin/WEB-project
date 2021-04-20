import datetime
import sqlalchemy
from sqlalchemy import orm


from app import db_session


class Post(db_session.SqlAlchemyBase):
    __tablename__ = 'posts'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    # image = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    creator = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    tags = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    start_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                   default=datetime.datetime.now)
    end_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                 default=datetime.datetime.now)
    user = orm.relation('User')
    images = orm.relation('Image', back_populates='post')
    comments = orm.relation('Comment', back_populates='post')

    def __repr__(self):
        return f'<Post> {self.title}'

