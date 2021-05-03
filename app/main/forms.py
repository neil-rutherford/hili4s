from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app.models import User
import datetime

def special_check(form, field):
    if form.special_units.data != '' and form.special_explanation.data == '':
        raise ValidationError("Please explain why you are applying for special pay.")

def number_check(form, field):
    try:
        float(field.data)
    except:
        raise ValidationError("Please enter a number.")

class ShiftForm(FlaskForm):
    shift_start = StringField('Work Day Clock-In Time', validators=[Length(max=5)], render_kw={'style': 'width:25%;', 'placeholder': 'Work Day Clock-In Time'})
    lunch_start = StringField('Lunch Break Start Time', validators=[Length(max=5)], render_kw={'style': 'width:25%;', 'placeholder': 'Lunch Break Start Time'})
    lunch_end = StringField('Lunch Break End Time', validators=[Length(max=5)], render_kw={'style': 'width:25%;', 'placeholder': 'Lunch Break End Time'})
    shift_end = StringField('Work Day Clock-Out Time', validators=[Length(max=5)], render_kw={'style': 'width:25%;', 'placeholder': 'Work Day Clock-Out Time'})
    special_units = StringField('Special Units', validators=[number_check], render_kw={'style': 'width:25%;', 'placeholder': 'Special Units'})
    special_explanation = TextAreaField('Explain why you are applying for special pay.', validators=[special_check], render_kw={'style': 'width:50%;', 'placeholder': 'Explain why you are applying for special pay.'})
    submit = SubmitField('Save Shift >>', render_kw={'style': 'width:50%;', 'class': 'btn btn-primary'})