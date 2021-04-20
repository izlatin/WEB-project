import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, PasswordField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy.orm import relation
from werkzeug.security import generate_password_hash, check_password_hash

from app.db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    age = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, nullable=True, unique=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                      default=datetime.datetime.now)

    posts = relation('Post', back_populates='user')
    images = relation('Image', back_populates='user')
    
    oauth2_client = relation('OAuth2Client', back_populates='user', uselist=False)
    oauth2_code = relation('OAuth2AuthorizationCode', back_populates='user', uselist=False)
    oauth2_token = relation('OAuth2Token', back_populates='user', uselist=False)
    

    def __repr__(self):
        return f'<User> {self.id} {self.name} {self.surname}'

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def get_user_id(self):
        return self.get_id()
