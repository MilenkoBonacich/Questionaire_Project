from flask import Flask
from flask_mail import Mail, Message 

app = Flask(__name__)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'alvaro.castillo.rifo@gmail.com'
app.config['MAIL_PASSWORD'] = 'isfiwsphwejadstk'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)




@app.route("/")
def hello():
  msg = Message('flaskMail', sender =   'alvaro.castillo.rifo@gmail.com', recipients = ['franico_c@hotmail.com','fcarrion2018@udec.cl','fcarrion2018@inf.ude.cl'])
  msg.body = "aqui segunda prueba"
  mail.send(msg)
  return "Message sent!"