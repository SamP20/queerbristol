from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import HiddenField, StringField, TextAreaField
from wtforms.validators import DataRequired, Regexp


class ImageUploadForm(FlaskForm):
    image = FileField('Image File', validators=[FileRequired()])
    name = StringField('Name', validators=[DataRequired()])
    alt_text = TextAreaField('Alt text (for screen readers)')