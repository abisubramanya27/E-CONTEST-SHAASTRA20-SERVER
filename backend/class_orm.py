import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model) :
	__tablename__ = "users"
	id = db.Column(db.Integer,primary_key = True)
	username = db.Column(db.String(20),nullable = False,unique = True)
	password = db.Column(db.String,nullable = False)
	name = db.Column(db.String(50))
	contact = db.Column(db.String(20))
	shaastraID = db.Column(db.String(25),nullable = False,unique = True)
	email = db.Column(db.String(50))
	done = db.Column(db.Boolean,nullable = False)
	rem_time = db.Column(db.Integer,nullable = False)

	def __init__(self, **kwargs) :
	   	super(User, self).__init__(**kwargs)

class Result(db.Model) :
	__tablename__ = "results"
	id = db.Column(db.Integer,primary_key = True)
	userid = db.Column(db.Integer,db.ForeignKey('users.id'))
	user = db.relationship("User",backref = "result",lazy = True)
	q1s = db.Column(db.Integer)
	q2s = db.Column(db.Integer)
	q3s = db.Column(db.Integer)
	q4s = db.Column(db.Integer)
	q5s = db.Column(db.Integer)
	q1t = db.Column(db.Numeric(precision = 14,scale = 4))
	q2t = db.Column(db.Numeric(precision = 14,scale = 4))
	q3t = db.Column(db.Numeric(precision = 14,scale = 4))
	q4t = db.Column(db.Numeric(precision = 14,scale = 4))
	q5t = db.Column(db.Numeric(precision = 14,scale = 4))
	tot_score = db.Column(db.Integer)
	tot_time = db.Column(db.Numeric(precision = 14,scale = 4))

	def __init__(self, **kwargs) :
		super(Result, self).__init__(**kwargs)

class Submission(db.Model) :
	__tablename__ = "submissions"
	id = db.Column(db.Integer,primary_key = True)
	userid = db.Column(db.Integer,db.ForeignKey('users.id'))
	user = db.relationship("User",backref = "submission",lazy = True)
	qnno = db.Column(db.Integer)
	mark = db.Column(db.Integer)
	message = db.Column(db.String)
	timeofs = db.Column(db.Numeric(precision = 14,scale = 4))

	def __init__(self, **kwargs) :
		super(Submission, self).__init__(**kwargs)