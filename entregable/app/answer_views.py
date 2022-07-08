from app import app, get_dbconnection, render_template, request, getPlot, flash

#Código franco: Formulario para enviar respuesta------------------------------------------------------------------
@app.route('/responder')    #Url con la lista, tiene la id de encuesta en la url
def responder():
    conn = get_dbconnection()                       #Conexión a la base de datos
    
    cur = conn.cursor()
    sqlquery = "select id_e,respondido from respondido where hash = %s;"    #Seleccionar id y booleano
    emailhash = request.args.get('id_r')
    cur.execute(sqlquery, (emailhash,))
    row = cur.fetchone()
    if row is None:             #Caso 1: Encuesta no existe.
        return render_template('postrespuesta.html')   
    else:                       #Caso 2: Encuesta ya fue respondida.
        if row[1] == True:
            flash('encuesta ya respondida','respondido')
            return render_template('postrespuesta.html')
                                #Caso 3: Encuesta puede responderse.
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

@app.route('/responder', methods={'POST'})
def enviar():
    conn = get_dbconnection()
    cur = conn.cursor()

    sqlquery = "select email,id_e,respondido from respondido where hash = %s;"    #Seleccionar id y booleano
    emailhash = request.args.get('id_r')
    cur.execute(sqlquery, (emailhash,))
    row = cur.fetchone()
    if row[2] == True:  #Caso: Reenvío de formulario?(No estoy seguro si esto puede suceder, pero solo por asegurarse)
            flash('encuesta ya respondida','respondido')
            return render_template('postrespuesta.html')
    email = row[0]
    id_e = row[1]
    sqlquery = """ UPDATE respondido
                    SET respondido = %s
                    WHERE email = %s AND id_e = %s """
    cur.execute(sqlquery,('1',email,id_e))

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
    flash('encuesta ya respondida','respondido')
    return render_template('postrespuesta.html')

@app.route('/encuesta/<string:id_e>/resultados')    #Url con la lista, tiene la id de encuesta en la url
def resultados(id_e):
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
    return render_template('enviar_resultados.html', title=title, preguntas=preguntas, graficos=graficos)