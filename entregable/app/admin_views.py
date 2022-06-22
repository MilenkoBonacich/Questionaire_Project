from app import app, login_required, render_template, request,  redirect, url_for
from app import Message, mail
from app import get_dbconnection, insertDescripcion, getPlot, eliminarEncuesta
#----------------------------------- Manejo Página principal Public ---------------------------------------

@app.route("/")
def principal():
    return render_template("ingreso.html")

#----------------------------------- Manejo Página principal Admin ---------------------------------------
@app.route("/index")
@login_required
def pprincipal():
    return render_template("principal.html")

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
