from flask import Flask, render_template, request, url_for, redirect
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

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        if request.form.get('crear encuesta')=='Crear Encuesta':
            return redirect(url_for('create'))
    return render_template('index.html')

@app.route('/create/', methods=['GET','POST'])
def create():
    if request.method == 'POST':
        if not request.form:
            pass
        elif request.form.get('menu')=='Volver a Menu':
            return redirect(url_for('index'))
    return render_template('create.html')

if __name__=='__main__':
    app.run()