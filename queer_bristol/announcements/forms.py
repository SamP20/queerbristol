from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, TimeField, SelectField
from wtforms.validators import DataRequired, InputRequired, Optional

class AnnouncementForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    body = TextAreaField('Content')
    hide_after_date = DateField('Hide after date', validators=[Optional()])
    group = SelectField('Group', coerce=int)