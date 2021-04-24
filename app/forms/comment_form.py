from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired


class CommentForm(FlaskForm):
    text = TextAreaField('Your comment:', validators=[DataRequired()])
    submit = SubmitField('Leave a comment')


class EditCommentForm(FlaskForm):
    text = TextAreaField('Your comment:', validators=[DataRequired()])
    submit = SubmitField('Save comment')
