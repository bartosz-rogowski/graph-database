from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from datetime import date
from mysite.db_functions import get_dataframe_with_nodes

current_year = date.today().year
df = get_dataframe_with_nodes()


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

	mother = SelectField(
		'Mother',
		validators=[Optional()],
		coerce=int,
		choices = [(df.loc[i].fname, df.loc[i].fname) for i in range(len(df))]
	)

	submit = SubmitField('Insert person')