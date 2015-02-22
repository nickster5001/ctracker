from flask.ext.wtf import Form
from wtforms import StringField, BooleanField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired

class LoginForm(Form):
    openid = StringField('openid', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)
    
class Search(Form):
	search = StringField('search', validators=[DataRequired()])

class AddClient(Form):
	fname = StringField('fname', validators=[DataRequired('First Name Required')])
	lname = StringField('lname', validators=[DataRequired('Last Name Required')])
	dob = StringField('dob')
	phone = StringField('phone')

class AddIfa(Form):
	duedate = StringField('duedate',validators=[DataRequired('Due Date Required')])
	description = StringField('description',validators=[DataRequired('Description Required')])


#class AddClient(Form):
#	fname = StringField('fname', validators=[DataRequired()])
#	lname = StringField('lname', validators=[DataRequired()])
#	phone = StringField('phone', validators=[DataRequired()])
#	dob = 
