from flask import Flask,render_template,jsonify,abort,request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

import enum
import requests 
import re
import json
from date_validate import *
app = Flask(__name__)


def is_present_areanumber(num):
	f=open("AreaNameEnum.csv","r")
	H={}
	i=0
	for line in f:
		if i==0:			# first line heading of the attribute
			i=i+1
		else:
			l=line.split(',')	#values of the place in integer
			H[int(l[0])]=int(l[0])
	f.close()
	return (num in H)
	
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test1.db'
db = SQLAlchemy(app)
db.create_all()

class User(db.Model):
	username = db.Column(db.String, unique=True, nullable=False, primary_key=True)
	password = db.Column(db.String(40),nullable=False)
	
	def __repr__(self):
		return "\n{username : %s , password : %s}" % (self.username,self.password)

class Ride(db.Model):
	r_id = db.Column(db.Integer, primary_key=True)
	time= db.Column(db.String,nullable=False)
	src = db.Column(db.Integer,nullable=False)
	dest = db.Column(db.Integer,nullable=False)
	created_by = db.Column(db.String, nullable=False)
	
	def __repr__(self):
		return '\n{"rideID": %d ,"username": %s, "timestamp" : %s}' % (self.r_id,self.created_by,self.time)

class ride_user(db.Model):
	
	r_id = db.Column(db.Integer, nullable=False,primary_key=True)
	username = db.Column(db.String, nullable=False,primary_key=True)


	def __repr__(self):
		return "\n{RideId : %d , User : %s}" % (self.r_id,self.username)

@app.route("/api/v1/users",methods=["PUT"])
def adduser():
	
	if request.method == "PUT":
		try:
			uname = request.get_json()["username"]
			passwd = request.get_json()["password"]
		except:
			return {},400
		flag = User.query.filter_by(username=uname).first()
		if(flag is not None):
			return jsonify({"flag":"user exists"}),400
		if(re.match(r'^[0-9a-fA-F]{40}$',passwd) is None):
			return jsonify({}),400

		"""r = requests.post("http://3.233.19.138/write/adduser",json = request.get_json())
		return jsonify(r.json())"""
		db.session.add(User(username=request.get_json()["username"],password=request.get_json()["password"]))
		db.session.commit()
		return {},201

	else:
		return {},405

		
	

#I wouldn't allow to delete user who has created atleast 1 ride.
@app.route("/api/v1/users/<uname>",methods=["DELETE"])
def removeuser(uname):
	if request.method == "DELETE":
		
		#you cann't delete the guy who has created the ride.
		rflag = Ride.query.filter_by(created_by=uname).first()
		
		uflag = User.query.filter_by(username=uname).first()
		if rflag is not None or uflag is None:
			return jsonify({}),400

		db.session.delete(uflag)
		ride_user.query.filter_by(username=uname).delete()
		db.session.commit()
		
		return jsonify({}),200
			
	else:
		return {},405
#6,5,7th
#add user to current RideID
@app.route("/api/v1/rides/<rideId>",methods=["POST","GET","DELETE"])
def Ridelistings(rideId):
	#Join an existing ride
	if request.method == "POST":
		flag = Ride.query.filter_by(r_id=rideId).first()
		uflag= User.query.filter_by(username=request.get_json()["username"]).first()
		
		does_exists = ride_user.query.filter(ride_user.r_id==rideId,ride_user.username==request.get_json()["username"]).first()
		
		if flag is None or uflag is None or does_exists is not None:
			return {},400
		else:
			shared = ride_user(r_id = rideId , username = request.get_json()["username"])
			db.session.add(shared)
			db.session.commit()
			return {},200

	elif request.method == "DELETE":

		try:
			flag = Ride.query.filter_by(r_id=rideId).first()
			if flag is None:
				return {},400
			else:
				db.session.delete(flag)
				ride_user.query.filter_by(r_id=rideId).delete()
				db.session.commit()
				return {},200
		except:
			return {},500

	#List all the details of a given ride
	elif request.method == "GET":
		try:
			flag = Ride.query.filter_by(r_id=rideId).first()
			if flag is None:
				return {},400
			r = db.session.execute('select r_id,created_by,time,src,dest from Ride where r_id = {}'.format(rideId))
			d = {}
			for i in r:
				d["rideId"] = i[0]
				d["created_by"]=i[1]
				d["Timestamp"]=i[2]
				d["source"]=i[3]
				d["destination"]=i[4]
		
		
			res = db.session.execute('select username from ride_user where r_id = {}'.format(rideId))
			l = []		
			for i in res:
				l.append(i[0])
			d["users"]=l
			return jsonify(d),200	
		except KeyError:
			return {},400
		except:
			return {},500	

	else:
		return {},405


