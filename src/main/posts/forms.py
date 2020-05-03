from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, DateField
from wtforms.validators import DataRequired

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    date_expires = DateField('Expiry Date (YYYY-MM-dd)', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Post')
