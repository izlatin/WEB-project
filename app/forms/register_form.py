from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length


class RegisterForm(FlaskForm):
    surname = StringField(
        'Surname',
        validators=[
            Length(
                max=35),
            DataRequired()])
    name = StringField('Name', validators=[Length(max=35), DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    email = StringField(
        'Email',
        validators=[
            Length(
                min=6,
                max=35),
            DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign up')


class EditProfileForm(FlaskForm):
    surname = StringField(
        'Surname',
        validators=[
            Length(
                max=35),
            DataRequired()])
    name = StringField('Name', validators=[Length(max=35), DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    submit = SubmitField('Save')
