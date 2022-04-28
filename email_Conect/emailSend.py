from flask import Flask
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



@app.route("/")
def hello():
  conn = get_dbconnection()
  cur = conn.cursor()
  sqlquery = "select id from email;"
  cur.execute(sqlquery)
  rows = cur.fetchall()
  receptores = []
  for r in rows:
    receptores.append(r[0])
  print(receptores)

  cur.close()
  conn.close()
  msg = Message('Prueba-Encuesta', sender =   'alvaro.castillo.rifo@gmail.com', recipients = receptores)
  msg.body = "Hola prueba enviando a todos los correos!"
  mail.send(msg)
  return "Message sent!"