from app import app, request, flash, render_template, redirect, url_for
from app import User, ModelUser, get_dbconnection
from app import login_user, logout_user

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