from flask import render_template, redirect
from flask import Flask, request, url_for
from app import app
from .forms import LoginForm
from .forms import Search
from .forms import AddClient
from .forms import AddIfa
from .models import clients, ifa, deleted_ifa
from .secrets import *
from flask.ext.login import login_user, logout_user, current_user, login_required
import MySQLdb
db = MySQLdb.connect(host="localhost", user=USER, passwd=PASSWORD, db="nickdb1")
cursor = db.cursor()
#login_manager = LoginManager()

def redirect_url(default='index'):
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)
 
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

#@app.before_request
#def before_request():
    #g.user = "admin"
    
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
def index():
	return redirect('/ifalist?ifasearch=1')
@app.route('/viewstatus', methods=['GET', 'POST'])
def viewifa():
	status = request.args.get("status")
	status = int(status)
	if status == 1:
		num = cursor.execute("SELECT * FROM clients, ifa WHERE duedate <= DATE_ADD(now(),INTERVAL 1 MONTH) AND ifa.clients_idclients = clients.idclients ORDER BY duedate")
		query = cursor.fetchall()
		info = "Active Clients"
	if status == 2:
		num = cursor.execute("SELECT * FROM clients, ifa WHERE ifa.duedate > DATE_ADD(now(),INTERVAL 1 MONTH) AND ifa.clients_idclients = clients.idclients ORDER BY ifa.duedate")
		query = cursor.fetchall()
		info = "Stalled Clients"

	return render_template('viewstatus.html',
							title='View IFAs',
							num = num, 
							query = query,
							info = info)
	#						
	
@app.route('/searchname', methods=['GET', 'POST'])
def searchname():
	search = request.args.get("clientsearch")	
	num = cursor.execute("SELECT * FROM clients WHERE CONCAT(fname,' ',lname,' ',phone) LIKE '%%{0}%%'" .format(search))
	i = 0
	dedupe = []
	query = []
	for row in cursor:
		query.append(row)	
	return render_template('searchname.html',
							title='Search By Name',
							num = num,
							query = query)
		
@app.route('/profile', methods=['GET', 'POST'])
def profile():   
	
	
	form = AddIfa()
	clientid = request.args.get("clientid")
	if form.validate_on_submit():
		#cursor.execute("INSERT INTO ifa VALUES ('', '%(desc)s', '%(duedate)s', '%(clientid)s'", {'desc': form.description.data, 'duedate': form.duedate.data, 'clientid': clientid})
		cursor.execute("INSERT INTO ifa VALUES ('','{0}','{1}','{2}')" .format(form.description.data, form.duedate.data, clientid))
		db.commit()
	cursor.execute("SELECT fname, lname, phone, dob FROM clients WHERE idclients = {0}" .format(clientid))
	query = cursor.fetchall()
	cursor.execute("SELECT * FROM ifa, clients WHERE clients.idclients = {0} AND ifa.clients_idclients = clients.idclients ORDER BY duedate" .format(clientid))
	query2 = cursor.fetchall()
	cursor.execute("SELECT * FROM deleted_ifa, clients WHERE deleted_ifa.clients_idclients = clients.idclients AND clients.idclients = {0} ORDER BY deleted_ifa.duedate DESC" .format(clientid))
	query3 = cursor.fetchall()
	

		
	
	return render_template('profile.html',
							client = query,
							query2 = query2,
							query3 = query3,
							form = form,
							clientid = clientid)

@app.route('/ifalist', methods=['GET', 'POST'])
def ifalist():
	ifasearch = request.args.get("ifasearch")
	ifasearch = int(ifasearch)
	if ifasearch == 1:
		num = cursor.execute("SELECT * FROM ifa, clients WHERE duedate <= CURDATE() AND ifa.clients_idclients = clients.idclients ORDER BY duedate")
		timeframe = "Today"
	if ifasearch == 2:
		num = cursor.execute("SELECT * FROM ifa, clients WHERE duedate <= DATE_ADD(now(),INTERVAL 1 WEEK) AND ifa.clients_idclients = clients.idclients ORDER BY duedate")
		timeframe = "This Week"
	if ifasearch == 3:
		num = cursor.execute("SELECT * FROM ifa, clients WHERE duedate <= DATE_ADD(now(),INTERVAL 1 MONTH) AND ifa.clients_idclients = clients.idclients ORDER BY duedate")
		timeframe = "This Month"
	if ifasearch == 4:
		num = cursor.execute("SELECT * FROM deleted_ifa, clients WHERE deleted_ifa.clients_idclients = clients.idclients ORDER BY deleted_ifa.duedate DESC")
		timeframe = "The Past"
	query = cursor.fetchall()
	return render_template('ifalist.html',
							query = query,
							num = num,
							timeframe = timeframe)
                           
@app.route('/addclient', methods=['GET', 'POST'])
def addclient():
	form = AddClient()
	if form.validate_on_submit():
		cursor.execute("INSERT INTO clients VALUES ('','{0}','{1}','{2}','{3}','1')" .format(form.fname.data, form.lname.data, form.dob.data, form.phone.data))
		db.commit()
		cursor.execute("SELECT idclients FROM clients ORDER BY idclients DESC LIMIT 1")
		query = cursor.fetchall()
		query = int(query[0][0])
		query2 = query
		cursor.execute("SELECT fname, lname, phone, dob FROM clients WHERE idclients = {0}" .format(query))
		query = cursor.fetchall()
		return render_template('profile.html',
							clientid = query2,
							client = query)
	return render_template ('addclient.html',
							form=form)
		
