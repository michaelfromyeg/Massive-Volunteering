from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from main import db, bcrypt
from main.models import Org, Exp
from main.orgs.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                   RequestResetForm, ResetPasswordForm)
from main.orgs.utils import save_picture, send_reset_email

orgs = Blueprint('orgs', __name__)

@orgs.route("/register", methods=['GET','POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('index.home'))
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		org = Org(org_name=form.username.data, email=form.email.data, password=hashed_password)
		db.session.add(org)
		db.session.commit()
		flash(f'Your account has been created. You are now able to log-in. Check your email to verify your e-mail address.', 'success')
		return redirect(url_for('orgs.login'))
	return render_template('register.html', title='Register', form=form)

@orgs.route("/login", methods=['GET','POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index.home'))
	form = LoginForm()
	if form.validate_on_submit():
		org = Org.query.filter_by(email=form.email.data).first()
		if form.email.data == 'admin@massive.com' and form.password.data == 'password':
			flash(f'You have been logged in as an administrator', 'success')
			return redirect(url_for('index.home'))
		elif org and bcrypt.check_password_hash(org.password, form.password.data):
			login_user(org, remember=form.remember.data)
			next_page = request.args.get('next')
			flash(f'You are logged in.', 'success')
			return redirect(next_page) if next_page else redirect(url_for('index.home'))
		else:
			flash(f'Login unsuccessful. Please check email and password.', 'danger')
	return render_template('login.html', title='Login', form=form)

@orgs.route("/logout")
def logout():
	logout_user()
	flash(f'You are logged out.', 'success')
	return redirect(url_for('index.home'))

@orgs.route("/account", methods=['GET','POST'])
@login_required
def account():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_picture(form.picture.data)
			current_user.image_file = picture_file
		current_user.org_name = form.username.data
		current_user.email = form.email.data
		db.session.commit()
		flash(f'Your account has been successfully updated!', 'success')
		return redirect(url_for('orgs.account'))
	elif request.method == 'GET':
		form.username.data = current_user.org_name
		form.email.data = current_user.email
	image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
	return render_template('account.html', title='Account', image_file=image_file, form=form)

@orgs.route("/user/<string:org_name>")
def user_posts(org_name):
	page = request.args.get('page', 1, type=int)
	org = Org.query.filter_by(org_name=org_name).first_or_404()
	experiences = Exp.query.filter_by(org=org.id).order_by(Exp.date_posted.desc()).paginate(page=page, per_page=5)
	return render_template('user_posts.html', experiences=experiences, organization=org)

@orgs.route("/reset_password", methods=['GET','POST'])
def reset_request():
	if current_user.is_authenticated:
		return redirect(url_for('index.home'))
	form = RequestResetForm()
	if form.validate_on_submit():
		org = Org.query.filter_by(email=form.email.data).first()
		send_reset_email(org)
		flash('Check your inbox for further instructions.', 'info')
		return redirect(url_for('orgs.login'))
	return render_template('reset_request.html', title='Reset Password', form=form)

@orgs.route("/reset_password/<token>", methods=['GET','POST'])
def reset_token(token):
	if current_user.is_authenticated:
		return redirect(url_for('index.home'))
	org = Org.verify_reset_token(token)
	if org is None:
		flash('That is an invalid or expired token.', 'warning')
		return redirect(url_for('orgs.reset_request'))
	form = ResetPasswordForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		org.password = hashed_password
		db.session.commit()
		flash(f'Your password has been updated.', 'success')
		return redirect(url_for('orgs.login'))
	return render_template('reset_token.html', title='Reset Password', form=form)
