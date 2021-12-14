from flask import render_template, url_for, flash, redirect, Response, request
from mysite import app
from mysite.db_functions import *
from mysite.forms import InsertPersonForm, FindRelationsForm
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
	df = get_dataframe_with_nodes()
	options = [
		(f"{df.loc[i].fname},{df.loc[i].lname},{df.loc[i].born}", 
		f"{df.loc[i].fname} {df.loc[i].lname}, born in {df.loc[i].born}") 
		for i in range(len(df))
	]
	form = InsertPersonForm()
	if request.method == "POST":
		if form.validate_on_submit():
			print(request.form)
			person = f"{request.form['first_name']},{request.form['last_name']},{request.form['year_of_birth']}"
			if person in [p[0] for p in options]:
				person = person.split(',')
				flash(f"{person[0]} {person[1]} born in {person[2]} is already in the databse.", 'warning')
				return render_template('insert_person.html', 
					title='Genealogical Tree / Insert person', 
					form=form,
					options=options
				)
			elif request.form['parent1'] == request.form['parent2'] and \
				(request.form['parent1'] or request.form['parent2']):
				person = request.form['parent1'].split(',')
				flash(f"You cannot choose {person[0]} {person[1]} as both parents.", 'warning')
				return render_template('insert_person.html', 
					title='Genealogical Tree / Insert person', 
					form=form,
					options=options
				)
			elif request.form['spouse'] and \
				(request.form['parent1'] == request.form['spouse'] or \
					request.form['parent2'] == request.form['spouse']):
					person = request.form['spouse'].split(',')
					flash(f"You cannot choose {person[0]} {person[1]} as both parent and spouse.", 'warning')
					return render_template('insert_person.html', 
						title='Genealogical Tree / Insert person', 
						form=form,
						options=options
					)
			flash(f"Person {form.first_name.data} {form.last_name.data} " + \
				"has been successfully inserted to database.", 'success')
			return redirect(url_for('home'))
	return render_template('insert_person.html', 
		title='Genealogical Tree / Insert person', 
		form=form,
		options=options
	)

@app.route("/find_relations", methods=['GET', 'POST'])
def find_relations():
	form = FindRelationsForm()
	df = get_dataframe_with_nodes()
	options = [
		(f"{df.loc[i].fname},{df.loc[i].lname},{df.loc[i].born}", 
		f"{df.loc[i].fname} {df.loc[i].lname}, born in {df.loc[i].born}") 
		for i in range(len(df))
	]
	if request.method == "POST":
		if request.form['person1'] == request.form['person2'] and \
			(request.form['person1'] or request.form['person2']):
			flash(f"You cannot choose the same person.", 'warning')
			return render_template('find_relations.html', 
				title='Genealogical Tree / Find relations',
				form=form,
				options=options,
				results=None
			)
		elif not request.form['person1'] or not request.form['person2']:
			flash(f"You have to choose two different people.", 'warning')
			return render_template('find_relations.html', 
				title='Genealogical Tree / Find relations',
				form=form,
				options=options,
				results=None
			)

		try:
			person1 = request.form['person1'].split(',')
			person1 = {"fname": person1[0], "lname": person1[1], "born": int(person1[2])}
			person2 = request.form['person2'].split(',')
			person2 = {"fname": person2[0], "lname": person2[1], "born": int(person2[2])}
			return render_template('find_relations.html', 
				title='Genealogical Tree / Find relations',
				form=form,
				options=options,
				results=find_connections(person1, person2)
			)
		except Exception as e:
			print("Something went wrong", e)
	return render_template('find_relations.html', 
		title='Genealogical Tree / Find relations',
		form=form,
		options=options,
		results=None
	)