from flask import Flask
from py2neo import Graph, Node, Relationship
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
URI = os.getenv("DB_URI")
LOGIN = os.getenv("DB_LOGIN")
PASSWORD = os.getenv("DB_PASSWORD")
db = Graph(
	URI,
	auth=(LOGIN, PASSWORD),
)

from mysite import routes
