import datetime
import sqlalchemy
from flask_login import current_user
from flask_wtf import FlaskForm
from sqlalchemy import orm
from wtforms import StringField, BooleanField, SubmitField, IntegerField, TextAreaField
from wtforms.validators import DataRequired

from app import db_session


class Post(db_session.SqlAlchemyBase):
    __tablename__ = 'posts'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    images = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    creator = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('User.id'))
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    tags = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    start_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                   default=datetime.datetime.now)
    end_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                 default=datetime.datetime.now)
    user = orm.relation("User")

    def __repr__(self):
        return f'<Post> {self.title}'

#
#
# class JobsEditForm(FlaskForm):
#     job = StringField('Работа', validators=[DataRequired()])
#     team_leader = IntegerField('id тимлидера')
#     work_size = IntegerField('Длительность работы')
#     collaborators = StringField('Сотрудники')
#     is_finished = BooleanField("Завершено")
#     submit = SubmitField('Сохранить')
