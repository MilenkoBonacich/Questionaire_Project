from app import app, get_dbconnection, render_template, request

#Código franco: Formulario para enviar respuesta------------------------------------------------------------------
@app.route('/responder')    #Url con la lista, tiene la id de encuesta en la url
def responder():
    conn = get_dbconnection()                       #Conexión a la base de datos
    
    cur = conn.cursor()
    sqlquery = "select id_e,respondido from respondido where hash = %s;"
    emailhash = request.args.get('id_r')
    cur.execute(sqlquery, (emailhash,))
    row = cur.fetchone()
    if row is None:
        return "<h1>Encuesta no encontrada :(</h1>"
    else:
        if row[1] == True:
            return return "<h1>Ya respondiste esta encuesta, gracias por tu respuesta!</h1>"
    id_e = row[0]

    #Seleccionar titulo de la encuesta
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
