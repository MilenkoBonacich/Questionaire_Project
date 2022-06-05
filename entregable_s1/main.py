from flask import Flask, request, render_template, redirect, url_for, flash
from flask_mail import Mail, Message 
import psycopg2
import forms

#Paquetes para login
from flask_login import LoginManager, login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from models.ModelUser import ModelUser
from models.entities.User import User
from flask_wtf.csrf import CSRFProtect
import secrets
#Para los gráficos
import matplotlib.pyplot as plt
import base64
from io import BytesIO

app = Flask(__name__)
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'alvaro.castillo.rifo@gmail.com'
app.config['MAIL_PASSWORD'] = 'isfiwsphwejadstk'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['SECRET_KEY'] = secrets.token_hex(16)

csrf = CSRFProtect()
csrf.init_app(app)
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

def getPlot(labels, sizes):
    for i in range(len(sizes)):
        if sizes[i] == 0:
            sizes[i] = 1
    print("Debug:")
    print(labels)
    print(sizes)
    fig, ax = plt.subplots()
    fig.set_size_inches(10, 3)
    patches, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
#    for text in texts:
#        text.set_color('grey')for autotext in autotexts:
#    autotext.set_color('grey')# Equal aspect ratio ensures that pie is drawn as a circle
    ax.axis('equal')  
    plt.tight_layout()
    #Guardar archivo en buffer
    buf = BytesIO()
    fig.savefig(buf, format="png")
    #Imagen a imprimir en html
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return data

def crearUsers():   #Función para insertar usuarios escritos en el archivo "users"
    with open('users') as file: #Abrir archivo "users"
        for line in file:
            #Cada línea está escrita de la forma: "[Usuario] [Contraseña]"
            split = line.split()
            username = split[0]
            password = split[1]
            nick = split[2]

            #Checkeo de existencia del usuario, si no existe se inserta el usuario
            conn = get_dbconnection()
            cur = conn.cursor()
            sqlquery =  "select * from usuario where usuario.username = \'" + username + "\';"
            cur.execute(sqlquery)
            existente = cur.fetchone()
            if existente is None:
                #Se inserta el usuario y el hash de su contraseña
                sqlquery =  "INSERT INTO usuario VALUES (\'"+username+"\',\'"+generate_password_hash(password)+"\',\'"+nick+"\');"
                cur.execute( sqlquery )
                conn.commit()
                print("Insertado: " + nick)
            else:
                print("Existente: " + nick)
            cur.close()
            conn.close() 
crearUsers()

login_manager_app = LoginManager(app)
@login_manager_app.user_loader
def load_user(id):
    return ModelUser.get_by_id(get_dbconnection(),id)

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

#----------------------------- Manejo de login ---------------------------------------------
@app.route("/ingresar")
def login():
    return render_template("login.html")
@app.route("/ingresar", methods=['POST'])
def checkLogin():
    #obtener email y contraseña ingresados
    username = request.form['username']
    password = request.form['password']
    user = User(username,password)
    logged_user = ModelUser.login(get_dbconnection(), user)
    if logged_user != None: #Usuario existe
        if logged_user.password:    #Contraseña coincide
            login_user(logged_user)
            return redirect(url_for('pprincipal'))
        else:
            flash("Contraseña invalida")
            return render_template("login.html")
    else:
        flash("Usuario no encontrado")
        return render_template("login.html")
@app.route("/salir")
def logout():
    logout_user()
    return redirect(url_for('login'))

def status_401(error):
    return redirect(url_for('login'))

app.register_error_handler(401,status_401)
#----------------------------------- Manejo Página principal ---------------------------------------
@app.route("/")
@login_required
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
@login_required
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
            cur.execute("INSERT INTO encuesta (id_e,titulo,url,f_ini,f_exp,descripcion) VALUES (%s,%s,%s,%s,%s,%s)",(datos[1],datos[0],url,datos[3],datos[4],datos[2]))
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
@login_required
def registrar_email():
    emailTF = forms.emailForm()
    emailTF.validate()
    return render_template('registrar_email.html', title='Registration', eTF=emailTF)

#--------------------- Manejo de Página para ver lista de emails ---------------------------------
@app.route("/email/lista")
@login_required
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
@login_required
def email_registrado():

    email = request.args.get('email', 'no email')

    conn = get_dbconnection()
    cur = conn.cursor()
    
    sqlquery = """ INSERT INTO email (id) VALUES ('%s') """ %(email)
    cur.execute( sqlquery )
    conn.commit()

    cur.close()
    conn.close()

    #flash("Email registrado exitosamente.")
    #return redirect( url_for('registrar_email') )
    return render_template('email_registrado.html', title='Registration Successful', email=email)

