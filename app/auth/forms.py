from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app.models import User
import datetime

def email_check(form, field):
    email = User.query.filter_by(email=str(form.email.data)).first()
    if email:
        raise ValidationError("That email address is already in use. Please choose another.")

def password_check(form, field):
    if form.password.data != form.verify_password.data:
        raise ValidationError('Passwords must match.')

class RegisterForm(FlaskForm):
    region_id = SelectField('Region', coerce=int, validators=[DataRequired()], render_kw={'style': 'width:50%;'})
    user_type = SelectField('User Type', choices=[('2', 'Skilled Worker'), ('3', 'Unskilled Worker'), ('4', 'Other')], validators=[DataRequired()], render_kw={'style': 'width:50%;'})
    stripe_customer_id = StringField('Stripe Customer ID', validators=[Length(max=300)], render_kw={'style': 'width:50%;', 'placeholder': 'Stripe Customer ID'})
    email = StringField('Email', validators=[DataRequired(), Email(), email_check], render_kw={'style': 'width:50%;', 'placeholder': 'Email address'})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={'style': 'width:50%;', 'placeholder': 'Password'})
    verify_password = PasswordField('Verify Password', validators=[DataRequired(), password_check], render_kw={'style': 'width:50%;', 'placeholder': 'Verify Password'})
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)], render_kw={'style': 'width:50%;', 'placeholder': 'First Name'})
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)], render_kw={'style': 'width:50%;', 'placeholder': 'Last Name'})
    comments = TextAreaField('Say Something About Yourself (Optional)', validators=[Length(max=300)], render_kw={'style': 'width:50%;', 'placeholder': 'Anything you would like the staffing coordinators to know?'})
    submit = SubmitField('Register >>', render_kw={'style': 'width:50%;', 'class': 'btn btn-primary'})

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()], render_kw={'style': 'width:50%;', 'placeholder': 'Email'})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={'style': 'width:50%;', 'placeholder': 'Password'})
    submit = SubmitField('Log In >>', render_kw={'style': 'width:50%;', 'class': 'btn btn-primary'})