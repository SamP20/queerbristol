from typing import Any, Mapping, Sequence
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, TimeField, SelectField
from wtforms.validators import DataRequired, InputRequired, Optional

class AnnouncementForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    body = TextAreaField('Content')
    schedule_date = DateField('Schedule date (optional)', validators=[Optional()])
    schedule_time = TimeField('Schedule time (optional)', validators=[Optional()])
    hide_after = DateField('Hide after date (optional)', validators=[Optional()])

    def validate(self, extra_validators: Mapping[str, Sequence[Any]] | None = None):
        if not super().validate(extra_validators):
            return False
        
        if self.schedule_date.data and not self.schedule_time.data:
            self.schedule_time.errors.append("Schedule time must be provided if date is provided.")
            return False
        return True