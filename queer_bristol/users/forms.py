from typing import Any, Mapping, Sequence
from flask_wtf import FlaskForm
from wtforms import BooleanField, EmailField, SelectMultipleField, StringField, SelectField
from wtforms.validators import DataRequired, InputRequired, Optional

class UserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    admin = BooleanField('Is Admin')
    helper = BooleanField('Is Helper')
    groups = SelectMultipleField('Groups')
    