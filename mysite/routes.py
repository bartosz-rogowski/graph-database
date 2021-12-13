from flask import render_template, url_for, flash, redirect, Response
from mysite import app
from mysite.db_functions import *
from mysite.forms import InsertPersonForm
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

@app.route("/")
@app.route("/home")
def home():
	return render_template('home.html', title='Genealogical Tree / Home')

@app.route("/about")
def about():
	return render_template('about.html', title='Genealogical Tree / About')

@app.route("/tree")
def tree():
	df = get_dataframe_with_nodes()
	return render_template('tree.html', 
		title='Genealogical Tree / Tree',
		mytable=df
	) 

@app.route("/plot.png")
def plot_png():
	fig = plot_graph()
	output = io.BytesIO()
	FigureCanvas(fig).print_png(output)
	return Response(output.getvalue(), mimetype='image/png')

@app.route("/insert_person", methods=['GET', 'POST'])
def insert_person():
	form = InsertPersonForm()
	if form.validate_on_submit():
		flash(f"Person {form.first_name.data} {form.last_name.data} " + \
			"has been successfully inserted to database.", 'success')
		return redirect(url_for('home'))
	return render_template('insert_person.html', 
		title='Genealogical Tree / Insert person', 
		form=form
	)