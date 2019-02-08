from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from main.config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'orgs.login'
login_manager.login_message_category = 'info'
mail = Mail(app)

from main.orgs.routes import orgs
from main.posts.routes import posts
from main.index.routes import index
from main.errors.handlers import errors

app.register_blueprint(orgs)
app.register_blueprint(posts)
app.register_blueprint(index)
app.register_blueprint(errors)