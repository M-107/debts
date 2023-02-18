from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)


class User(db.Model):
    todo = "TODO"


@app.route('/', methods=['GET'])
def index():
    return 'TODO'


@app.route('/user/<name>/', methods=['GET'])
def show_user(name):
    return 'TODO'


@app.route('/add/', methods=['POST'])
def add_user():
    return 'TODO'


@app.route('/transaction/', methods=['POST'])
def add_transaction(creditor, debtor, value):
    return 'TODO'
