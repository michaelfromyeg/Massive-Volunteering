from datetime import datetime
from flask import Flask, render_template, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from forms import RegistrationForm, LoginForm

app = Flask(__name__)

app.config['SECRET_KEY'] = '93742bf2883b9bdbc076fc21703c6bbe'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)

class Org(db.Model): # table name is 'org' by default (note: lowercase 'o')
	id = db.Column(db.Integer, primary_key=True)
	org_name = db.Column(db.String(20), unique=True, nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	logo = db.Column(db.String(20), nullable=False, default='default.jpg')
	password = db.Column(db.String(60), nullable=False)
	experiences = db.relationship('Exp', backref='org', lazy=True)

	def __repr__(self):
		return f"Organization('{self.org_name}', '{self.email}', '{self.logo}')"

class Exp(db.Model): # table name is 'exp' by default (note: lowercase 'o')
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), nullable=False)
	content = db.Column(db.Text, nullable=False)
	date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	date_expiry = db.Column(db.DateTime, nullable=False, default=datetime.utcnow + datetime.timedelta(days=7))
	org = db.Column(db.Integer, db.ForeignKey('org.id'), nullable=False)

	def __repr__(self):
		return f"Experience('{self.name}', '{self.date_posted}', '{self.org}')"



experiences = [
	{
		'title': 'Volunteer with Festival of Trees',
		'content': 'Here is a volunteer opportunity.',
		'date_posted': 'November 3, 2018',
		'date_expiry': 'December 19, 2018'
	},
	{
		'title': 'Volunteer with Trick-or-Eat',
		'content': 'Here is a volunteer opportunity.',
		'date_posted': 'October 1, 2018',
		'date_expiry': 'October 20, 2018'
	},
	{
		'title': 'Volunteer with Trick-or-Eat',
		'content': 'Here is a volunteer opportunity.',
		'date_posted': 'October 1, 2018',
		'date_expiry': 'October 20, 2018'
	},
	{
		'title': 'Volunteer with Trick-or-Eat',
		'content': 'Here is a volunteer opportunity.',
		'date_posted': 'October 1, 2018',
		'date_expiry': 'October 20, 2018'
	},
	{
		'title': 'Volunteer with Trick-or-Eat',
		'content': 'Here is a volunteer opportunity.',
		'date_posted': 'October 1, 2018',
		'date_expiry': 'October 20, 2018'
	}
]

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', experiences=experiences)

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/register", methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
    	flash(f'Account created for {form.username.data}!', 'success')
    	return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
    	if form.email.data == 'admin@massive.com' and form.password.data == 'mcnallytigers':
    		flash(f'You have been logged in', 'success')
    		return redirect(url_for('home'))
    	else:
    		flash(f'Login unsuccessful. Please check username and password.', 'danger')
    return render_template('login.html', title='Login', form=form)

if __name__ == '__main__':
	app.run(debug=True)