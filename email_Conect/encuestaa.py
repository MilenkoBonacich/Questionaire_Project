# from crypt import methods
# from sqlite3 import Row
# from turtle import title
# from crypt import methods
# from multiprocessing import context
# from xml.etree.ElementTree import Comment
from flask import Flask, request, render_template, redirect, url_for
#from flask import Flask, render_template, request. url_for
from flask_mail import Mail, Message 
import psycopg2

app = Flask(__name__)
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'alvaro.castillo.rifo@gmail.com'
app.config['MAIL_PASSWORD'] = 'isfiwsphwejadstk'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


def get_dbconnection():
    PSQL_HOST = "ec2-52-201-124-168.compute-1.amazonaws.com"
    PSQL_PORT = "5432"
    PSQL_USER = "hppcxweyblynah"
    PSQL_PASS = "e4dbaf0502a56b15b4a64151940508613171a9e287817e5a4417d292fa8eb5ec"
    PSQL_DB = "de3skgdka01pk8"
    connstr = "host=%s port=%s user=%s password=%s dbname=%s" % (PSQL_HOST, PSQL_PORT, PSQL_USER, PSQL_PASS, PSQL_DB)
    conn = psycopg2.connect(connstr)
    return conn

def emailSend(url):
    conn = get_dbconnection()
    cur = conn.cursor()
    sqlquery = "select id from email;"
    cur.execute(sqlquery)
    rows = cur.fetchall()
    receptores = []
    for r in rows:
        receptores.append(r[0])
    cur.close()
    conn.close()
    msg = Message('Prueba-Encuesta', sender =   'alvaro.castillo.rifo@gmail.com', recipients = receptores)
    msg.body = "Hola puedes responder tu encuesta aqui: localhost:5000/encuesta/" + url + "/responder"
    mail.send(msg)


@app.route("/")
def hello_world():
    return render_template("index.html")


@app.route("/createE")
def createE():
    return render_template("createE.html")

@app.route("/agreeE")
def agreeE():
    return render_template("agreeE.html")

@app.route("/watchE/send/<string:id_e>")
def sendUrl(id_e):
    emailSend(id_e)
    return redirect(url_for('watchE'))


@app.route("/watchE")
def watchE():
    conn = get_dbconnection() 
    cur = conn.cursor()
    sqlquery = "select titulo from encuesta;"
    cur.execute(sqlquery)
    row = cur.fetchall() 
    titulos=row
    cur.close()                     
    cur = conn.cursor() 
    sqlquery2 = "select id_e from encuesta;" 
    cur.execute(sqlquery2)
    row = cur.fetchall() 
    id_es=row
    cur.close()  
    conn.close()
    return render_template("watchE.html",titulos=titulos,id_es=id_es)


    # if request.method == 'POST':
    #     seleccion= request.form.get('prev')
    #     return render_template("watchE.html",titulos=seleccion)
    #     # comment_form = forms.CommentForm(request.form)
    #     # print(comment_form)
    # else:
    #     titulos={"encuesta_1","Encuesta2","Encuesta3"}
    #     return render_template("watchE.html",titulos=titulos)

@app.route('/watchE/<string:id_e>')    #Url con la lista, tiene la id de encuesta en la url
def previewE(id_e):
    conn = get_dbconnection()                       #Conexión a la base de datos
    #Seleccionar titulo de la encuesta
    cur = conn.cursor()
    sqlquery = "select * from encuesta where encuesta.id_e = \'" + id_e + "\';"
    cur.execute(sqlquery)
    row = cur.fetchone()            #Acceso a los datos de la encuesta

    if row is None:                 #Si no se obtiene nada se retorna error.
        return {"Error":"No existe esta encuesta :("}

    title = row[1]                  #Título de la encuesta
    cur.close()                     #Se cierra el cursor
    cur = conn.cursor()             #Se reabre el cursor

    sqlquery = "select * from pregunta where pregunta.id_e = \'" + id_e + "\';" #Arreglo de preguntas
    cur.execute(sqlquery)
    preguntas = cur.fetchall()
    cur.close()
    cur = conn.cursor()
    sqlquery =  """
                select *
                from alternativa a, (select p.id_p from pregunta p where p.id_e = \'""" + id_e + """\') as b
                where a.id_p = b.id_p;
                """
    cur.execute(sqlquery)
    alternativas = cur.fetchall()   #Arreglo de alternativas
    cur.close()
    conn.close()
    return render_template('previewE.html', titulo=title, preguntas=preguntas, alternativas=alternativas)

