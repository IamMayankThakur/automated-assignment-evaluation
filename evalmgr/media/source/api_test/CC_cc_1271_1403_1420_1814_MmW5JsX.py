from flask import Flask,request,jsonify,redirect, url_for, abort
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import ModelSchema
from datetime import datetime
import requests
import json
import pandas as pd

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///db.sqlite3'
db = SQLAlchemy(app)
ma=Marshmallow(app)

data=pd.read_csv("AreaNameEnum.csv")


class User(db.Model):
    username = db.Column(db.String(50),primary_key=True)
    password = db.Column(db.String(50))
	
	
class Ride(db.Model):
	id = db.Column(db.Integer,primary_key=True)   
	created_by= db.Column(db.String(50), nullable=False)
	timestamp= db.Column(db.String(50))
	source= db.Column(db.String(50))
	destination= db.Column(db.String(50))
	#users=db.relationship('Shared_user', backref="Ride", cascade="all, delete-orphan" , lazy='dynamic')
	users=db.relationship('Shared_user',cascade="all, delete-orphan" , lazy='dynamic')


class Shared_user(db.Model):
	rideid = db.Column(db.Integer, db.ForeignKey('ride.id'),nullable=False,primary_key=True)
	users=db.Column(db.String(100),nullable=False,primary_key=True)



class SharedSchema(ma.ModelSchema):
	class Meta:
		model = Shared_user


class UserSchema(ma.ModelSchema):
	class Meta:
		model = User
class RideSchema(ma.ModelSchema):
	class Meta:
		model = Ride

	
user_schema=UserSchema()
users_schema=UserSchema(many=True)

ride_schema=RideSchema()
rides_schema=RideSchema(many=True)

shared_schema=SharedSchema()
shareds_schema=SharedSchema(many=True)

#------------------------------------------------------------#
#WRITING AND READING TO DATABASE

#User
@app.route('/api/v1/write/user' , methods=["POST"])
def write():	
	username=request.get_json()['username']
	password=request.get_json()['password']
	user= User(username=username,password=password)
	db.session.add(user)
	db.session.commit()
	return ""

@app.route('/api/v1/read/user')
def read():
	user =  User.query.all()
	user_schema=UserSchema(many=True)
	output=user_schema.dump(user)
	return jsonify(output)

#------------------------------------------------------------#
#Ride
@app.route('/api/v1/write/ride' , methods=["POST"])
def write_ride():
	#rideid=request.get_json()['rideid']
	created_by=request.get_json()['created_by']
	timestamp=request.get_json()['timestamp']
	source=request.get_json()['source']
	destination=request.get_json()['destination']
	ride= Ride(created_by=created_by,timestamp=timestamp,source=source,destination=destination)
	db.session.add(ride)
	db.session.commit()
	return ""

@app.route('/api/v1/read/ride')
def read_ride():
	ride =  Ride.query.all()
	ride_schema=RideSchema(many=True)
	output=ride_schema.dump(ride)
	return jsonify(output)


#------------------------------------------------------------#
#shared User
@app.route('/api/v1/write/shared' , methods=["POST"])
def write_shared():	
	rideid=request.get_json()['rideid']
	users=request.get_json()['users']
	shared= Shared_user(rideid=rideid,users=users)
	db.session.add(shared)
	db.session.commit()
	return ""


@app.route('/api/v1/read/shared')
def read_shared():
	shared =  Shared_user.query.all()
	shareds_schem=SharedSchema(many=True)
	output=shareds_schema.dump(shared)
	return jsonify(output)



#------------------------------------------------------------#

#1) Add user (API)	 
@app.route('/api/v1/users',methods=["PUT"])
def create_user():
	with app.test_client() as client:
		response = client.get('/')
		if(response.status_code==405):
			abort (str(response.status_code))
	user={
    	'username':request.get_json()['username'],
    	'password':request.get_json()['password']
	}
	if not request.get_json() or not 'username' in request.get_json() or not 'password' in request.get_json():
		abort(400)
	if len(user['password'])<40 or not user['password'].isalnum() :
		abort(400)
	
	if(bool(User.query.filter_by(username=user["username"]).first())):
			abort(400,"username already exists")
	user_request=requests.post(request.url_root+"api/v1/write/user",json=user)
	user_request.text
	return jsonify(),201

 
#2)Remove user (API)
@app.route("/api/v1/users/<username>",methods=["DELETE"])
def remove_user(username):
	with app.test_client() as client:
		response = client.get('/')
		if(response.status_code==405):
			abort (str(response.status_code))
	users=User.query.filter_by(username=username).first()
	if users:
		db.session.delete(users)	
		db.session.commit()
		return jsonify(),200
	abort(400)



