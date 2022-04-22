from wtforms import Form
from wtforms.fields import EmailField, SubmitField

class emailForm(Form):
	email = EmailField('Email')
	submit = SubmitField('Register')
