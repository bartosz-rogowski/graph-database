from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from datetime import date

current_year = date.today().year

class InsertPersonForm(FlaskForm):
	first_name = StringField(
		'First Name*',
		validators=[DataRequired(), Length(min=2, max=30)]
	)
	last_name = StringField(
		'Last Name*',
		validators=[DataRequired(), Length(min=2, max=30)]
	)

	year_of_birth = IntegerField(
		'Year Of Birth*', 
		validators=[DataRequired(), NumberRange(min=0, max=current_year)],
		default = current_year
	)

	year_of_death = IntegerField(
		'Year Of Death',
		validators=[Optional()]
	)

	submit = SubmitField('Insert person')

class FindRelationsForm(FlaskForm):
	submit = SubmitField('Find relations')