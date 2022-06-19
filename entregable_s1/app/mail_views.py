from app import app, flash, render_template, redirect, url_for, request
from app import get_dbconnection, forms
from app import login_required

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