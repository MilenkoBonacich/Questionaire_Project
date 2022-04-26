# from crypt import methods
# from sqlite3 import Row
# from turtle import title
from crypt import methods
from multiprocessing import context
from xml.etree.ElementTree import Comment
from flask import Flask, render_template, request
import psycopg2

app = Flask(__name__)

# def get_dbconnection():
#     PSQL_HOST = "ec2-52-201-124-168.compute-1.amazonaws.com"
#     PSQL_PORT = "5432"
#     PSQL_USER = "hppcxweyblynah"
#     PSQL_PASS = "e4dbaf0502a56b15b4a64151940508613171a9e287817e5a4417d292fa8eb5ec"
#     PSQL_DB = "de3skgdka01pk8"
#     connstr = "host=%s port=%s user=%s password=%s dbname=%s" % (PSQL_HOST, PSQL_PORT, PSQL_USER, PSQL_PASS, PSQL_DB)
#     conn = psycopg2.connect(connstr)
#     return conn


@app.route("/")
def hello_world():
    return render_template("index.html")


@app.route("/createE")
def createE():
    return render_template("createE.html")

@app.route("/watchE", methods=['GET','POST'])
def watchE():
    if request.method == 'POST':
        seleccion= request.form.get('prev')
        return render_template("watchE.html",titulos=seleccion)
        # comment_form = forms.CommentForm(request.form)
        # print(comment_form)
    else:
        titulos={"Encuesta1","Encuesta2","Encuesta3"}
        return render_template("watchE.html",titulos=titulos)

@app.route("/agreeE")
def agreeE():
    return render_template("agreeE.html")

# @app.route("/login")
# def create():
#     return render_template("login.html")

# # @app.route("/watchE/previewE")
# # def previewE():
# #     return render_template("previewE.html")

@app.route("/previewE/<param>/")
def preview(param):
   
    # titulo="Encuesta 82"
    npreguntas=["Le gusta el queso?","Come flan?","Va al baño seguido?","LLora por las noches?","Juega lolcito?"]
    alter1=["si","no"]
    # alter2={"si","no"}
    context = {
        'titulo' : '{}'.format(param),
        'npreguntas' : npreguntas,
        'alter1' : alter1,
    }
    return render_template('previewE.html',**context)

if __name__=="__main__":
        app.run(debug=True)