from flask_wtf import FlaskForm
from sqlalchemy import orm
from wtforms import StringField, BooleanField, SubmitField, IntegerField, TextAreaField
from wtforms.validators import DataRequired


class PostForm(FlaskForm):
    title = StringField('Заголовок')
    description = TextAreaField('Описание товара', validators=[DataRequired()])

    tags = StringField('Теги')
    submit = SubmitField('Добавить')