#Código Franco: Lista de Respuestas--------------------------------------------------------------------------
@app.route('/encuesta/<string:id_e>/respuestas')    #Url con la lista, tiene la id de encuesta en la url
def respuestas(id_e):
    conn = get_dbconnection()                       #Conexión a la base de datos
    #Seleccionar titulo de la encuesta
    cur = conn.cursor()
    sqlquery = "select * from encuesta where encuesta.id_e = \'" + id_e + "\';"
    cur.execute(sqlquery)
    row = cur.fetchone()            #Acceso a los datos de la encuesta

    if row is None:                 #Si no se obtiene nada se retorna error.
        return {"Error":"No existe esta encuesta :("}

    title = row[1]                  #Título de la encuesta
    cur.close()                     #Se cierra el cursor
    #Seleccionar preguntas de la encuesta
    cur = conn.cursor()             #Se reabre el cursor
    sqlquery = "select * from pregunta where pregunta.id_e = \'" + id_e + "\';" #Arreglo de preguntas
    cur.execute(sqlquery)
    preguntas = cur.fetchall()
    cur.close()
    cur = conn.cursor()
    sqlquery =  """
                select *
                from alternativa a, (select p.id_p from pregunta p where p.id_e = \'""" + id_e + """\') as b
                where a.id_p = b.id_p;
                """
    cur.execute(sqlquery)
    alternativas = cur.fetchall()   #Arreglo de alternativas
    cur.close()
    conn.close()
    return render_template('list.html', title=title, preguntas=preguntas, alternativas=alternativas)
#-----------------------------------------------------------------------------------------------------------------
#Código franco: Formulario para enviar respuesta------------------------------------------------------------------
@app.route('/encuesta/<string:id_e>/responder')    #Url con la lista, tiene la id de encuesta en la url
def responder(id_e):
    conn = get_dbconnection()                       #Conexión a la base de datos
    #Seleccionar titulo de la encuesta
    cur = conn.cursor()
    sqlquery = "select * from encuesta where encuesta.id_e = \'" + id_e + "\';"
    cur.execute(sqlquery)
    row = cur.fetchone()            #Acceso a los datos de la encuesta

    if row is None:                 #Si no se obtiene nada se retorna error.
        return {"Error":"No existe esta encuesta :("}

    title = row[1]                  #Título de la encuesta
    cur.close()                     #Se cierra el cursor
    #Seleccionar preguntas de la encuesta
    cur = conn.cursor()             #Se reabre el cursor
    sqlquery = "select * from pregunta where pregunta.id_e = \'" + id_e + "\';" #Arreglo de preguntas
    cur.execute(sqlquery)
    preguntas = cur.fetchall()
    cur.close()
    cur = conn.cursor()
    sqlquery =  """
                select *
                from alternativa a, (select p.id_p from pregunta p where p.id_e = \'""" + id_e + """\') as b
                where a.id_p = b.id_p;
                """
    cur.execute(sqlquery)
    alternativas = cur.fetchall()   #Arreglo de alternativas
    cur.close()
    conn.close()
    return render_template('formulario.html', title=title, preguntas=preguntas, alternativas=alternativas)

@app.route('/encuesta/<string:id_e>/responder', methods={'POST'})
def enviar(id_e):
    conn = get_dbconnection()
    cur = conn.cursor()

    opciones = list(request.form.keys())
    opciones.remove("enviar_respuesta")
    resp = []
    for op in opciones:
        resp.append(request.form[op])
    for r in resp:
        query = """ UPDATE alternativa
                    SET cont_r = cont_r+1
                    WHERE id_a = \'""" + r + "\'"
        cur.execute(query)
    conn.commit()
    cur.close()
    conn.close()
    return "<h1>Greacias! :D</h1><h2>Agradecemos su participación</h2>"
#-----------------------------------------------------------------------------------------------------------------

# @app.route("/previewE/<param>/")
# def preview(param):
   
#     # titulo="Encuesta 82"
#     # npreguntas=["Le gusta el queso?","Come flan?","Va al baño seguido?","LLora por las noches?","Juega lolcito?"]
#     # alter1=["si","no"]
#     # alter2={"si","no"}
#     context = {
#         'titulo' : '{}'.format(param),
#         # 'npreguntas' : npreguntas,
#         # 'alter1' : alter1,
#     }
#     return render_template('previewE.html',**context)


# @app.route("/login")
# def create():
#     return render_template("login.html")

# # @app.route("/watchE/previewE")
# # def previewE():
# #     return render_template("previewE.html")

if __name__=="__main__":
        app.run(debug=True)