from flask import Flask,flash,render_template, redirect, url_for, request
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail, Message 
import secrets
from flask_login import LoginManager, login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from app.models.ModelUser import ModelUser
from app.models.entities.User import User
import psycopg2
import hashlib
#Para los gráficos
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from app import forms

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
    empty = [i for i in range(len(sizes)) if sizes[i] == 0]
    for i in range(len(sizes)):
        if sizes[i] == 0:
    #        empty.append(labels[i])
    #        del labels[i]
    #        del sizes[i]
             sizes[i] = 1
    labels = [x for i,x in enumerate(labels) if i not in empty]
    sizes = [x for i,x in enumerate(sizes) if i not in empty]
    if len(labels) > 0:
        fig, ax = plt.subplots()
        fig.set_size_inches(8, 3)
        fig.subplots_adjust(left=0.2,wspace = 0.2)
        patches, texts, autotexts = ax.pie(sizes, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  
        plt.tight_layout()
        plt.legend(labels,bbox_to_anchor=(1,0.5), loc="center right", fontsize=10, 
           bbox_transform=plt.gcf().transFigure)
        plt.subplots_adjust(left=0.0, bottom=0.1, right=0.45)
        #Guardar archivo en buffer
        buf = BytesIO()
        fig.savefig(buf, format="png")
        #Imagen a imprimir en html
        data = base64.b64encode(buf.getbuffer()).decode("ascii")
    else:
        data = None
    return data

def crearUsers():   #Función para insertar usuarios escritos en el archivo "users"
    with open('app/users') as file: #Abrir archivo "users"
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
    # descripcion='Veamos si funca'
    # id='encuesta_2'
    conn = get_dbconnection() 
    cur = conn.cursor()
    # update encuesta set descripcion='descripcion de prueba' WHERE id_e='id5';
    #Borrando en "cascada inversa"
    cur.execute( "DELETE FROM respondido WHERE id_e = %s", (id,) )
    sqlquery = "DELETE FROM encuesta WHERE id_e=\'" + id + "\';"
    cur.execute(sqlquery)
    conn.commit()
    cur.close()
   
    conn.close()  

app = Flask(__name__)
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'alvaro.castillo.rifo@gmail.com'
app.config['MAIL_PASSWORD'] = 'isfiwsphwejadstk'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['SECRET_KEY'] = secrets.token_hex(16)
URL = "localhost:5002"
csrf = CSRFProtect()
csrf.init_app(app)
mail = Mail(app)

login_manager_app = LoginManager(app)
@login_manager_app.user_loader
def load_user(id):
    return ModelUser.get_by_id(get_dbconnection(),id)

from app import login_views
def status_401(error):
    return redirect(url_for('login'))
app.register_error_handler(401,status_401)

from app import mail_views
from app import admin_views
from app import answer_views