from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from main import db
from main.models import Exp
from main.posts.forms import PostForm

posts = Blueprint('posts', __name__)

@posts.route("/post/new", methods=['GET','POST'])
@login_required
def new_post():
	form = PostForm()
	if form.validate_on_submit():
		exper = Exp(name=form.title.data, content=form.content.data, organization=current_user, date_expiry=form.date_expires.data)
		db.session.add(exper)
		db.session.commit()
		flash(f'Your post has been created.', 'success')
		return redirect(url_for('index.home'))
	return render_template('create_post.html', title='New Post', form=form, legend='New Post')

@posts.route("/post/<int:exp_id>")
def post(exp_id):
	exper = Exp.query.get_or_404(exp_id)
	return render_template('post.html', name=exper.name, experience=exper)

@posts.route("/post/<int:exp_id>/update", methods=['GET','POST'])
@login_required
def update_post(exp_id):
	exper = Exp.query.get_or_404(exp_id)
	if exper.organization != current_user:
		abort(403)
	form = PostForm()
	if form.validate_on_submit():
		exper.name = form.title.data
		exper.content = form.content.data
		exper.date_expiry = form.date_expires.data
		db.session.commit()
		flash('Your post has been successfully updated.', 'success')
		return redirect(url_for('posts.post', exp_id=exper.id))
	elif request.method == 'GET':
		form.title.data = exper.name
		form.content.data = exper.content
		form.date_expires.data = exper.date_expiry
	return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')

@posts.route("/post/<int:exp_id>/delete", methods=['POST'])
@login_required
def delete_post(exp_id):
	exper = Exp.query.get_or_404(exp_id)
	if exper.organization != current_user:
		abort(403)
	db.session.delete(exper)
	db.session.commit()
	flash('Your post has been deleted.', 'success')
	return redirect(url_for('index.home'))