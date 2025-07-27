from flask_wtf import FlaskForm
from wtforms import EmailField, StringField, TextAreaField, DateField, TimeField, SelectField
from wtforms.validators import DataRequired, InputRequired, Optional

class MyForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])

class NewEventForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    start_date = DateField('Start date', validators=[InputRequired()])
    start_time = TimeField('Start time', validators=[InputRequired()])
    end_date = DateField('End date', validators=[Optional()])
    end_time = TimeField('End time', validators=[Optional()])
    venue = StringField('Venue', validators=[DataRequired()])
    group = SelectField('Group', coerce=int)


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])