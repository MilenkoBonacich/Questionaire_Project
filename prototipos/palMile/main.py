from flask import Flask, request, render_template, redirect, url_for
import psycopg2


app = Flask(__name__)


# def get_dbconnection():
#     PSQL_HOST = "ec2-52-201-124-168.compute-1.amazonaws.com"
#     PSQL_PORT = "5432"
#     PSQL_USER = "hppcxweyblynah"
#     PSQL_PASS = "e4dbaf0502a56b15b4a64151940508613171a9e287817e5a4417d292fa8eb5ec"
#     PSQL_DB = "de3skgdka01pk8"
#     connstr = "host=%s port=%s user=%s password=%s dbname=%s" % (PSQL_HOST, PSQL_PORT, PSQL_USER, PSQL_PASS, PSQL_DB)
#     conn = psycopg2.connect(connstr)
#     return conn
listaP = []
listaA = []
@app.route('/')
def home(): #Página con cuadro de texto para consultar por un id de encuesta
    return render_template('lista.html', lista=listaP, alternativas=listaA)
@app.route('/', methods={'POST'})
def addtolist(): #Página con cuadro de texto para consultar por un id de encuesta
    if 'agregaPregunta' in request.form.keys():
        pregunta = request.form['agregaPregunta']
        listaP.append(pregunta)
        listaA.append([])
    else:
        index = 0
        val = ""
        for key in request.form.keys():
            if request.form[key]:
                index = int(key.replace("agregaAlternativa",""))
                val = request.form[key]
                break
        listaA[index].append(val)
        print(val)
    return render_template('lista.html', lista=listaP, alternativas=listaA)

