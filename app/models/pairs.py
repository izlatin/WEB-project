import sqlalchemy
from sqlalchemy_serializer import SerializerMixin

from app import db_session


class Pair(db_session.SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'pairs'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    original = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('posts.id'))
    reply = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('posts.id'))

    def __repr__(self):
        return f'<Pair> {self.original} and {self.reply}'
