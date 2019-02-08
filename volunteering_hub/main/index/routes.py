from flask import render_template, request, Blueprint
from main.models import Exp

index = Blueprint('index', __name__)

@index.route("/")
@index.route("/home")
def home():
	page = request.args.get('page', 1, type=int)
	sortby = request.args.get('sortby', 1, type=str)
	if sortby == 'date_posted':
		experiences = Exp.query.order_by(Exp.date_posted.desc()).paginate(page=page, per_page=5)
		return render_template('home.html', experiences=experiences)
	if sortby == 'date_expiry':
		experiences = Exp.query.order_by(Exp.date_expiry.asc()).paginate(page=page, per_page=5)
		return render_template('home.html', experiences=experiences)
	experiences = Exp.query.order_by(Exp.date_expiry.asc()).paginate(page=page, per_page=5)
	return render_template('home.html', experiences=experiences)


@index.route("/about")
def about():
    return render_template('about.html')