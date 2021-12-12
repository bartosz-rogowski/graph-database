from flask import Flask
from py2neo import Graph, Node, Relationship
import pandas as pd
from numpy import isnan
import networkx as nx
from matplotlib.pyplot import figure
from datetime import date

app = Flask(__name__)
# app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = Graph("neo4j+s://8d5ae205.databases.neo4j.io",
	auth = ("neo4j", "URtjTjSqnpB2FoztE8tYDhU3ujIGy8WAvoAMZfrU9eE"))

from mysite import routes