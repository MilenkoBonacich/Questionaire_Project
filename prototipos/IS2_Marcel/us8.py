from flask import Flask
from flask import render_template, redirect, url_for, request

import psycopg2
import forms

app = Flask(__name__)

def get_dbconnection():
    PSQL_HOST = "ec2-52-201-124-168.compute-1.amazonaws.com"
    PSQL_PORT = "5432"
    PSQL_USER = "hppcxweyblynah"
    PSQL_PASS = "e4dbaf0502a56b15b4a64151940508613171a9e287817e5a4417d292fa8eb5ec"
    PSQL_DB = "de3skgdka01pk8"
    connstr = "host=%s port=%s user=%s password=%s dbname=%s" % (PSQL_HOST, PSQL_PORT, PSQL_USER, PSQL_PASS, PSQL_DB)
    conn = psycopg2.connect(connstr)
    return conn

@app.route("/")
def email_register():

	emailTF = forms.emailForm()
	emailTF.validate()

	return render_template('email_Register.html', title='Registration', eTF=emailTF)


@app.route("/list")
def email_list():
	
	conn = get_dbconnection()
	cur = conn.cursor()
    
	sqlquery = "SELECT * FROM email ORDER BY id;"
	cur.execute(sqlquery)
	rows = cur.fetchall()
    
	cur.close()
	conn.close()

	emails = []
	for r in rows:
		emails.append( r[0] )

	length = len(emails)
	return render_template('email_List.html', title='Email DataBase', emails=emails, index=length )


@app.route('/email')
def userEmail():

	email = request.args.get('email', 'no email')

	conn = get_dbconnection()
	cur = conn.cursor()
	
	sqlquery = """ INSERT INTO email (id) VALUES ('%s') """ %(email)
	cur.execute( sqlquery )
	conn.commit()

	cur.close()
	conn.close()

	return render_template('email_Confirm.html', title='Registration Successful', email=email)

if __name__ == '__main__':
    app.run( debug=True )