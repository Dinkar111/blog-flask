from flask import Flask
import mysql.connector as mysql

app = Flask(__name__)
app.config['SECRET_KEY'] = '9841707744'

db = mysql.connect(
    host = "localhost",
    user = "root",
    passwd = "Dinku@12345",
    database = "facebok"           
)


from facebok import routes
