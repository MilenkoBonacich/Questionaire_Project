from flask import Flask
from flask import render_template, redirect, url_for, request

import psycopg2
import forms

app = Flask(__name__)

# Función que genera y retorna conexión con BD.
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

	'''
	Ruta Base de las User Stories US7 y US8
	En esta ruta aparece un campo de texto 
	para registrar emails + boton que lo envia a BD.
	Mas abajo aparece otro boton que te lleva a una lista
	de los emails registrados en la BD. 
	'''

	emailTF = forms.emailForm() # Campo de Texto para ingresar emails.
	emailTF.validate()			# Se valida que el campo de texto no este vacio.

	return render_template('email_Register.html', title='Registration', eTF=emailTF)
	# Carga el template html, entregandole un titulo y el campo de texto creado.


@app.route("/list")
def email_list():
	
	'''
	Ruta Listado de Emails
	En esta ruta se extraen y se imprimen 
	los emails ya ingresados en la BD.
	Tambien aparece un boton para volver a la ruta anterior.
	'''

	conn = get_dbconnection() 	# Se obtiene conexion con BD.
	cur = conn.cursor()			# Se obtiene el cursor de BD.
    
    # Query SQL, que extrae todos los emails en BD en orden alfabetico.
	sqlquery = "SELECT * FROM email ORDER BY id;"
	cur.execute(sqlquery)	# Se ejecuta la query.
	rows = cur.fetchall()	# Se extraen y guardan todas las filas de la query en una lista.
    
	cur.close()		# Se cierra el cursor de BD.
	conn.close()	# Se cierra la conexion con BD.

	# En una lista aparte, se extraen uno a uno los resultados extraidos de la query
	# con tal de obtener los strings (emails) unicamente.
	emails = []
	for r in rows:
		emails.append( r[0] )	

	length = len(emails)	# Se obtiene tamaño de la lista de emails.
	
	return render_template('email_List.html', title='Email DataBase', emails=emails, index=length )
	# Carga el template html, entregandole un titulo, la lista de emails y el tamaño de esta.


@app.route('/email')
def userEmail():

	'''
	Ruta de Confirmacion Email Registrado.
	En esta ruta, se recibe como parametro el email ingresado en el campo
	de texto mencionado anteriormente (vease email_register, linea 22).
	El email luego es insertado en la BD, y en la pagina se imprime un mensaje
	confirmando este hecho.
	Al final de la pagina aparece un boton para volver a la ruta anterior.
	'''

	# Se obtiene el email entregado en el campo de texto anteriormente.
	email = request.args.get('email', 'no email')

	conn = get_dbconnection()	# Se obtiene conexion con BD.
	cur = conn.cursor()			# Se obtiene el cursor de BD.
	
	# Query SQL que realiza el insert del email entregado a la BD.
	sqlquery = """ INSERT INTO email (id) VALUES ('%s') """ %(email)
	cur.execute( sqlquery )	# Se ejecuta la query.
	conn.commit()			# Se ejecuta el cambio en BD.

	cur.close()		# Se cierra el cursor de BD.
	conn.close()	# Se cierra la conexion con BD.

	return render_template('email_Confirm.html', title='Registration Successful', email=email)
	# Carga el template html, entregandole un titulo y el email ingresado anteriormente.


if __name__ == '__main__':
    app.run( debug=True )