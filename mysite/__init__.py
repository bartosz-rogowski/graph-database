from flask import Flask
from py2neo import Graph, Node, Relationship


app = Flask(__name__)
app.config['SECRET_KEY'] = 'ce50bd8fbfbeb7391c109aca88e6ff16'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = Graph("neo4j+s://8d5ae205.databases.neo4j.io",
	auth = ("neo4j", "URtjTjSqnpB2FoztE8tYDhU3ujIGy8WAvoAMZfrU9eE"))

from mysite import routes