import os
import secrets
from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from main import mail
from main import app

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

def send_reset_email(org):
	token = org.get_reset_token()
	msg = Message('Password Reset Request', sender='michaelfromyeg@gmail.com', recipients=[org.email])
	msg.body = f'''To reset your password, visit the following link:
{url_for('orgs.reset_token', token=token, _external=True)}

If you did not make this request, then simply ignore this email and no changes will occur.
'''
	mail.send(msg)