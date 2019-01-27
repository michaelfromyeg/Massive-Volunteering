import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from main import app, db, bcrypt, mail
from main.models import Org, Exp # Python still runs entire module! If db imported, must happen first
from main.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, RequestResetForm, ResetPasswordForm
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

@app.route("/")
@app.route("/home")
def home():
	page = request.args.get('page', 1, type=int)
	experiences = Exp.query.order_by(Exp.date_posted.desc()).paginate(page=page, per_page=5)
	return render_template('home.html', experiences=experiences)

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/register", methods=['GET','POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		org = Org(org_name=form.username.data, email=form.email.data, password=hashed_password)
		db.session.add(org)
		db.session.commit()
		flash(f'Your account has been created. You are now able to log-in. Check your email to verify your e-mail address.', 'success')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET','POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	if form.validate_on_submit():
		org = Org.query.filter_by(email=form.email.data).first()
		if form.email.data == 'admin@massive.com' and form.password.data == 'mcnallytigers':
			flash(f'You have been logged in as an administrator', 'success')
			return redirect(url_for('home'))
		elif org and bcrypt.check_password_hash(org.password, form.password.data):
			login_user(org, remember=form.remember.data)
			next_page = request.args.get('next')
			flash(f'You are logged in.', 'success')
			return redirect(next_page) if next_page else redirect(url_for('home'))
		else:
			flash(f'Login unsuccessful. Please check email and password.', 'danger')
	return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
	logout_user()
	flash(f'You are logged out.', 'success')
	return redirect(url_for('home'))

def save_picture(form_picture):
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex + f_ext
	picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

	output_size = (125, 125)
	i = Image.open(form_picture)
	i.thumbnail(output_size)

	i.save(picture_path)

	return picture_fn

@app.route("/account", methods=['GET','POST'])
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
		return redirect(url_for('account'))
	elif request.method == 'GET':
		form.username.data = current_user.org_name
		form.email.data = current_user.email
	image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
	return render_template('account.html', title='Account', image_file=image_file, form=form)

@app.route("/post/new", methods=['GET','POST'])
@login_required
def new_post():
	form = PostForm()
	if form.validate_on_submit():
		exper = Exp(name=form.title.data, content=form.content.data, organization=current_user)
		db.session.add(exper)
		db.session.commit()
		flash(f'Your post has been created.', 'success')
		return redirect(url_for('home'))
	return render_template('create_post.html', title='New Post', form=form, legend='New Post')

@app.route("/post/<int:exp_id>")
def post(exp_id):
	exper = Exp.query.get_or_404(exp_id)
	return render_template('post.html', name=exper.name, experience=exper)

@app.route("/post/<int:exp_id>/update", methods=['GET','POST'])
@login_required
def update_post(exp_id):
	exper = Exp.query.get_or_404(exp_id)
	if exper.organization != current_user:
		abort(403)
	form = PostForm()
	if form.validate_on_submit():
		exper.name = form.title.data
		exper.content = form.content.data
		db.session.commit()
		flash('Your post has been successfully updated.', 'success')
		return redirect(url_for('post', exp_id=exper.id))
	elif request.method == 'GET':
		form.title.data = exper.name
		form.content.data = exper.content
	return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')

@app.route("/post/<int:exp_id>/delete", methods=['POST'])
@login_required
def delete_post(exp_id):
	exper = Exp.query.get_or_404(exp_id)
	if exper.organization != current_user:
		abort(403)
	db.session.delete(exper)
	db.session.commit()
	flash('Your post has been deleted.', 'success')
	return redirect(url_for('home'))

@app.route("/user/<string:org_name>")
def user_posts(org_name):
	page = request.args.get('page', 1, type=int)
	org = Org.query.filter_by(org_name=org_name).first_or_404()
	experiences = Exp.query.filter_by(org=org.id).order_by(Exp.date_posted.desc()).paginate(page=page, per_page=5)
	return render_template('user_posts.html', experiences=experiences, organization=org)

@app.route("/reset_password", methods=['GET','POST'])
def reset_request():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RequestResetForm()
	if form.validate_on_submit():
		org = Org.query.filter_by(email=form.email.data).first()
		send_reset_email(org)
		flash('Check your inbox for further instructions.', 'info')
		return redirect(url_for('login'))
	return render_template('reset_request.html', title='Reset Password', form=form)

def send_reset_email(org):
	token = org.get_reset_token()
	msg = Message('Password Reset Request', sender='michaelfromyeg@gmail.com', recipients=[org.email])
	msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request, then simply ignore this email and no changes will occur.
'''
	mail.send(msg)

@app.route("/reset_password/<token>", methods=['GET','POST'])
def reset_token(token):
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	org = Org.verify_reset_token(token)
	if org is None:
		flash('That is an invalid or expired token.', 'warning')
		return redirect(url_for('reset_request'))
	form = ResetPasswordForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		org.password = hashed_password
		db.session.commit()
		flash(f'Your password has been updated.', 'success')
		return redirect(url_for('login'))
	return render_template('reset_token.html', title='Reset Password', form=form)