#--------------------- Manejo de Página de Confirmacion Eliminacion Correo - Usuario -------------------------
@app.route('/email/desuscripcion/<string:id_em>')
def desuscripcion_email(id_em):

    return render_template('desuscripcion_email.html', title='Desuscripcion Email', email=id_em, usuario="susc")

#--------------------- Manejo de Página para eliminar emails -------------------------
@app.route("/email/borrar/<string:user>/<string:id_em>")
def borrar_email(id_em, user):

    if user == "admin":
        url = 'lista_email'
        flash('Correo eliminado exitosamente.')
    else:
        url = 'pprincipal'


    conn = get_dbconnection()
    cur = conn.cursor()
    
    cur.execute( "DELETE FROM email WHERE id = %s", (id_em,) )
    conn.commit()

    cur.close()
    conn.close()

    if user == "susc":
        return "Su correo ha sido eliminado."


    return redirect(url_for( url ))

#----------------------------- Manejo de envío de encuestas -------------------------------
@app.route("/lista-encuestas/enviar/<string:id_e>")
@login_required
def enviar_encuesta(id_e):
    #id_e := id de encuesta cuyo url se enviará.
    conn = get_dbconnection()               #Conexión a la base de datos.
    cur = conn.cursor()
    cur.execute("select id from email;")    #Query a base de datos de mails
    rows = cur.fetchall()                   #Obtención de tuplas (con una única columna)
    receptores = []                         #receptores := Lista de receptores para el email.
    for r in rows:                          #Transformamos lista de tuplas a lista.
        receptores.append(r[0])
    cur.execute("select descripcion from encuesta where id_e=\'" +id_e+ "\'")
    descrip=cur.fetchone()
    cur.close()                             #Desconexión a la base de datos.
    conn.close()
    
    msg1 = "Hola, puedes responder tu encuesta en el siguiente: localhost:5000/encuesta/" + id_e + "/responder\n\n"
    descr=  "La descripcion de la encuesta es: " + descrip[0] + "\n"
    msg2 = "Si desea dejar de recibir estos correos: localhost:5000/email/desuscripcion/"

    with mail.connect() as m_conn:

        for dst in receptores:
            
            message = msg1 + descr + msg2 + dst
            subj = "Prueba Encuesta" 

            msg = Message(
                subject = subj,
                sender = 'alvaro.castillo.rifo@gmail.com',
                body = message,
                recipients = [ dst ] )

            m_conn.send( msg )

    
    """
    msg = Message(  
                'Prueba-Encuesta',                          #Asunto del email.
                sender =   'alvaro.castillo.rifo@gmail.com',#Emisor del email.
                recipients = receptores                     #Receptor del email.
                )
    #Cuerpo del email
    
    msg.body = "Hola puedes responder tu encuesta aqui: localhost:5000/encuesta/" + id_e + "/responder"
    mail.send(msg)  #Envio del email.
    """

    return redirect(url_for('listaE'))

#-------------------------- Manejo de Página de lista de encuestas ----------------------------
@app.route("/lista-encuestas", methods=['GET','POST'])
@login_required
def listaE():
    if request.method == 'POST':
        if request.form['signup']=='ok':
            descripcion=request.form['descrip']
            ids=request.form['prodId']  
            insertDescripcion(ids,descripcion)
        elif request.form['signup']=='Eliminar':
            # print("HOLAAAAA")
            ids=request.form['prodId']
            # print(ids)
            eliminarEncuesta(ids)
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
    cur=conn.cursor()
    sqlquery3="select descripcion from encuesta"
    cur.execute(sqlquery3)
    row = cur.fetchall() 
    descripciones=row
    cur.close()  
    conn.close()
    return render_template("lista_encuesta.html",titulos=titulos,id_es=id_es,descripciones=descripciones)
#--------------------------Inserta la descripcion--------------------------------------------}
def insertDescripcion(id,descripcion):
    print("insertDescripcion!!")
    # descripcion='Veamos si funca'
    # id='encuesta_2'
    conn = get_dbconnection() 
    cur = conn.cursor()
    # update encuesta set descripcion='descripcion de prueba' WHERE id_e='id5';
    sqlquery = "UPDATE encuesta SET descripcion = \'" + descripcion + "\' WHERE id_e=\'" + id + "\';"
    cur.execute(sqlquery)
    conn.commit()
    cur.close()
    # cur = conn.cursor() 
    # sqlquery2 = "select * from encuesta WHERE id_e=\'" + id + "\';"
    # cur.execute(sqlquery2)
    # row = cur.fetchall() 
    # cur.close()
    # print(row)
    conn.close()    
#-------------------------Funcion Eliminar Encuesta-------------------------------#                    
def eliminarEncuesta(id):
    print("insertDescripcion!!")
    # descripcion='Veamos si funca'
    # id='encuesta_2'
    conn = get_dbconnection() 
    cur = conn.cursor()
    # update encuesta set descripcion='descripcion de prueba' WHERE id_e='id5';
    sqlquery = "DELETE FROM encuesta WHERE id_e=\'" + id + "\';"
    cur.execute(sqlquery)
    conn.commit()
    cur.close()
   
    conn.close()  





