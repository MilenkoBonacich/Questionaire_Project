from flask import Flask, request, render_template
import psycopg2


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

@app.route('/')
def my_form():
    return render_template('answers.html')
@app.route('/', methods={'POST'})
def my_form_post():
    text = request.form['u']
    conn = get_dbconnection()
    #Seleccionar titulo de la encuesta
    cur = conn.cursor()
    sqlquery = "select * from encuesta where encuesta.id_e = \'" + text + "\';"
    cur.execute(sqlquery)
    row = cur.fetchone()
    title = row[1] #text.upper()
    cur.close()
    #Seleccionar preguntas de la encuesta
    cur = conn.cursor()
    sqlquery = "select * from pregunta where pregunta.id_e = \'" + text + "\';"
    cur.execute(sqlquery)
    preguntas = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('list.html', title=title, preguntas=preguntas)
#@app.route("/")
#def index():
#    # Abrir un cursor para realizar operaciones sobre la base de datos
#   conn = get_dbconnection()
#    cur = conn.cursor()
    # Ejecutar una consulta SELECT
#    sqlquery = "select * from encuesta;"
#    cur.execute(sqlquery)
    # Obtener los resultados como objetos Python
#    row = cur.fetchone()
    # Cerrar la conexión con la base de datos
#    cur.close()
#    conn.close()
    # Recuperar datos del objeto Python
#    datoprueba = row[1]
    # Hacer algo con los datos
#    print(datoprueba)
#    return {"hello": "world"}

