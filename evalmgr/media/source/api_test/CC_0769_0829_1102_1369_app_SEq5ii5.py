from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restful import Resource, Api
import json
import os
import re
from constant import Area
from datetime import datetime
import requests
import ast

################################################
#Flask App
app = Flask(__name__)
basedir=os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///"+os.path.join(basedir,'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)
api=Api(app)

################################################

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String, unique=True, nullable=False)
	password = db.Column(db.String, nullable=False)

	def __init__(self,username,password):
		self.username=username
		self.password=password

class UserSchema(ma.Schema):
	class Meta:
		fields=('id','username','password')

user_schema = UserSchema()
users_schema = UserSchema(many=True)

#################################################

class Rides(db.Model):
	rideId = db.Column(db.Integer, primary_key=True)
	Created_by = db.Column(db.String, unique=False, nullable=False)
	Timestamp = db.Column(db.String)
	source = db.Column(db.Integer, nullable=False)
	destination = db.Column(db.Integer, nullable=False)

	def __init__(self,Created_by,Timestamp,source,destination):
			self.Created_by=Created_by
			self.Timestamp=Timestamp
			#self.users=[users]

			self.source=source
			self.destination=destination

class RideSchema(ma.Schema):
	class Meta:
		fields=('rideId','Created_by','Timestamp','source','destination')

ride_schema = RideSchema()
rides_schema = RideSchema(many=True)

################################################

class Other_Users(db.Model):
	i = db.Column(db.Integer, primary_key=True)
	ID = db.Column(db.Integer, unique=False,nullable=False)
	user_names= db.Column(db.String, nullable=False)

	def __init__(self,ID,user_names):
		self.ID=ID
		self.user_names=user_names

class Other_UsersSchema(ma.Schema):
	class Meta:
		fields=('ID','user_names')

other_user_schema = Other_UsersSchema()
other_users_schema = Other_UsersSchema(many=True)

###############################################
db.create_all()
#API 1 : Remaining work : Validating password
#ADD USER
@app.route("/api/v1/users",methods=["PUT"])
def adduser():
	psd=re.compile("(^[abcdefABCDEF0123456789]{40}$)")
	userToAdd=request.get_json()["username"]
	pwd=request.get_json()["password"]

	if(not(psd.match(pwd))):
		return jsonify({}), 400 #if password is not valid

	d = dict()
	d['flag'] = 1 
	d['username'] = userToAdd
	d['password'] = pwd

	w=requests.post("http://127.0.0.1:5000/api/v1/db/read", json=d)

	e =ast.literal_eval(w.text)

	if(e):
		return jsonify({}), 400
	else:
		r=requests.post("http://127.0.0.1:5000/api/v1/db/write", json=d)
		return jsonify({}), 201


#API 2 
#DELETE USER
@app.route("/api/v1/users/<username>",methods=["DELETE"])
def delete_user(username):
	d = dict()
	d['flag'] = 1
	d['username'] = username

	w=requests.post("http://127.0.0.1:5000/api/v1/db/read", json=d)

	e =ast.literal_eval(w.text)

	if(e):
		d['flag'] = 2
		r=requests.post("http://127.0.0.1:5000/api/v1/db/write", json=d)
		return jsonify({}), 201
	else:
		return jsonify({}),400

#SHOW ALL USERS {FOR REFERENCE}
@app.route("/api/v1/db/showall_users")
def show():
	all_users=User.query.all()
	re=users_schema.dump(all_users)
	return jsonify(re)

