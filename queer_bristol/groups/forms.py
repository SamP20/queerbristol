

from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, TextAreaField
from wtforms.validators import DataRequired


class GroupForm(FlaskForm):
    id = HiddenField('Group')
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    tags = StringField('Tags')