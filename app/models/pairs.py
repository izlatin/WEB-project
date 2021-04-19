import sqlalchemy


from app import db_session


class Pair(db_session.SqlAlchemyBase):
    __tablename__ = 'pairs'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    original = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('posts.id'))
    reply = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('posts.id'))

    def __repr__(self):
        return f'<Pair> {self.original} and {self.reply}'