#########################################################
#API 3
#ADD RIDE
@app.route("/api/v1/rides",methods=["POST"])
def addride():
	timeptrn=re.compile("((0[1-9]|[12][0-9]|3[01])-(0[13578]|1[02])-(18|19|20)[0-9]{2})|(0[1-9]|[12][0-9]|30)-(0[469]|11)-(18|19|20)[0-9]{2}|(0[1-9]|1[0-9]|2[0-8])-(02)-(18|19|20)[0-9]{2}|29-(02)-(((18|19|20)(04|08|[2468][048]|[13579][26]))|2000) [0-5][0-9]:[0-5][0-9]:(2[0-3]|[01][0-9])")

	created_by=request.get_json()["created_by"]
	timestamp=request.get_json()["timestamp"]
	source=request.get_json()["source"]
	destination=request.get_json()["destination"]

	now1=datetime.utcnow()
	s11=now1.strftime("%d-%m-%Y:%S-%M-%H")
	d11=datetime.strptime(s11, "%d-%m-%Y:%S-%M-%H")
	s22=timestamp
	d22=datetime.strptime(s22,"%d-%m-%Y:%S-%M-%H")
	k1=str(d22-d11)
	if(k1[0]=="-"):
		return jsonify({}), 400 #if time is not valid

	s=int(source) in Area._value2member_map_
	desti=int(destination) in Area._value2member_map_

	if(not(timeptrn.match(timestamp)) or not(s) or not(desti)):
		return jsonify({}), 400 #if time is not valid

	d = dict()
	d['created_by'] = created_by
	d['timestamp'] = timestamp
	d['source'] = source
	d['destination'] = destination
	d['flag'] = 2

	w=requests.post("http://127.0.0.1:5000/api/v1/db/read", json=d)
	e =ast.literal_eval(w.text)

	if(e):
		d['flag'] = 3
		r=requests.post("http://127.0.0.1:5000/api/v1/db/write", json=d)
		return jsonify({}), 201
	else :
		return jsonify({}), 400

#API 7
#DELETE RIDE
@app.route("/api/v1/rides/<ride_id>",methods=["DELETE"])
def deleterride(ride_id):
	d=dict()
	d['flag']=3
	d['rideid']=ride_id

	w=requests.post("http://127.0.0.1:5000/api/v1/db/read", json=d)
	e=ast.literal_eval(w.text)

	if(e):
		d['flag']=4
		r=requests.post("http://127.0.0.1:5000/api/v1/db/write", json=d)
		return jsonify({}), 201
	else :
		return jsonify({}), 400

#SHOW ALL RIDES {FOR REFERENCE}
@app.route("/api/v1/db/showall")
def showall():
	all_rides=Rides.query.all()
	res=rides_schema.dump(all_rides)
	return jsonify(res)

########################################################

#API 4 : Remaining : printing format
#View ride details using source and destination
@app.route("/api/v1/rides",methods=["GET"])
def viewridesource():
	source=request.args['source']
	dest =request.args['destination']

	d=dict()
	d['source']=source
	d['destination']=dest
	d['flag']= 7

	s=int(source) in Area._value2member_map_
	desti=int(dest) in Area._value2member_map_
	# print(s)
	#print(d)
	# print(type(source))
	# print(type(dest))
	if(s and desti ):
		rr1=requests.post("http://127.0.0.1:5000/api/v1/db/read", json=d)
		r =ast.literal_eval(rr1.text)
		if(r):
			return json.dumps(r), 201
		else:
			return jsonify({}), 400
	else:
		return jsonify({}), 400


