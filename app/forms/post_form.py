from flask_wtf import FlaskForm
from sqlalchemy import orm
from wtforms import StringField, BooleanField, SubmitField, IntegerField, TextAreaField, MultipleFileField
from wtforms.validators import DataRequired


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    tags = StringField('Tags', validators=[DataRequired()])
    images = MultipleFileField('Upload images')
    submit = SubmitField('Add')
