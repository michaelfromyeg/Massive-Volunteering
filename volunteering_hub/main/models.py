from datetime import datetime
from main import db, login_manager, app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

@login_manager.user_loader
def load_user(org_id):
	return Org.query.get(int(org_id))

class Org(db.Model, UserMixin): # table name is 'org' by default (note: lowercase 'o')
	id = db.Column(db.Integer, primary_key=True)
	org_name = db.Column(db.String(20), unique=True, nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
	password = db.Column(db.String(60), nullable=False)
	experiences = db.relationship('Exp', backref='organization', lazy=True)

	def get_reset_token(self, expires_seconds=1800):
		s = Serializer(app.config['SECRET_KEY'], expires_seconds)
		return s.dumps({'org_id': self.id}).decode('utf-8')

	@staticmethod
	def verify_reset_token(token):
		s = Serializer(app.config['SECRET_KEY'])
		try:
			org_id = s.loads(token)['org_id']
		except: 
			return None
		return Org.query.get(org_id)

	def __repr__(self):
		return f"Organization('{self.org_name}', '{self.email}', '{self.image_file}')"

class Exp(db.Model): # table name is 'exp' by default (note: lowercase 'o')
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), nullable=False)
	content = db.Column(db.Text, nullable=False)
	date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	date_expiry = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	org = db.Column(db.Integer, db.ForeignKey('org.id'), nullable=False)

	def __repr__(self):
		return f"Experience('{self.name}', '{self.date_posted}')"

