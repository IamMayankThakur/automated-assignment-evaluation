from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy 
from flask_marshmallow import Marshmallow
from sqlalchemy.orm.attributes import flag_modified
import os
from sqlalchemy import PickleType
import requests
import re
import sys
from datetime import datetime
import datetime
import pandas as pd


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db1.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
db = SQLAlchemy(app)
ma = Marshmallow(app)




class User(db.Model):
	userId = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(),unique=True,nullable=False)
	password = db.Column(db.String(),nullable=False)

	def __init__(self, username, password):
		self.username = username
		self.password = password




class UserSchema(ma.Schema):
	class Meta:
		fields = ('username', 'password')




user_schema = UserSchema()
users_schema = UserSchema(many=True)


class Ride(db.Model):
	rideId = db.Column(db.Integer, primary_key=True)
	created_by = db.Column(db.String())
	timestamp = db.Column(db.String())
	source = db.Column(db.Integer)
	destination = db.Column(db.Integer)
	riders_list = db.Column(db.PickleType())



	def __init__(self, created_by, timestamp, source, destination, riders_list=[]):
		self.created_by = created_by
		self.timestamp = timestamp
		self.source = source
		self.destination = destination
		self.riders_list = riders_list


class RideSchema(ma.Schema):
	class Meta:
		fields = ('rideId','timestamp','created_by', 'source', 'destination', 'riders_list')




ride_schema = RideSchema()
rides_schema = RideSchema(many=True)

db.create_all()


def check_timestamp_24(timestamp):
	date_format = '%d-%m-%Y:%S-%M-%H'
	try:
		datetime1=datetime.datetime.strptime(timestamp,date_format)
		value = True
	except ValueError :
		value = False
	if value :
		current = datetime.datetime.utcnow()
		if current <= datetime1 :
			return True
		else :
			return False
	else :
		return False






@app.route('/api/v1/users', methods=['PUT'])
def add_user():
	if(request.method == 'PUT'):
		username = request.json['username']
		password = request.json['password']
		pattern=re.compile(r'\b([0-9a-f]|[0-9A-F]){40}\b')
		dic={}
		dic["username"]=username
		dic["password"]=password
		dic["some"]="add_user"
		if(len(username)==0 or len(password)==0):			
			return jsonify({}),400
		response = requests.post(url ='http://0.0.0.0:80/api/v1/db/read',json=dic)
		result= response.text
		if((result=="None") and (re.search(pattern, password))):
			response = requests.post(url ='http://0.0.0.0:80/api/v1/db/write',json=dic)
			
			return jsonify({}), 201
		else:
			return jsonify({}), 400
	else:
		return jsonify({}), 405



#2.Delete user
@app.route('/api/v1/users/<username>', methods=['DELETE'])
def remove_user(username):
	if(request.method == 'DELETE'):
		d={}
		d["some"]="remove_user"
		d["username"]=username
		response = requests.post(url ='http://0.0.0.0:80/api/v1/db/read',json=d)
		result = response.text
		if(result=="None"):
			return jsonify({}), 400
		else:
			response = requests.post(url ='http://0.0.0.0:80/api/v1/db/write',json=d)
			return jsonify({}), 200
	else:
		return jsonify({}), 405


#3.New ride
@app.route('/api/v1/rides', methods=['POST'])
def add_ride():
	if(request.method == 'POST'):
		created_by = request.json['created_by']
		timestamp = request.json['timestamp']
		source = request.json['source']
		destination = request.json['destination']
		if(int(source)==int(destination)):  #check
			return jsonify({}),400		

		if check_timestamp_24(timestamp):
			d={}
			d["created_by"]=created_by
			d["timestamp"]=timestamp
			d["source"]=source
			d["destination"]=destination
			d["some"]="add_ride"
			response = requests.post(url = 'http://0.0.0.0:80/api/v1/db/read' , json = d)
			result=response.text
			if int(source) in range(199) and int(destination) in range(199):
				if(result=="None"):
					return jsonify({}), 400
				else:
					response_1 = requests.post(url = 'http://0.0.0.0:80/api/v1/db/write' , json = d)
					return jsonify({}),201
			else:
				return jsonify({}),400
					
		else:
			return jsonify({}), 400
	else:
		return jsonify({}),405



#5.Ride details
@app.route('/api/v1/rides/<rideId>', methods=['GET'])
def ride_details(rideId):
	if(request.method == 'GET'):
		d={}
		d["some"]="ride_details"
		d["rideId"]=rideId
		response = requests.post(url = 'http://0.0.0.0:80/api/v1/db/read' , json = d)
		result=response.json()
		if(not bool(result)):
			return jsonify({}), 204
		else:
			return response.text, 200
	else:
		return jsonify({}),405

#7.Delete ride
@app.route('/api/v1/rides/<rideId>', methods=['DELETE'])
def delete_ride(rideId):
	if(request.method == 'DELETE'):
		d={}
		d["some"]="delete_ride"
		d["rideId"]=rideId
		response=requests.post(url='http://0.0.0.0:80/api/v1/db/read',json=d,headers={'Content-type':'application/json','Accept':'text/plain'})
		result = response.text

		if(result=="None"):
			return jsonify({}), 400
		else:
			w=requests.post(url='http://0.0.0.0:80/api/v1/db/write',json=d,headers={'Content-type':'application/json','Accept':'text/plain'})
			return jsonify({}), 200
	else:
		return jsonify({}),405



