from flask import Flask
from flask import render_template
import forms

app = Flask(__name__)

@app.route("/")
def email_register():

	email = forms.emailForm()
	return render_template('structure.html', eTF=email)

if __name__ == '__main__':
    app.run( debug=True )