from app import db



class clients(db.Model):
	idclients = db.Column(db.Integer, primary_key=True)
	fname = db.Column(db.String(45), index=True)
	lname = db.Column(db.String(45), index=True)
	phone = db.Column(db.String(10))
	dob = db.Column(db.Date, index=True)
	
	def __repr__(self):
		return '<clients %r>' % (self.lname)
	
class ifa(db.Model):
	idifa = db.Column(db.Integer, primary_key=True)
	description = db.Column(db.String(450))
	duedate = db.Column(db.Date)
	clients_idclients = db.Column(db.Integer, db.ForeignKey('user.id'))
	
	def __repr__(self):
		return '<User %r>' % (self.nickname)

class deleted_ifa(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	description = db.Column(db.String(450))
	duedate = db.Column(db.Date)
	clients_idclients = db.Column(db.Integer, db.ForeignKey('user.id'))
	
	def __repr__(self):
		return '<User %r>' % (self.nickname)
