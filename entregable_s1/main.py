from crypt import methods
from flask import Flask, request, render_template, redirect, url_for
from flask_mail import Mail, Message 
import psycopg2
import forms

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

#------------------------------- Función para mandar mails ----------------------------------------------
# def enviar_encuesta(id_e): 
#     #id_e := id de encuesta cuyo url se enviará.

#     conn = get_dbconnection()               #Conexión a la base de datos.
#     cur = conn.cursor()
#     cur.execute("select id from email;")    #Query a base de datos de mails
#     rows = cur.fetchall()                   #Obtención de tuplas (con una única columna)
#     receptores = []                         #receptores := Lista de receptores para el email.
#     for r in rows:                          #Transformamos lista de tuplas a lista.
#         receptores.append(r[0])
#     cur.close()                             #Desconexión a la base de datos.
#     conn.close()
#     msg = Message(  
#                 'Prueba-Encuesta',                          #Asunto del email.
#                 sender =   'alvaro.castillo.rifo@gmail.com',#Emisor del email.
#                 recipients = receptores                     #Receptor del email.
#                 )
#     #Cuerpo del email
#     msg.body = "Hola puedes responder tu encuesta aqui: localhost:5000/encuesta/" + id_e + "/responder"
#     mail.send(msg)  #Envio del email.

#----------------------------------- Manejo Página principal ---------------------------------------
@app.route("/")
def pprincipal():
    return render_template("principal.html")

#----------- Manejo Página para el botón para ir a crear una encuesta? -------------
#@app.route("/createE", methods=['GET','POST'])
#def createE():
 #   if request.method == 'POST':
 #       if request.form.get('crear encuesta')=='Crear Encuesta':
 #           return redirect(url_for('create'))
 #   return render_template('createE.html')  

#----------------------------------- Manejo Página para crear encuesta ------------------------------
@app.route('/crear-encuesta/', methods=['GET','POST'])
def crearE():
    datos=[] #0 = titulo, 1 = id, 2 = fecha inicio, 3 = fecha final
    lp=[] # Preguntas
    la=[] # Lista de alternativas por pregunta
    size=0
    if request.method == 'POST':
        if request.form.get('menu')=='Volver a Menu':
            return redirect(url_for('manejador_pp'))
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
            conn = get_dbconnection()
            cur = conn.cursor()
            url = "localhost:5000/encuesta/"+datos[1] +"/responder"
            cur.execute("INSERT INTO encuesta (id_e,titulo,url,f_ini,f_exp) VALUES (%s,%s,%s,%s,%s)",(datos[1],datos[0],url,datos[2],datos[3],))
            conn.commit() 
            for i in range(len(lp)):
                id_p = datos[1]+'_p'+str(i)
                cur.execute("INSERT INTO pregunta (id_p,id_e,texto) VALUES (%s,%s,%s)",(id_p,datos[1],lp[i],))
                conn.commit()
                for j in range(len(la[i])):
                    id_a = id_p +'_a'+str(j)
                    cur.execute("INSERT INTO alternativa (id_a,id_p,texto,cont_r) VALUES (%s,%s,%s,%s)",(id_a,id_p,la[i][j],0,))
            conn.commit()
            cur.close()
            conn.close() 
    
    return render_template('crear_encuesta.html')

#-------------------------- Manejo de Página para agregar emails ------------------------------
@app.route("/email/registrar")
def registrar_email():
    emailTF = forms.emailForm()
    emailTF.validate()
    return render_template('registrar_email.html', title='Registration', eTF=emailTF)

#--------------------- Manejo de Página para ver lista de emails ---------------------------------
@app.route("/email/lista", methods=['GET','POST'])
def lista_email():
    
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
    return render_template('lista_email.html', title='Email DataBase', emails=emails, index=length )

#--------------------- Manejo de Página para finalizar registro de emails -------------------------
@app.route('/email/registro-exitoso')
def email_registrado():

    email = request.args.get('email', 'no email')

    conn = get_dbconnection()
    cur = conn.cursor()
    
    sqlquery = """ INSERT INTO email (id) VALUES ('%s') """ %(email)
    cur.execute( sqlquery )
    conn.commit()

    cur.close()
    conn.close()

    return render_template('email_registrado.html', title='Registration Successful', email=email)

#----------------------------- Manejo de envío de encuestas -------------------------------
@app.route("/lista-encuestas/enviar/<string:id_e>")
def enviar_encuesta(id_e):
    #id_e := id de encuesta cuyo url se enviará.
    conn = get_dbconnection()               #Conexión a la base de datos.
    cur = conn.cursor()
    cur.execute("select id from email;")    #Query a base de datos de mails
    rows = cur.fetchall()                   #Obtención de tuplas (con una única columna)
    receptores = []                         #receptores := Lista de receptores para el email.
    for r in rows:                          #Transformamos lista de tuplas a lista.
        receptores.append(r[0])
    cur.close()                             #Desconexión a la base de datos.
    conn.close()
    msg = Message(  
                'Prueba-Encuesta',                          #Asunto del email.
                sender =   'alvaro.castillo.rifo@gmail.com',#Emisor del email.
                recipients = receptores                     #Receptor del email.
                )
    #Cuerpo del email
    msg.body = "Hola puedes responder tu encuesta aqui: localhost:5000/encuesta/" + id_e + "/responder"
    mail.send(msg)  #Envio del email.

    return redirect(url_for('listaE'))

#-------------------------- Manejo de Página de lista de encuestas ----------------------------
@app.route("/lista-encuestas", methods=['GET','POST'])
def listaE():
    if request.method == 'POST':
        insertDescripcion()
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
    return render_template("lista_encuesta.html",titulos=titulos,id_es=id_es)
#--------------------------Inserta la descripcion--------------------------------------------}
def insertDescripcion():
    print("insertDescripcion!!")
    descripcion='NOME FUNCIONA EL PRIMER BOTON T.T'
    id='encuesta_1'
    conn = get_dbconnection() 
    cur = conn.cursor()
    # update encuesta set descripcion='descripcion de prueba' WHERE id_e='id5';
    sqlquery = "UPDATE encuesta SET descripcion = \'" + descripcion + "\' WHERE id_e=\'" + id + "\';"
    cur.execute(sqlquery)
    cur.close()
    cur = conn.cursor() 
    sqlquery2 = "select * from encuesta WHERE id_e=\'" + id + "\';"
    cur.execute(sqlquery2)
    row = cur.fetchall() 
    cur.close()
    print(row)
    conn.close()
                       
    

#------------------- Manejo de Página de Previsualización de Encuesta ----------------------
@app.route('/previsualizar/<string:id_e>')    #Url con la lista, tiene la id de encuesta en la url
def previsualizar(id_e):
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
    return render_template('previsualizar_encuesta.html', titulo=title, preguntas=preguntas, alternativas=alternativas)

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
    return render_template('respuestas.html', title=title, preguntas=preguntas, alternativas=alternativas)
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
    return render_template('responder.html', title=title, preguntas=preguntas, alternativas=alternativas)

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

if __name__=="__main__":
        app.run(debug=True)