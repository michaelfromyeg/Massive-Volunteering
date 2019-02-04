from main.models import Org
from flask import flash
from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

class RegistrationForm(FlaskForm):
	username = StringField('Username', 
		validators=[DataRequired(), Length(min=2, max=20)])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Sign Up')
	
	def validate_username(self, org_name):
		org = Org.query.filter_by(org_name=org_name.data).first()
		if org:
			flash(f'That username is taken. Please choose a different username.', 'danger')
			raise ValidationError('Username taken. Please choose a different username.')
	def validate_email(self, email):
		email = Org.query.filter_by(email=email.data).first()
		if email:
			flash(f'That e-mail is taken. Please choose a different e-mail.', 'danger')
			raise ValidationError('E-mail taken. Please choose a different one.')

class LoginForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember = BooleanField('Remember Me')
	submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
	username = StringField('Username', 
		validators=[DataRequired(), Length(min=2, max=20)])
	email = StringField('Email', validators=[DataRequired(), Email()])
	picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg','png'])])
	submit = SubmitField('Update')

	def validate_username(self, org_name):
		if org_name.data != current_user.org_name:
			org = Org.query.filter_by(org_name=org_name.data).first()
			if org:
				flash(f'That username is taken. Please choose a different username.', 'danger')
				raise ValidationError('Username taken. Please choose a different username.')

	def validate_email(self, email):
		if email.data != current_user.email:
			email = Org.query.filter_by(email=email.data).first()
			if email:
				flash(f'That e-mail is taken. Please choose a different e-mail.', 'danger')
				raise ValidationError('E-mail taken. Please choose a different one.')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')

class RequestResetForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email()])
	submit = SubmitField('Request Password Reset')

	def validate_email(self, email):
		email = Org.query.filter_by(email=email.data).first()
		if email is None:
			flash(f'There is not account with that email. Please make an account first.', 'danger')
			raise ValidationError('No email.')

class ResetPasswordForm(FlaskForm):
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Reset Password')