#########################################################
#API 5
#DISPLAY RIDE DETAILS
@app.route("/api/v1/rides/<ride_id>", methods=["GET"])
def viewridedetails(ride_id):
	l=[]
	d = dict()
	d['flag'] = 3 #check if rideid exists in rides db
	d['rideid'] = ride_id
	exus1=requests.post("http://127.0.0.1:5000/api/v1/db/read", json=d)
	exus =ast.literal_eval(exus1.text)
	strss=exus

	di=dict()
	di['flag'] = 4  #to get ride details
	di['rideid'] = ride_id
	ride1=requests.post("http://127.0.0.1:5000/api/v1/db/read", json=di)
	ride =ast.literal_eval(ride1.text)
	
	
	dit = dict()
	dit['flag'] =  5 #check if rideid exists in other users db
	dit['rideid'] = ride_id
	ursr1=requests.post("http://127.0.0.1:5000/api/v1/db/read", json=dit)
	ursr =ast.literal_eval(ursr1.text)
	
	dito = dict()
	dito['flag'] = 6 #copy her 8 th one
	dito['rideid'] = ride_id
	r1=requests.post("http://127.0.0.1:5000/api/v1/db/read", json=dito)
	r =r1.json()
	r2=r['val']
	

	if(r2):
		ride_to=ride_schema.jsonify(ride)
		extract=db.session.query(Rides.rideId,Rides.Created_by,Rides.Timestamp,Rides.source,Rides.destination).filter_by(rideId = ride_id).one()
		ridiss=str(extract[0])
		cbss=str(extract[1])
		tsss=str(extract[2])
		sss=str(extract[3])
		dss=str(extract[4])
		dr={"rideId":''.join(ridiss),"Created_by":''.join(cbss),"Timestamp":''.join(tsss),"source":''.join(sss),"destination":''.join(dss)}
		ride_to=json.dumps(dr)
		usrss_to=other_user_schema.jsonify(ursr)
		usr = Other_Users.query.all()
		for urs in usr:
			if(urs.ID == int(ride_id)):
				l.append(urs.user_names)
		d={"usernames":l}
		usrss_to=json.dumps(d)
		dict1ss=eval(ride_to)
		dict2ss=eval(usrss_to)
		dict3ss={**dict1ss,**dict2ss}
		reslt=json.dumps(dict3ss)
		fnss={"rideId":dict3ss.get("rideId"),"created_by":dict3ss.get("Created_by"),"users":dict3ss.get("usernames"),"timestamp":dict3ss.get("Timestamp"),"source":dict3ss.get("source"),"destination":dict3ss.get("destination")}
		reslt=json.dumps(fnss)
		return reslt, 200
	else:
		if(request.method!="GET"):
			return jsonify({}), 405
		else:
			return jsonify({}), 400





#########################################################

#API 6
#Add other users
@app.route("/api/v1/rides/<rideid>", methods=["POST"])
def add_otheruser(rideid):
	user_name=request.get_json()["username"]
	d = dict()
	d['rideid']= rideid
	d['username']=user_name
	

	d['flag'] = 1 #check if user exists
	u=requests.post("http://127.0.0.1:5000/api/v1/db/read", json=d)
	e1=ast.literal_eval(u.text)

	d['flag'] = 3 #check if ride exists
	u=requests.post("http://127.0.0.1:5000/api/v1/db/read", json=d)
	e2=ast.literal_eval(u.text)

	d['flag'] = 8 #check if the user to be added is the used who created the ride
	u=requests.post("http://127.0.0.1:5000/api/v1/db/read", json=d)
	e3=ast.literal_eval(u.text)

	d['flag'] = 9 #check if the user to be added is the used who created the ride
	u=requests.post("http://127.0.0.1:5000/api/v1/db/read", json=d)
	e4=ast.literal_eval(u.text)

	d['flag'] = 10 
	u=requests.post("http://127.0.0.1:5000/api/v1/db/read", json=d)
	e5=ast.literal_eval(u.text)


	if(e1 and e2 and e3 and e4 and e5):
		d['flag']=5
		r=requests.post("http://127.0.0.1:5000/api/v1/db/write", json=d)
		return jsonify({}), 201
	else :
		return jsonify({}), 400


#SHOW ALL OTHER USERS {JUST FOR REFERENCE}
@app.route("/api/v1/db/showall_otherusers")
def showallusers():
	all_rides=Other_Users.query.all()
	res=other_users_schema.dump(all_rides)
	return jsonify(res)



#########################################################

#write API

