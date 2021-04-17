from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired


class CommentForm(FlaskForm):
    text = TextAreaField('Ваш комментарий:', validators=[DataRequired()])
    submit = SubmitField('Оставить комментарий')


class EditCommentForm(FlaskForm):
    text = TextAreaField('Ваш комментарий:', validators=[DataRequired()])
    submit = SubmitField('Сохранить комментарий')
