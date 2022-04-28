from wtforms import Form, validators
from wtforms.fields import EmailField

class emailForm(Form):

	email = EmailField( 'Email', [ validators.InputRequired() ] )