@app.route("/api/v1/db/write",methods=["POST","DELETE"])
def writeToDB():
	flag = request.get_json()["flag"]
	if flag == 1:  #User add
		username = request.get_json()["username"]
		password = request.get_json()["password"]
		newUser=User(username,password)
		db.session.add(newUser)
		db.session.commit()
		return jsonify({})
	elif flag == 2 : #user delete
		username = request.get_json()["username"]
		User.query.filter_by(username=username).delete()
		Other_Users.query.filter_by(user_names=username).delete()
		Rides.query.filter_by(Created_by=username).delete()
		db.session.commit()
		return jsonify({})
	elif flag == 3: #add ride
		created_by=request.get_json()["created_by"]
		timestamp=request.get_json()["timestamp"]
		source=request.get_json()["source"]
		destination=request.get_json()["destination"]
		newRide=Rides(created_by,timestamp,source,destination)
		db.session.add(newRide)
		db.session.commit()
		return jsonify({})
	elif flag == 4 : #delete ride
		rideid = request.get_json()["rideid"]
		Rides.query.filter_by(rideId=rideid).delete()
		Other_Users.query.filter_by(ID=rideid).delete()
		db.session.commit()
		print("Ride Deleted")
		return jsonify({})
	elif flag == 5 : #Add other user
		ID = request.get_json()["rideid"]
		username = request.get_json()["username"]
		new=Other_Users(ID,username)
		db.session.add(new)
		db.session.commit()
		return jsonify({})


###########################################################

#read API

@app.route("/api/v1/db/read",methods=["GET","PUT","POST","DELETE"])
def readFromDB():
	flag = request.get_json()["flag"]
	if flag == 1:  #check if username is present
		username = request.get_json()["username"]
		u=bool(User.query.filter_by(username = username).first())
		if(u):
			return "1"
		else:
			return "0"
	elif flag == 2: #check if createby is present in users db
		username = request.get_json()["created_by"]
		u=bool(User.query.filter_by(username = username).first())
		if(u):
			return "1"
		else:
			return "0"
	elif flag == 3: #check if ride is present
		rideid = request.get_json()["rideid"]
		u=bool(Rides.query.filter_by(rideId = rideid).first())
		if(u):
			return "1"
		else:
			return "0"
	elif flag == 4:
		rideid = request.get_json()["rideid"]
		ride = db.session.query(Rides.rideId, Rides.Created_by, Rides.Timestamp,Rides.source, Rides.destination).filter_by(rideId = rideid).all()
		return jsonify(ride)
	elif flag == 5:
		rideid = request.get_json()["rideid"]
		ursr= db.session.query(Other_Users.user_names).filter_by(ID = rideid).all()
		return jsonify(ursr)
	elif flag == 6:
		rideid = request.get_json()["rideid"]
		r=bool(Rides.query.filter_by(rideId = rideid).first())
		return jsonify({'val':r})	
	elif flag == 7: #source/destination - display ride details
		sourceok=request.get_json()['source']
		dest =request.get_json()['destination']
		now=datetime.utcnow()
		s1=now.strftime("%d-%m-%Y:%S-%M-%H")
		d1=datetime.strptime(s1, "%d-%m-%Y:%S-%M-%H")

		srcc = db.session.query(Rides).filter_by(source = sourceok, destination=dest).with_entities(Rides.rideId,Rides.Created_by,Rides.Timestamp).all()
		for use in srcc:
			s2=use.Timestamp
			d2=datetime.strptime(s2,"%d-%m-%Y:%S-%M-%H")
			k=str(d2-d1)
			user_data={}
			if(k[0]=="-"):
				srcc.remove(use)
		r_schema = RideSchema(many=True)
		ress= r_schema.dump(srcc)       
		return jsonify(ress)

	elif flag == 8:
		rideid=request.get_json()['rideid']
		username=request.get_json()['username']
		r=bool(Rides.query.filter_by(rideId = rideid, Created_by=username).first())
		if(r):
			return "0"
		else:
			return "1"
	elif flag ==9 :
		rideid=request.get_json()['rideid']
		username=request.get_json()['username']
		r=bool(Other_Users.query.filter_by(ID = rideid, user_names=username).first())
		if(r):
			return "0"
		else:
			return "1"
		

if __name__ == '__main__':
	app.debug=True
	app.run()
		