#3)Create a new ride 
@app.route("/api/v1/rides",methods=["POST"])
def create_ride():
	with app.test_client() as client:
		response = client.get('/')
		if(response.status_code==405):
			abort (str(response.status_code))
	if not request.get_json() or not 'created_by' in request.get_json() or not 'source' in request.get_json() or not 'destination' in request.get_json() or not 'timestamp' in request.get_json():
		abort(400)
	ride_username=request.get_json()['created_by']
	timestamp=request.get_json()['timestamp']
	source=request.get_json()['source']
	destination=request.get_json()['destination']

	if(bool(Ride.query.filter_by(created_by=ride_username,timestamp=timestamp,source=source,destination=destination).first())):
			return jsonify("inside")
			abort(400,"ride already exists")
	if(int(source)==int(destination)):
		abort(400)
	riders={"created_by":ride_username,"timestamp":timestamp,"source":source,"destination":destination}
	if(bool(User.query.filter_by(username=ride_username).first())):
		created=requests.post(request.url_root+"api/v1/write/ride",json=riders)
		created.text
		return jsonify(),201
	abort(400)

#4)List all upcoming rides for a given source and destination
@app.route('/api/v1/rides')
def all_rides():
	with app.test_client() as client:
		response = client.get('/')
		if(response.status_code==405):
			abort (str(response.status_code))
	ride=[]
	flag=False
	source = request.args.get('source')
	destination = request.args.get('destination')
	if(int(source)==int(destination)):
		abort(400)
	if(len(source)==0 or len(destination)==0):
		abort(400)
	if(int(source)<1 or int(source)>198) or (int(destination)<1 or int(destination)>198):
		abort(400)
	if (int(source) in data['Area No']) and (int(destination) in data['Area No']):
		upcoming=Ride.query.filter_by(source=source,destination=destination).all()
		ride_schema=RideSchema(many=True)
		output=ride_schema.dump(upcoming)
		for details in output:
			d={}
			d.update(details)
			d.pop("source")
			d.pop("destination")
			d.pop("users")
			x=d["id"]
			y=d["created_by"]
			d.pop("created_by")
			d.pop("id")
			d["rideId"]=x
			d["username"]=y
			timestamp=d["timestamp"]
			date_time=timestamp.split(":")
			s_m_h=date_time[1].split("-")
			d_m_y=date_time[0].split("-")
			new_date=d_m_y[2]+"-"+d_m_y[1]+"-"+d_m_y[0]+" "+s_m_h[2]+":"+s_m_h[1]+":"+s_m_h[0]

			current=datetime.now()
			
			date1 = datetime.strptime(new_date, '%Y-%m-%d %H:%M:%S')
			if(date1>current):
				ride.append(d)
				flag=True
		if(flag):
			return jsonify(ride),200
		return jsonify(),204

#5) List all the details of a given ride 
@app.route("/api/v1/rides/<rideid>")
def ride_details(rideid):
	with app.test_client() as client:
		response = client.get('/')
		if(response.status_code==405):
			abort (str(response.status_code))

	det_ride=Ride.query.filter_by(id=rideid)
	if (bool(Ride.query.filter_by(id=rideid).first())):
		ride_schema=RideSchema(many=True)
		output=ride_schema.dump(det_ride)
		st=[]
		for i in output:
			for j in i["users"]:
				st.append(j["users"])
			i["users"]=st
			i.pop("id")
			i["rideId"]=rideid
			x=i["created_by"]
			i.pop("created_by")
			i["Created_by"]=x
			y=i["timestamp"]
			i.pop("timestamp")
			i["Timestamp"]=y
			

		return jsonify(output),200
	return jsonify(),204

#6)Join an existing ride (API)
@app.route("/api/v1/rides/<rideid>",methods=["POST"])
def join_ride(rideid):
	with app.test_client() as client:
		response = client.get('/')
		if(response.status_code==405):
			abort (str(response.status_code))
	if not request.get_json() or not 'username' in request.get_json(): 
		abort(400)
	username=request.get_json()["username"]
	users=User.query.filter_by(username=username).first()
	ride=Ride.query.filter_by(id=rideid).first()
	riders={"rideid":rideid,"users":username}
	if bool(users):
		if bool(ride):
			if(Ride.query.filter_by(created_by=username,id=rideid).first()):
				abort(400)
			if(Shared_user.query.filter_by(rideid=rideid,users=username)).first():
				abort(400)
			shared_request=requests.post(request.url_root+"api/v1/write/shared",json=riders)
			shared_request.text
			return jsonify(),200
		return jsonify(),204
	return jsonify(),204



#7)Delete ride (API)
@app.route("/api/v1/rides/<rideid>",methods=["DELETE"])
def remove_ride(rideid):
	with app.test_client() as client:
		response = client.get('/')
		if(response.status_code==405):
			abort (str(response.status_code))
	rides=Ride.query.filter_by(id=rideid).first()
	if rides:
		db.session.delete(rides)	
		db.session.commit()
		return jsonify(),200
	abort(400)

	
if __name__ == '__main__':	
	app.run(host='0.0.0.0')

#{"created_by":"Karan","timestamp":"31-05-2021:23-16-10","source":"3","destination":"5"}
#{"username":"Karan","password":"dasdasdasdwjejqkhejkdasdasdaqwhjkeqhjkwe3344"}
