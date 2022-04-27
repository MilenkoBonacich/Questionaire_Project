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
    datos=[] #0 = titulo, 1 = id, 2 = fecha inicio, 3 = fecha final
    lp=[] # Preguntas
    la=[] # Lista de alternativas por pregunta
    size=0
    if request.method == 'POST':
        if request.form.get('menu')=='Volver a Menu':
            return redirect(url_for('index'))
        elif request.form.get('crear')=='Crear Encuesta':
            f = request.form
            for key in f.keys():
                for value in f.getlist(key):
                    if(key.startswith('p')):
                        size +=1
                        lp.append(value)
                        la.append([])
                    elif(key.startswith('a')):
                        la[size-1].append(value)
                    elif(key!='crear'):
                        datos.append(value)
            print(datos) 
            print(lp)
            print(la)
            conn = get_dbconnection()
            cur = conn.cursor()
            url = "localhost/encuesta"+datos[0] +"/responder"
            cur.execute("INSERT INTO encuesta (id_e,titulo,url,f_ini,f_exp) VALUES (%s,%s,%s,%s,%s)",(datos[0],datos[1],url,datos[2],datos[3],))
            conn.commit() 
            for i in range(len(lp)):
                id_p = datos[0]+'_p'+str(i)
                cur.execute("INSERT INTO pregunta (id_p,id_e,texto) VALUES (%s,%s,%s)",(id_p,datos[0],lp[i],))
                conn.commit()
                for j in range(len(la[i])):
                    id_a = id_p +'_a'+str(j)
                    cur.execute("INSERT INTO alternativa (id_a,id_p,texto,cont_r) VALUES (%s,%s,%s,%s)",(id_a,id_p,la[i][j],0,))
            conn.commit()
            cur.close()
            conn.close() 
    


    return render_template('create.html')

if __name__=='__main__':
    app.run()