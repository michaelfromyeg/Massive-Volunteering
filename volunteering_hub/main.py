from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = '93742bf2883b9bdbc076fc21703c6bbe'

experiences = [
	{
		'organization': 'Festival of Trees',
		'title': 'Volunteer with Festival of Trees',
		'content': 'Here is a volunteer opportunity.',
		'date_posted': 'November 3, 2018',
		'date_expiry': 'December 19, 2018'
	},
	{
		'organization': 'Trick-or-Eat',
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

@app.route("/login")
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