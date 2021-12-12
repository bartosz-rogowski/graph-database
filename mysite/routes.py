from flask import render_template, url_for, flash, redirect
from mysite import app

@app.route("/")
@app.route("/home")
def home():
	# return render_template('home.html', posts=posts)
	return "<h1>Home</h1>"

@app.route("/about")
def about():
	# return render_template('about.html', title='About')
	return "<h1>About</h1>"