#6.Join ride 
@app.route('/api/v1/rides/<rideId>', methods=['POST'])
def join_ride(rideId):
	if(request.method == 'POST'):
	
		username = request.json['username']
		d={}
		d["rideId"]=rideId
		d["username"]=username
		d["some"]="join_ride"
		response=requests.post(url='http://0.0.0.0:80/api/v1/db/read',json=d,headers={'Content-type':'application/json','Accept':'text/plain'})
		result = response.text
		
		if(result=="Invalid"):
			return jsonify({}), 204
		else:
			response=requests.post(url='http://0.0.0.0:80/api/v1/db/write',json=d,headers={'Content-type':'application/json','Accept':'text/plain'})
			result = response.text
			return jsonify({}), 200
	else:
		return jsonify({}),405


#4.upcoming rides
@app.route('/api/v1/rides', methods=['GET'])
def upcoming_rides():
	if(request.method == 'GET'):

		source  = request.args.get('source')
		destination  = request.args.get('destination')
		if(int(source)==int(destination)):  #check
			return jsonify({}),400	
		d={}
		d["some"]="upcoming_rides"
		d["destination"]=destination
		d["source"]=source
		if int(source) in range(199) and int(destination) in range(199):
			response=requests.post(url='http://0.0.0.0:80/api/v1/db/read',json=d)
			result = response.text
			if(len(result)==0):
				return jsonify({}),204
			
			if(not bool(result)):
				return jsonify({}), 204
			else:
				return result, 200
		else:
			return jsonify({}),400
	else:
		return jsonify({}),405






#8.Write db
@app.route('/api/v1/db/write', methods=['POST'])
def write_db():
	api=request.get_json()["some"]
	if(api =="add_user"):
		user=request.get_json()["username"]
		pswd=request.get_json()["password"]
		new_user=User(user, pswd)
		db.session.add(new_user)
		db.session.commit()
		return jsonify({}),201
		
	elif(api=="remove_user"):
		user=request.get_json()["username"]
		user = User.query.filter_by(username=user).first()
		db.session.delete(user)
		db.session.commit()
		return jsonify({}),200


	elif(api=="add_ride"):
		username=request.get_json()["created_by"]
		timestamp=request.get_json()["timestamp"]
		source=request.get_json()["source"]
		destination=request.get_json()["destination"]
		new_ride=Ride(username, timestamp, source, destination )
		db.session.add(new_ride)
		db.session.commit()
		return jsonify({}),201

	elif (api=="delete_ride"):
		ride1=request.get_json()["rideId"]
		ride = Ride.query.filter_by(rideId=ride1).first()
		db.session.delete(ride)
		db.session.commit()
		return jsonify({}),200


	elif(api =="join_ride"):
		user=request.get_json()["username"]
		rideId=request.get_json()["rideId"]
		ride = Ride.query.filter_by(rideId=rideId).first()
		l=ride.riders_list
		if user not in l:
			l.append(user)
			ride.riders_list=l
			flag_modified(ride,"riders_list")
			db.session.merge(ride)
			db.session.flush()
			db.session.commit()
			return ride_schema.jsonify(ride)

	

	
		
	





	
	
		    
	

#9.Read db
@app.route('/api/v1/db/read', methods=['POST'])
def read_db():
	api=request.get_json()["some"]
	if(api=="add_user"):
		uname=request.get_json()["username"]
		user = User.query.filter_by(username=uname).first()
		return str(user)

	elif (api =="remove_user"):
		uname=request.get_json()["username"]
		user = User.query.filter_by(username=uname).first()
		return str(user)

	elif (api=="add_ride"):
		uname=request.get_json()["created_by"]
		user = User.query.filter_by(username=uname).first()
		return str(user)

	elif (api =="ride_details"):
		rides=request.get_json()["rideId"]
		ride = Ride.query.get(rides)
		return ride_schema.jsonify(ride)

	elif (api=="delete_ride"):
		ride1=request.get_json()["rideId"]
		ride = Ride.query.filter_by(rideId=ride1).first()
		return str(ride)



	elif(api=="join_ride"):
		uname=request.get_json()["username"]
		user = User.query.filter_by(username=uname).first()
		if(str(user)!="None"):
			rides=request.get_json()["rideId"]
			ride = Ride.query.filter_by(rideId=rides).first()
			if(str(ride)!="none"):
				return "Valid"
			else:
				return "Invalid"
		return "Invalid"

	elif (api=="upcoming_rides"):
		source1=request.get_json()["source"]
		destination1=request.get_json()["destination"]
		ride2=Ride.query.filter(Ride.source==int(source1),Ride.destination==int(destination1)).all()
		if(len(ride2)==0):
			return jsonify({}),204
		else:

			sk=str(ride2)
			upcoming=[]
			x=map(int, re.findall(r'\d+',sk))
			z=list(x)
			if(len(z)==0):
				return ride_schema.jsonify(ride2)

			else:
				for i in z: 
					y=Ride.query.get(i)
					tstamp=y.timestamp
					dt_value = datetime.datetime.strptime(tstamp, '%d-%m-%Y:%S-%M-%H')
					present_ts=datetime.datetime.utcnow()
					user1=y.created_by
					ucheck=User.query.filter_by(username=user1).first()
					if(str(ucheck)=="None"):
						pass
					elif(dt_value>present_ts):
						lol={}
						lol["rideId"]=y.rideId
						lol["username"]=y.created_by
						lol["timestamp"]=y.timestamp
						upcoming.append(lol)
				if(len(upcoming)==0):
					return "None"
				else:
					return jsonify(upcoming)


	
if __name__ == '__main__':
	app.run(debug=True,host='0.0.0.0',port=80,threaded=True)





