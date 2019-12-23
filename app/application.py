from flask import Flask,render_template,request,redirect,url_for,session,copy_current_request_context,flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length, EqualTo
from flask_session import Session
import os
from app.class_orm import db,User,Result,Submission
import time
from datetime import datetime, timedelta
from werkzeug import generate_password_hash,check_password_hash
import threading
import re
import sys
from app.qnEvaluate import score
from flask_socketio import SocketIO, emit
import decimal 

sys.path.append('../evaluation')

app = Flask(__name__,template_folder='./templates', static_folder='./static')
app.config['SECRET_KEY'] = "HAVOCRULEZ"
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.secret_key = 'Thisisnottobesharedtoanyone'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)

ENV = 'PROD'
if ENV == 'dev' :
	app.debug = True
	app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
else :
	app.debug = False
	app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://ofkyawpdjvlppl:e98959750f19e6517d4e8eabf5710d40bb4f7d5c1cb7b3ad0e645efee910acf3@ec2-174-129-234-111.compute-1.amazonaws.com:5432/dduv1ph7hquc21'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
Session(app)
socketio = SocketIO(app)

class LoginForm(FlaskForm) :
	username = StringField('username',validators = [InputRequired(), Length(min = 4,max = 20,message="Username must be between 4 and 20 characters")])
	password = PasswordField('password',validators = [InputRequired(), Length(min = 6,max = 30,message="Passowrd must be between 6 and 30 characters")])

class SignupForm(FlaskForm) :
	username = StringField('username',validators = [InputRequired(), Length(min = 4,max = 20,message='Username must be between 4 and 20 characters')])
	password = PasswordField('password',validators = [InputRequired(), Length(min = 6,max = 30,message='Password must be between 6 and 30 characters'), EqualTo('confirm_password', message='Passwords must match')])
	confirm_password = PasswordField('confirm_password',validators = [InputRequired(), Length(min = 6,max = 30,message='Password must be between 6 and 30 characters')])
	email = StringField('email',validators = [Email(message='Not a valid Email Address'),Length(max = 50,message='Email must atmost 50 characters')])
	name = StringField('name',validators = [Length(min = 1,max = 50,message='Name must be between 1 and 50 characters')])
	shaastraID = StringField('shaastraID',validators = [InputRequired(), Length(max = 25,message='Shaastra ID must be atmost 25 characters')])
	contact = StringField('contact',validators = [Length(max = 20,message='Contact Number must be atmost 20 characters')])

register_url = '/shaastrareg:havocrulez'

pno = 0

@socketio.on('disconnect')
def disconnect_user():
	if 'userid' in session :
		usr = User.query.filter_by(id = session['userid']).first()
		if 'remTime' in request.form :
			rem_time = request.form.get('remTime')
			usr.rem_time = rem_time
		usr.done = True
		db.session.commit()
	session.pop('userid', None)
	session.pop('username',None)
	session.pop('time',None)

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "public, max-age=0, no-cache, no-store, must-revalidate, post-check=0, pre-check=0, max-stale=0"
    r.headers["Vary"] = "*"
    r.headers["Expires"] = "Mon, 26 Jul 1997 05:00:00 GMT"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    return r

@app.route('/',methods=['GET'])
def index() :
	return redirect('/login')

@app.route('/login',methods=['GET','POST'])
def login() :
	try :
		session['userid'] 
	except KeyError :
		form = LoginForm(request.form);

		error = None
		if (request.method == 'POST' and form.validate_on_submit()) :
			user = User.query.filter_by(username = form.username.data).first()
			if user is not None and user.done == True :
				error = "Already Completed the Contest"
			elif user is not None and check_password_hash(user.password,form.password.data) :
				session.modified = True
				session.permanent = True
				app.permanent_session_lifetime = timedelta(hours = 2)
				session['username'] = user.username
				session['userid'] = user.id
				session['time'] = time.time()
				user.done = True;
				return redirect('/dashboard')
			else :
				error = 'Username or Password Incorrect'

		if bool(form.errors) :
			error = form.errors[list(form.errors.keys())[0]][0]
			print(error)

		return render_template('login.html',form = form,error = error)

	return redirect('/dashboard')

