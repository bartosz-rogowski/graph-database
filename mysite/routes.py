from flask import render_template, url_for, flash, redirect, Response
from mysite import app
from mysite.db_functions import *
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

@app.route("/")
@app.route("/home")
def home():
	return render_template('home.html')

@app.route("/about")
def about():
	return render_template('about.html', title='About')

@app.route("/tree")
def tree():
	df = get_dataframe_with_nodes()
	return render_template('tree.html', 
		title = 'Tree',
		mytable = df
	) 

@app.route("/plot.png")
def plot_png():
	fig = plot_graph()
	output = io.BytesIO()
	FigureCanvas(fig).print_png(output)
	return Response(output.getvalue(), mimetype='image/png')