@app.route('/editifa', methods=['GET', 'POST'])
def editifa():
	move_where = request.form["move_where"]
	idifa = request.form["idifa"]

#complete ifa
	if move_where == '1':
		cursor.execute("INSERT INTO deleted_ifa select * from ifa where idifa = {0}" .format(idifa))
		db.commit()
		cursor.execute("DELETE FROM ifa where idifa = {0}" .format(idifa))
		db.commit()
		return redirect(redirect_url())
#un-complete ifa
	elif move_where == '2':
		cursor.execute("INSERT INTO ifa select * from deleted_ifa where idifa = {0}" .format(idifa))
		db.commit()
		cursor.execute("DELETE FROM deleted_ifa where idifa = {0}" .format(idifa))
		db.commit()
		return redirect(redirect_url())
#move duedate to tmro
	elif move_where == '3':
		cursor.execute("SELECT * FROM ifa WHERE idifa = {0}" .format(idifa))
		#query is the ifa thats being moved.
		query = cursor.fetchall()	
		 #copy query into new ifa. 
		cursor.execute("INSERT INTO ifa VALUES ('', '{0}', '{1}', '{2}')" .format(query[0][1], query[0][2], query[0][3]))
		db.commit()
		#move new ifa to completed
		cursor.execute("SELECT * FROM ifa ORDER BY idifa DESC LIMIT 1")
		query = cursor.fetchall()
		cursor.execute("INSERT INTO deleted_ifa select * from ifa where idifa = {0}" .format(query[0][0]))
		db.commit()
		cursor.execute("DELETE FROM ifa where idifa = {0}" .format(query[0][0]))
		db.commit()
		#modify duedate in old ifa. 
		cursor.execute("UPDATE ifa SET duedate=DATE_ADD(now(),INTERVAL 1 day) WHERE idifa= {0}" .format(idifa))
		db.commit()
		return redirect(redirect_url())
#move duedate to + 1 week
	elif move_where == '4':
		cursor.execute("SELECT * FROM ifa WHERE idifa = {0}" .format(idifa))
		#query is the ifa thats being moved.
		query = cursor.fetchall()	
		 #copy query into new ifa. 
		cursor.execute("INSERT INTO ifa VALUES ('', '{0}', '{1}', '{2}')" .format(query[0][1], query[0][2], query[0][3]))
		db.commit()
		#move new ifa to completed
		cursor.execute("SELECT * FROM ifa ORDER BY idifa DESC LIMIT 1")
		query = cursor.fetchall()
		cursor.execute("INSERT INTO deleted_ifa select * from ifa where idifa = {0}" .format(query[0][0]))
		db.commit()
		cursor.execute("DELETE FROM ifa where idifa = {0}" .format(query[0][0]))
		db.commit()
		#modify duedate in old ifa. 
		cursor.execute("UPDATE ifa SET duedate=DATE_ADD(now(),INTERVAL 1 week) WHERE idifa= {0}" .format(idifa))
		db.commit()
		return redirect(redirect_url())		
#move duedate to + 1 month
	elif move_where == '5':
		cursor.execute("SELECT * FROM ifa WHERE idifa = {0}" .format(idifa))
		#query is the ifa thats being moved.
		query = cursor.fetchall()	
		 #copy query into new ifa. 
		cursor.execute("INSERT INTO ifa VALUES ('', '{0}', '{1}', '{2}')" .format(query[0][1], query[0][2], query[0][3]))
		db.commit()
		#move new ifa to completed
		cursor.execute("SELECT * FROM ifa ORDER BY idifa DESC LIMIT 1")
		query = cursor.fetchall()
		cursor.execute("INSERT INTO deleted_ifa select * from ifa where idifa = {0}" .format(query[0][0]))
		db.commit()
		cursor.execute("DELETE FROM ifa where idifa = {0}" .format(query[0][0]))
		db.commit()
		#modify duedate in old ifa. 
		cursor.execute("UPDATE ifa SET duedate=DATE_ADD(now(),INTERVAL 1 month) WHERE idifa= {0}" .format(idifa))
		db.commit()
		return redirect(redirect_url())			
	return render_template('ifalist.html',
							query=move_where,
							timeframe=idifa)
							
@app.route('/addifa', methods=['GET', 'POST'])
def addifa():	
	form = AddIfa()
	clientid = request.args.get("clientid")
	if form.validate_on_submit():
		cursor.execute("INSERT INTO ifa VALUES ('','{0}','{1}','{2}')" .format(form.description.data, form.duedate.data, clientid))
		db.commit()
		cursor.execute("SELECT fname, lname, phone, dob FROM clients WHERE idclients = {0}" .format(clientid))
		query = cursor.fetchall()
		return render_template('profile.html',
								form=form,
								client = query,
								clientid=clientid)
	return render_template('profile.html',
							form=form)
							#clientid=form.clientid.data)
@app.route('/login', methods=['GET', 'POST'])
def login():
#	if g.user is not None and g.user.is_authenticated():
#		return redirect(url_for('index'))
	error = None
	if request.method == 'POST':
		if request.form['username'] != 'admin' or request.form['password'] != 'admin':
			error = 'Invalid Credentials. Please try again.'
		else:
			return redirect(url_for('index'))
	return render_template('login.html', error=error)


#def login():
#    form = LoginForm()
#    if form.validate_on_submit():
#        flash('Login requested for OpenID="%s", remember_me=%s' %
#              (form.openid.data, str(form.remember_me.data)))
#        return redirect('/index')
#    return render_template('login.html', 
#                           title='Sign In',
#                          form=form,
#                           providers=app.config['OPENID_PROVIDERS'])
                           
                           
                           
                           