@app.route('/dashboard',methods=['GET','POST'])
def dashboard() :
	try :
		session['userid'] 
	except KeyError :
		return redirect('/login')

	if (request.method == 'POST' and ('quit' in request.form or 'remTime' in request.form)) :
		usr = User.query.filter_by(id = session['userid']).first()
		usr.done = True
		usr.rem_time = request.form.get('remTime')
		db.session.commit()
		session.pop('userid',None)
		session.pop('username',None)
		session.pop('time',None)
		return redirect('/login')

	elif (request.method == 'POST' and 'code' in request.form) :
		if Result.query.filter_by(userid = session['userid']).count() == 0 :
			res = Result(userid = session['userid'])
			db.session.add(res)
			db.session.commit()
		CODE = request.form.get('code')
		qn = str(request.form.get('question-select'))

		@copy_current_request_context
		def evaluate(code,qn,init_time) :
			global pno
			qn_no = str(re.sub('[^0-9]+',"",str(qn)))
			res = score(code,qn_no,str(pno))
			currRes = Result.query.filter_by(userid = session['userid']).first()
			if (res == 'CORRECT ANSWER') :
				if (qn == 'QN1') :
					if currRes.q1s == 100 :
						currRes.q1t = min([currRes.q1t,init_time])
					elif currRes.q1s == None or currRes.q1s < 100 :
						currRes.q1s = 100
						currRes.q1t = init_time
				elif (qn == 'QN2') :
					if currRes.q2s == 100 :
						currRes.q2t = min([currRes.q2t,init_time])
					elif currRes.q2s == None or currRes.q2s < 100 :
						currRes.q2s = 100
						currRes.q2t = init_time
				elif (qn == 'QN3') :
					if currRes.q3s == 100 :
						currRes.q3t = min([currRes.q3t,init_time])
					elif currRes.q3s == None or currRes.q3s < 100 :
						currRes.q3s = 100
						currRes.q3t = init_time
				elif (qn == 'QN4') :
					if currRes.q4s == 100 :
						currRes.q4t = min([currRes.q4t,init_time])
					elif currRes.q4s == None or currRes.q4s < 100 :
						currRes.q4s = 100
						currRes.q4t = init_time
				elif (qn == 'QN5') :
					if currRes.q5s == 100 :
						currRes.q5t = min([currRes.q5t,init_time])
					elif currRes.q5s == None or currRes.q5s < 100 :
						currRes.q5s = 100
						currRes.q5t = init_time
				submis = Submission(userid = session['userid'],mark = 100,message = res,timeofs = init_time,qnno = int(qn_no))

			else :
				if (qn == 'QN1') :
					currRes.q1s = currRes.q1s if currRes.q1s is not None else 0
				elif (qn == 'QN2') :
					currRes.q2s = currRes.q2s if currRes.q2s is not None else 0
				elif (qn == 'QN3') :
					currRes.q3s = currRes.q3s if currRes.q3s is not None else 0
				elif (qn == 'QN4') :
					currRes.q4s = currRes.q4s if currRes.q4s is not None else 0
				elif (qn == 'QN5') :
					currRes.q5s = currRes.q5s if currRes.q5s is not None else 0
				submis = Submission(userid = session['userid'],mark = 0,message = res,timeofs = init_time,qnno = int(qn_no))

			db.session.add(submis)

			scorel = [currRes.q1s,currRes.q2s,currRes.q3s,currRes.q4s,currRes.q5s]
			timel = [currRes.q1t,currRes.q2t,currRes.q3t,currRes.q4t,currRes.q5t]
			pno += 1
			currRes.tot_score = sum([e for e in scorel if e is not None])
			currRes.tot_time = sum([decimal.Decimal(e) for e in timel if e is not None])

			db.session.commit()


		threading.Thread(target = evaluate,args = (CODE,qn,time.time()-session['time'])).start()
		flash('Solution Submitted Successfully')
		return redirect('/dashboard')

	rem_time = User.query.filter_by(id = session['userid']).first().rem_time;
	if rem_time > 0 :
		return render_template('index.html',name = session['username'],rem_time = rem_time)
	else :
		usr = User.query.filter_by(id = session['userid']).first()
		usr.done = True
		db.session.commit()
		session.pop('userid',None)
		session.pop('username',None)
		session.pop('time',None)
		return redirect('/login')

@app.route(register_url,methods=['GET','POST'])
def register() :
	try :
		session['userid'] 
	except KeyError :
		form = SignupForm(request.form)

		if (request.method == 'POST' and form.validate_on_submit()) :
			if User.query.filter_by(username = form.username.data).count() == 0 :
				new_user = User(done = False,rem_time = 5400,username = form.username.data,password = generate_password_hash(form.confirm_password.data),email = form.email.data,shaastraID = form.shaastraID.data,name = form.name.data,contact = form.contact.data)
				db.session.add(new_user)
				db.session.commit() 
			return '<h1>' + 'Successfully Registered Contestant' + '</h1>'

		error = None
		if bool(form.errors) :
			error = form.errors[list(form.errors.keys())[0]][0]
			print(form.errors)

		return render_template('register.html',form = form,error = error)

	return redirect('/dashboard')

@app.route('/standings')
def standings() :
	res = Result.query.order_by(Result.tot_score.desc(),Result.tot_time).all()
	return render_template('standings.html',results = res)

@app.route('/submissions')
def submissions() :
	try :
		session['userid'] 
	except KeyError :
		return redirect('/login')
	usr = User.query.filter_by(id = session['userid']).first()
	subs = usr.submission
	return render_template('submissions.html',name = session['username'],submissions = subs,to_time = time.strftime,to_ttuple = time.gmtime)

if __name__ == '__main__' :
	app.run()
