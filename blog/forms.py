
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SubmitField, EmailField, SelectField
from wtforms.validators import DataRequired, ValidationError, Regexp, EqualTo, InputRequired, Email, Length
import email_validator
from blog.models import User


class RegistrationForm(FlaskForm):
    firstname = StringField('Firstname', render_kw={"placeholder": "firstname"}, validators=[DataRequired(), Regexp('^[0-9a-zA-Z]{2,20}$',
                                                                                                                  message='Your firstname should be between 2 and 20 characters long, and can only contain letters and numbers.')])
    email = StringField('Email', render_kw={"placeholder": "email"}, validators=[DataRequired(), Email(message='Invalid email. Please Check.')])
    password = PasswordField('Password', render_kw={"placeholder": "password"}, validators=[DataRequired(), Regexp('^[0-9a-zA-Z]{6,20}$',  message='Your password contains invalid characters.'),
                            EqualTo('confirm_password', message='Passwords do not match. Please try again.')])
    confirm_password = PasswordField('Confirm Password', render_kw={"placeholder": "confirm password"}, validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email is not None:
            raise ValidationError('Email already exists. Please login.')


class SortForm (FlaskForm):
    options = SelectField("sort by date", choices=["date_asc", "date_desc"])
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    email = StringField('Email', render_kw={"placeholder": "Email"}, validators=[DataRequired()])
    password = PasswordField('Password', render_kw={"placeholder": "password"}, validators=[DataRequired()])
    submit = SubmitField('Login')


class ContactForm(FlaskForm):
    name = StringField("Name", render_kw={"placeholder": "name"}, validators = [DataRequired("Please Enter Your Name")])
    email = EmailField("Email", render_kw={"placeholder": "email"}, validators = [DataRequired("Please enter your email address")])
    subject = StringField("Subject", render_kw={"placeholder": "subject"}, validators = [DataRequired("Please enter a subject.")])
    message = TextAreaField("Message", render_kw={"placeholder": "message"}, validators = [DataRequired("Please enter a message.")])
    submit = SubmitField("Send")


class CommentForm(FlaskForm):
    body = StringField('', validators=[InputRequired(), Length(max=512)])
    submit = SubmitField('Submit')
