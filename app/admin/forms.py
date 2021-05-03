from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
import datetime

def time_check(form, field):
    try:
        datetime.datetime.strptime(field.data, '%Y-%m-%d %H:%M')
    except:
        raise ValidationError('Please use the following format: YYYY-MM-DD HH:MM')

def number_check(form, field):
    try:
        float(field.data)
    except:
        raise ValidationError("Please enter a number.")

def special_check(form, field):
    if form.special_units.data != '':
        if int(form.special_units.data) > 0 and form.special_explanation.data == '':
            raise ValidationError("Please explain why this qualifies for special pay.")

class RegionForm(FlaskForm):
    name = StringField('Region Name', validators=[DataRequired(), Length(max=100)], render_kw={'style': 'width:50%;', 'placeholder': 'Region Name'})
    submit = SubmitField('Save Region >>', render_kw={'style': 'width:50%;', 'class': 'btn btn-primary'})

class EventForm(FlaskForm):
    region_id = SelectField('Region', coerce=int, render_kw={'style': 'width:50%;'})
    name = StringField('Event Name', validators=[DataRequired(), Length(max=100)], render_kw={'style': 'width:50%;', 'placeholder': 'Event Name'})
    shift_start = StringField('Event Start Time', validators=[DataRequired(), time_check], render_kw={'style': 'width:25%;', 'placeholder': 'Event Start Time (YYYY-MM-DD HH:MM)'})
    shift_end = StringField('Event End Time', validators=[DataRequired(), time_check], render_kw={'style': 'width:25%;', 'placeholder': 'Event End Time (YYYY-MM-DD HH:MM)'})
    street_address = StringField('Street Address', validators=[DataRequired(), Length(max=100)], render_kw={'style': 'width:50%;', 'placeholder': 'Street Address'})
    city = StringField('City', validators=[DataRequired(), Length(max=50)], render_kw={'style': 'width:50%;', 'placeholder': 'City'})
    state = StringField('State', validators=[DataRequired(), Length(min=2, max=2)], render_kw={'style': 'width:50%;', 'placeholder': 'State'})
    zip_code = StringField('ZIP Code', validators=[DataRequired(), Length(min=5, max=5)], render_kw={'style': 'width:50%;', 'placeholder': 'ZIP Code'})
    skilled_capacity = StringField('Skilled Worker Capacity', validators=[DataRequired(), number_check], render_kw={'style': 'width:25%;', 'placeholder': 'Skilled Worker Capacity'})
    unskilled_capacity = StringField('Unskilled Worker Capacity', validators=[DataRequired(), number_check], render_kw={'style': 'width:25%;', 'placeholder': 'Unskilled Worker Capacity'})
    advance_url = StringField('Advance URL', validators=[DataRequired(), Length(max=300)], render_kw={'style': 'width:50%;', 'placeholder': 'Advance URL'})
    need_drug = BooleanField('Drug Screen Required?')
    need_background = BooleanField('Background Check Required?')
    skilled_base = StringField('Skilled Worker Base Pay', validators=[DataRequired(), number_check], render_kw={'style': 'width:25%;', 'placeholder': 'Skilled Worker Base Pay'})
    unskilled_base = StringField('Unskilled Worker Base Pay', validators=[DataRequired(), number_check], render_kw={'style': 'width:25%;', 'placeholder': 'Unskilled Worker Base Pay'})
    special_base = StringField('Special Worker Base Pay', validators=[DataRequired(), number_check], render_kw={'style': 'width:25%;', 'placeholder': 'Special Worker Base Pay'})
    special_rate = StringField('Special Worker Per-Unit Rate', validators=[DataRequired(), number_check], render_kw={'style': 'width:25%;', 'placeholder': 'Special Worker Per-Unit Rate'})
    submit = SubmitField('Save Event >>', render_kw={'style': 'width:50%;', 'class': 'btn btn-primary'})

class ShiftForm(FlaskForm):
    user_id = SelectField('User', coerce=int, validators=[DataRequired()], render_kw={'style': 'width:50%;'})
    event_id = SelectField('Event', coerce=int, validators=[DataRequired()], render_kw={'style': 'width:50%;'})
    special_units = StringField('Special Units', validators=[number_check], render_kw={'style': 'width:25%;', 'placeholder': 'Special Units'})
    special_explanation = TextAreaField('Special Pay Explanation', validators=[special_check], render_kw={'style': 'width:50%;', 'placeholder': 'Explain why this user is applying for special payment.'})
    shift_start = StringField('Work Day Clock-In Time', validators=[Length(max=5)], render_kw={'style': 'width:25%;', 'placeholder': 'Work Day Clock-In Time'})
    lunch_start = StringField('Lunch Break Start Time', validators=[Length(max=5)], render_kw={'style': 'width:25%;', 'placeholder': 'Lunch Break Start Time'})
    lunch_end = StringField('Lunch Break End Time', validators=[Length(max=5)], render_kw={'style': 'width:25%;', 'placeholder': 'Lunch Break End Time'})
    shift_end = StringField('Work Day Clock-Out Time', validators=[Length(max=5)], render_kw={'style': 'width:25%;', 'placeholder': 'Work Day Clock-Out Time'})
    is_cancel = BooleanField('Cancel?')
    is_waitlist = BooleanField('Waitlist?')
    is_noshow = BooleanField('No Show?')
    submit = SubmitField('Save Shift >>', render_kw={'style': 'width:50%;', 'class': 'btn btn-primary'})

class UserForm(FlaskForm):
    region_id = SelectField('Region', coerce=int, validators=[DataRequired()], render_kw={'style': 'width:50%;'})
    stripe_customer_id = StringField('Stripe ID', render_kw={'style': 'width:50%;', 'placeholder': 'Stripe Customer ID'})
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={'style': 'width:50%;', 'placeholder': 'Email'})
    password = PasswordField('Set Password', render_kw={'style': 'width:50%;', 'placeholder': 'Set Password'})
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)], render_kw={'style': 'width:50%;', 'placeholder': 'First Name'})
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)], render_kw={'style': 'width:50%;', 'placeholder': 'Last Name'})
    user_type = SelectField('User Type', choices=[('1', 'Website Administrator'), ('2', 'Skilled Worker'), ('3', 'Unskilled Worker'), ('4', 'Other')], validators=[DataRequired()], render_kw={'style': 'width:50%;'})
    comments = TextAreaField('Comments (300 characters max)', validators=[Length(max=300)], render_kw={'style': 'width:50%;', 'placeholder': 'Comments (300 characters max)'})
    is_blacklist = BooleanField('Blacklist?')
    is_drug = BooleanField('Passed Drug Screen?')
    is_background = BooleanField('Passed Background Check?')
    submit = SubmitField('Save User >>', render_kw={'style': 'width:50%;', 'class': 'btn btn-primary'})