#3 and 4th
@app.route("/api/v1/rides",methods=["POST","GET"])
def rides():
	#Create a new ride
	try:
		if request.method == "POST":
			uname = request.get_json()["created_by"]
			flag =  User.query.filter_by(username=uname).first()

			if flag is None:
				return jsonify({"flag":"user doesnt exist"}),400

			# use enum to check !!
			src =  int(request.get_json()["source"])
			dest =  int(request.get_json()["destination"])
			t=str(request.get_json()["timestamp"])
			res=date_and_time_validate(t)
			print(res)
			if(res!=True): #either date or time is in invalid format
				return jsonify({"flag":"date or time invalid"}),400
			if ((is_present_areanumber(src)) and (is_present_areanumber(dest)) and (src != dest )):
				"""r = requests.post("http://3.233.19.138/write/newride",json = request.get_json())
				if r.text == "ok":

					return {"flag":"added"},200
				else: 
					return {"flag":"not added"},500"""
				r = Ride(src=request.get_json()["source"],dest=request.get_json()["destination"],created_by=request.get_json()["created_by"],time=t)
				db.session.add(r)
				db.session.commit()
				return {"flag":"added"},201
				
			else:
				return jsonify({"flag":"invalid input"}),400

		#List all upcoming rides for a given source and destination
		elif request.method == "GET":
			try:
				tm=FormatTheDate(str(datetime.datetime.now()))
				src = int(request.args.get("source"))
				dest = int(request.args.get("destination"))
				if (( is_present_areanumber(src) ) and ( is_present_areanumber(dest)) and (src != dest )):
					query = db.session.execute('select r_id,created_by,time from Ride where src={} and dest={}'.format(src,dest))
					l = []
					for row in query:
						d = {}
						d["rideID"]=row[0]
						d["username"]=row[1]
						if(isupcoming(tm,row[2])):	#only if the ride is upcoming
							d["time"]=row[2]	#insert it into the res list
							l.append(d)
					if len(l)==0:
						return {},204
					else:
						return jsonify(l),200
				else:
					return jsonify({"flag":"either is not integer"}),400
			except KeyError:
				return {},400
			except:
				return {},500

		else:
			return {},405
	except Exception as e:
		print(e)
		return {},500
		


@app.errorhandler(404)
def error():
	return {},404
@app.route("/write/<name>",methods=["POST"])
def write(name):
	
	if (name == 'adduser'):
		try:
			db.session.add(User(username=request.get_json()["username"],password=request.get_json()["password"]))
			db.session.commit()
			return {},200
		except:
			return {},500
	elif (name == 'newride'):
		try:
			r = Ride(src=request.get_json()["source"],dest=request.get_json()["destination"],created_by=request.get_json()["created_by"],time=request.get_json()["timestamp"])
			db.session.add(r)
			db.session.commit()
	
			return "ok"
		except:
			return "!ok"	
	else:
		return None

@app.route("/view/<name>",methods=["POST"])
def view(name):
	
	if name == 'ridelist':
		src = request.get_json()["src"]
		dest = request.get_json()["dest"]
		
		return 
	else:
		return "couldn't"


""" ISSUES
0.validate inupt time first
1. format to correct datetime
2. "List all upcoming rides for a given source and destination " this needs to be passed to read api !
 
3.	Change the primary key for Ride Users
4.	Things that might happen when a user is deleted
	(a) On delete whether a ride creator is deleted then?
	(b) On delete if a ride user who joined a ride is deleted then?
	(c) On deleted should I cascade and remove entry from all tables where user appears?
"""




if __name__== '__main__':
	
	app.debug=True
	app.run()