#------------------- Manejo de Página de Previsualización de Encuesta ----------------------
@app.route('/previsualizar/<string:id_e>')    #Url con la lista, tiene la id de encuesta en la url
@login_required
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
    return render_template('previsualizar_encuesta.html', id=id_e, titulo=title, preguntas=preguntas, alternativas=alternativas)

# -------------------Edicion de pregunta-------------------------
@app.route('/previsualizar/<string:id_e>/editar-preguntas/<string:id_p>', methods=['GET','POST'])
@login_required
def editar_preguntas(id_e, id_p):

    conn = get_dbconnection()                       #Conexión a la base de datos
    #Seleccionar titulo de la encuesta
    cur = conn.cursor()
    sqlquery = "select * from pregunta where pregunta.id_p = \'" + id_p + "\';"
    cur.execute(sqlquery)
    pregunta = cur.fetchone()
    cur.close()
    cur = conn.cursor()
    sqlquery = "select * from alternativa where alternativa.id_p = \'" + id_p + "\';"
    cur.execute(sqlquery)
    alternativas = cur.fetchall()
    cur.close()
    if request.method == 'POST':
        p = None
        la=[] # Lista de alternativas por pregunta
        if request.form.get('save')=='Guardar Cambios':
            p = request.form['p']
            la = request.form.getlist('a')
            cur=conn.cursor()
            cur.execute("UPDATE pregunta SET texto=%s WHERE id_p=%s",(p,id_p))
            for i in range(len(la)):
                cur.execute("UPDATE alternativa SET texto=%s WHERE id_a=%s",(la[i],alternativas[i][0]))
            conn.commit()
            cur.close()
            conn.close()
            return redirect(url_for('previsualizar',id_e=id_e))
    conn.close()
    return render_template('editar_preguntas.html', pregunta=pregunta, alternativas=alternativas, id_e=id_e)

@app.route('/previsualizar/<string:id_e>/borrar_pregunta/<string:id_p>', methods=['GET','POST'])
@login_required
def borrar_pregunta(id_e,id_p):
    conn = get_dbconnection()
    cur = conn.cursor()
    cur.execute("DELETE from pregunta WHERE id_p = \'" + id_p + "\';")
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('previsualizar',id_e=id_e))

#----------------------------------------code Alvaro-------------------------
@app.route('/editarDatosEncuesta/<string:id_e>')
@login_required
def editar(id_e):
    conn = get_dbconnection()                       #Conexión a la base de datos
    #Seleccionar titulo de la encuesta
    cur = conn.cursor()
    sqlquery = "SELECT * from encuesta where encuesta.id_e = \'" + id_e + "\';"
    cur.execute(sqlquery)
    row = cur.fetchall()            #Acceso a los datos de la encuesta
    cur.close()                     #Se cierra el cursor
    cur = conn.cursor()             #Se reabre el cursor
    datosEncuesta = []
    for r in row:                          #Transformamos lista de tuplas a lista.
        datosEncuesta.append( r[0] )
        datosEncuesta.append( r[1] )
        datosEncuesta.append( r[2] )
        datosEncuesta.append( r[3] )
        datosEncuesta.append( r[4] )
        datosEncuesta.append( r[5] )
    return render_template('editar_datos_encuesta.html',datosEncuesta=datosEncuesta)

@app.route('/guardarDatosEncuesta/<string:id_e>',methods=['POST'])
@login_required
def guardarDatos(id_e):
    datos = []
    if request.method == 'POST':
        f = request.form
        for key in f.keys():
            for value in f.getlist(key):
                datos.append(value)
        print (datos)
        conn = get_dbconnection()
        cur = conn.cursor()
        cur.execute("UPDATE encuesta SET titulo=%s,f_ini=%s,f_exp=%s,descripcion=%s WHERE id_e=%s",(datos[1],datos[2],datos[3],datos[4],id_e))
        conn.commit()         
        cur.close()
        conn.close()
    return redirect(url_for('listaE'))    




#Código Franco: Lista de Respuestas--------------------------------------------------------------------------
@app.route('/encuesta/<string:id_e>/respuestas')    #Url con la lista, tiene la id de encuesta en la url
@login_required
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

    graficos = []
    for pregunta in preguntas:
        labels = []
        sizes = []
        for alternativa in alternativas:
            if alternativa[1] == pregunta[0]:
                labels.append(alternativa[2])
                sizes.append(alternativa[3])
        data = getPlot(labels,sizes)
        graficos.append(data)

    cur.close()
    conn.close()
    return render_template('respuestas.html', title=title, preguntas=preguntas, graficos=graficos)
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