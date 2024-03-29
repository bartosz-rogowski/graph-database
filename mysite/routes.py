from flask \
    import render_template, url_for, flash, redirect, Response, request
from mysite import app
from mysite.db_functions import *
from mysite.forms \
    import InsertPersonForm, FindRelationsForm, DeletePersonForm, CleanDatabaseForm
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure


@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
def home():
    form = CleanDatabaseForm()
    if request.method == "POST":
        if not 'clean_type' in request.form.keys():
            flash("You have to choose one of the clean options.", 'warning')
        else:
            if request.form['clean_type'] == 'delete':
                try:
                    delete_all()
                    flash("All data has been successfully deleted.", 'success')
                except Exception as e:
                    print("Something went wrong:", e)
                    flash("Operation failed. Try again.", 'warning')
            elif request.form['clean_type'] == 'reload':
                try:
                    delete_all()
                    add_mock_data()
                    flash("All data has been successfully reloaded.", 'success')
                except Exception as e:
                    print("Something went wrong:", e)
                    flash("Operation failed. Try again.", 'danger')
    return render_template(
        'home.html',
        title='Genealogical Tree / Home',
        form=form
    )


@app.route("/about")
def about():
    return render_template(
        'about.html',
        title='Genealogical Tree / About'
    )


@app.route("/list_all")
def list_all():
    df = get_dataframe_with_nodes()
    return render_template('list_all.html',
                           title='Genealogical Tree / List all',
                           mytable=df
                           )


@app.route("/graph.png")
def graph():
    fig = plot_graph()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)

    response = Response(output.getvalue(), mimetype='image/png')
    return response


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
                flash(f"{person[0]} {person[1]} born in {person[2]} is already in the databse.", 'danger')
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

            if request.form['spouse']:
                if not request.form['year_of_marriage']:
                    flash(f"You need to pass year of the marriage.", 'warning')
                    return render_template('insert_person.html',
                                           title='Genealogical Tree / Insert person',
                                           form=form,
                                           options=options
                                           )

            person1 = {
                "fname": form.first_name.data,
                "lname": form.first_name.data,
                "born": int(form.year_of_birth.data)
            }

            if form.year_of_death.data:
                add_person(
                    person1['fname'],
                    person1['lname'],
                    person1['born'],
                    form.year_of_death.data
                )
            else:
                add_person(
                    person1['fname'],
                    person1['lname'],
                    person1['born']
                )

            if request.form['spouse'] and request.form['year_of_marriage']:
                spouse = request.form['spouse'].split(',')
                spouse = {"fname": spouse[0], "lname": spouse[1], "born": int(spouse[2])}
                add_relationship(person1, spouse, "MARRIED",
                                 {"since": int(request.form['year_of_marriage'])}
                                 )

            if request.form['parent1']:
                parent1 = request.form['parent1'].split(',')
                parent1 = {"fname": parent1[0], "lname": parent1[1], "born": int(parent1[2])}
                add_relationship(parent1, person1, "HAS_CHILD")

            if request.form['parent2']:
                parent2 = request.form['parent2'].split(',')
                parent2 = {"fname": parent2[0], "lname": parent2[1], "born": int(parent2[2])}
                add_relationship(parent2, person1, "HAS_CHILD")

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
            results = find_connections(person1, person2)
            if not results:
                flash("There are no relations between those people.", 'info')
            return render_template('find_relations.html',
                                   title='Genealogical Tree / Find relations',
                                   form=form,
                                   options=options,
                                   results=results
                                   )
        except Exception as e:
            print("Something went wrong:", e)
    return render_template('find_relations.html',
                           title='Genealogical Tree / Find relations',
                           form=form,
                           options=options,
                           results=None
                           )


@app.route("/delete_person", methods=['GET', 'POST'])
def delete_person():
    form = DeletePersonForm()
    df = get_dataframe_with_nodes()
    options = [
        (f"{df.loc[i].fname},{df.loc[i].lname},{df.loc[i].born}",
         f"{df.loc[i].fname} {df.loc[i].lname}, born in {df.loc[i].born}")
        for i in range(len(df))
    ]
    if request.method == "POST":
        if not request.form['person1']:
            flash(f"You have to choose someone.", 'warning')
            return render_template('delete_person.html',
                                   title='Genealogical Tree / Delete person',
                                   form=form,
                                   options=options
                                   )
        else:
            try:
                person1 = request.form['person1'].split(',')
                person1 = {"fname": person1[0], "lname": person1[1], "born": int(person1[2])}
                # return render_template('find_relations.html',
                # 	title='Genealogical Tree / Find relations',
                # 	form=form,
                # 	options=options,
                # 	results=find_connections(person1, person2)
                # )
                delete(person1)
                flash("Person has been succcessfully removed.", 'success')
            except Exception as e:
                print("Something went wrong:", e)
                flash("Operation failed. Try again.", 'danger')
    return render_template('delete_person.html',
                           title='Genealogical Tree / Delete person',
                           form=form,
                           options=options
                           )
