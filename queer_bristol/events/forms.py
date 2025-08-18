from typing import Self
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, TimeField, SelectField, ValidationError
from wtforms.validators import DataRequired, InputRequired, Optional

class EventForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    accessibility = TextAreaField('Accessibility')
    start_date = DateField('Start date', validators=[InputRequired()])
    start_time = TimeField('Start time', validators=[InputRequired()])
    end_date = DateField('End date', validators=[Optional()])
    end_time = TimeField('End time', validators=[Optional()])
    venue = StringField('Venue', validators=[DataRequired()])

    def validate_end_date(form: Self, field: DateField):
        if field.data < form.start_date.data:
            raise ValidationError("End date must be after start date.")
        
    def validate_end_time(form: Self, field: TimeField):
        end_date = form.end_date.data or form.start_date.data

        if end_date != form.start_date.data:
            # Different days so end time will always be after start time
            return
        
        if form.end_time.data < form.start_time.data:
            if form.end_date.data:
                raise ValidationError("End time must be after start time.")
            else:
                raise ValidationError("End time must be after start time. You will need to provide an end date if it is an overnight event.")