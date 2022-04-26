from wtforms import Form
from wtforms.fields import EmailField, validators

class emailForm(Form):
	email = EmailField('Email')

