from flask import Flask, request , jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
import os
import re
import ast
import requests
import json
import csv
import collections
from flask_api import status
import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, DateTime
from flask_marshmallow import Marshmallow
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from flask import Flask, jsonify, request, abort,redirect, url_for, session
from flask import Flask, request, jsonify
from sqlalchemy import and_, or_, not_

app=Flask(__name__)
basedir= os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(basedir,'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False 
db = SQLAlchemy(app)
ma=Marshmallow(app)

class User(db.Model):
	__tablename__ ='User'
	uid = db.Column(db.Integer,primary_key=True)
	username=db.Column(db.String(25),unique=True)
	password=db.Column(db.String(40),unique=True)

	def __init__(self,username,password):
		self.username=username
		self.password=password

class UserSchema(ma.Schema):
	class Meta:
		fields=('uid','username','password')

user_schema=UserSchema()
users_schema=UserSchema(many=True)

class Ride(db.Model):
	__tablename__='Ride'
	ride_id = db.Column(db.Integer,primary_key=True)
	created_by=db.Column(db.String(25),unique=True)
	source=db.Column(db.String(50),unique=True)
	destination=db.Column(db.String(50),unique=True)
	time=db.Column(db.DateTime)
	users=db.Column(db.String(500))

	def __init__(self,created_by,users,timestamp,source,destination):
		self.created_by=created_by
		self.users=users
		self.timestamp=timestamp
		self.source=source
		self.destination=destination

class RideSchema(ma.Schema):
	class Meta:
		fields=('ride_id','created_by','users','timestamp','source','destination')

ride_schema=RideSchema()
rides_schema=RideSchema(many=True)

# 1. ADD USER API
@app.route('/api/v1/users',methods=['PUT'])
def addUser():
	if request.method=='PUT':
		username=request.json['username']
		password=request.json['password']
		Exists = db.session.query(User).filter_by(User.username=username)
		if (Exists.scalar() is not None ):
			return Response(status=400)
		else:
			length = len(password)
			if (length == 40):
				reg = r'[0-9a-fA-F]+'
				m = re.match(reg,password)
				if not m:
					return Response(status=400)
				data={"table" : "User", "method":"put", "username":username, "password":password}
				response=(requests.post('http://localhost:5000/api/v1/db/write', json=data))
				return Response(status=201)
			else:
				return Response(status=400)
	else:
		return Response(status=405)


# 2. DELETE USER
@app.route('/api/v1/users/<username>',methods=['DELETE'])
def deleteUser(username):
	if request.method=='DELETE':
		Exists = db.session.query(User).filter_by(username=username)
		if (Exists.scalar() is not None):
			data={"table":"User","method":"delete","username":username}
			print(data)
			response=(requests.post('http://localhost:5000/api/v1/db/write',json=data))
			return Response(status=200)
		else:
			return Response(status=400)
	else:
		return Response(status=405)


# 3. API FOR CREATING A NEW RIDE
@app.route('/api/v1/rides',methods=['POST'])
def addRide():
	if request.method=='POST':
		created_by=request.json['created_by']
		timestamp=request.json['timestamp']
		z=re.match("(0[1-9]|[1-2][0-9]|3[0-1])-(0[1-9]|1[0-2])-[0-9]{4}:[0-5][0-9]-[0-5][0-9]-(2[0-3]|[01][0-9])",timestamp)
		if not z:
			abort(401)
		source=request.json['source']
		destination=request.json['destination']
		Exists = db.session.query(User).filter_by(username=created_by)
		if (Exists.scalar() is not None ):
			data={"table" : "Ride" , "method":"post", "created_by":created_by, "users":created_by, "timestamp":timestamp, "source":source, "destination":destination}
			response=(requests.post('http://localhost:5000/api/v1/db/write',json=data))
			return Response(status=201)
		else:
			return Response(status=400)
	else:
		return Response(status=405)


#4. to list upcoming rides
@app.route('/api/v1/rides',methods=['GET'])
def upcomingRide():
	source=request.args.get('source')
	dest=request.args.get('destination')
	rides=db.session.query(Ride).filter(and_(Ride.source==int(source)),(Ride.destination==int(dest)))
	result=rides_schema.dump(rides)
	return jsonify(result)
'''
#4. Upcoming rides
@app.route('/api/v1/rides',methods=['GET'])
def upcomingRides():
	if (request.method=='GET'):
		source=request.args.get('source')
		dest=request.args.get('destination')
		for row in Area:
			if (int(row[0])!=source or int(row[0])!=destination):
				return Response(400)
			else:
				Exists = db.session.query(Ride).filter_by(rideId=rideId)
				if (Exists.scalar() is not None):
					rides=db.session.query(Ride).filter(and_(Ride.source==source),(Ride.destination==dest))
					result=rides_schema.dump(rides)
					return jsonify(result)
				else:
					return Response(204)
	else:
		return Response(405)
'''

# 5. Details of a Ride
@app.route('/api/v1/rides/<rideId>', methods = ['GET'])
def details():
	rideId = request.args.get('rideId')
	dets = db.session.query(Ride).filter(rideId= int(rideId))
	return {'status_code': status.HTTP_200_OK}

# 6. Join an existing ride
@app.route('/api/v1/rides/<rideId>',methods=['POST'])
def join():
	rideId = request.args.get('rideId')
	username = request.json['username']
	ride = db.session.query(Ride).filter_by(rideId=rideId)
	created_by = ride.created_by
	source = ride.source
	destination = ride.destination
	users = ride.users
	users = users+';'+username
	timestamp = ride.timestamp
	newRide = Ride(rideId,created_by,users,timestamp,source,destination)
	requests.post('http://localhost:5000/api/v1/db/write',json={"table":"Ride","method":"delete","rideId":rideId})
	response = requests.post('http://localhost:5000/api/v1/rides',json=newRide)
	return {'status_code':status.HTTP_200_OK}


# 7.TO DELETE A RIDE
@app.route('/api/v1/rides/<rideId>',methods=['DELETE'])
def deleteRide(rideId):
	rideId1=int(rideId)
	data={"table":"Ride","method":"delete","rideId":rideId1}
	print (data)
	response=(requests.post('http://localhost:5000/api/v1/db/write',json=data))
	return {'status_code':status.HTTP_200_OK}

# 8. Write to db
@app.route('/api/v1/db/write',methods=['POST'])
def writetodb():
	req=request.get_json()
	table=req['table']
	method=req['method']
	if (table=="Ride" and method=="post"):
		created_by=req['created_by']
		timestamp=req['timestamp']
		source=req['source']
		destination=req['destination']
		users=req['users']
		newRide=Ride(created_by,users,timestamp,source,destination)
		db.session.add(newRide)
		db.session.commit()
		return {'status_code':status.HTTP_200_OK}

	elif (table=="User" and method=="put"):
		username=req['username']
		password=req['password']
		newUser=User(username,password)
		db.session.add(newUser)
		db.session.commit()
		return {'status_code':status.HTTP_200_OK}

	elif (table=="User" and method=="delete"):
		username=req['username']
		user = User.query.filter_by(username=username).first_or_404()
		print("######################"+str(user))
		db.session.delete(user)
		db.session.commit()
		return {'status_code':status.HTTP_200_OK}

	elif(table=="Ride" and method=="delete"):
		ride_Id=req['rideId']
		ri=Ride.query.get(ride_Id)
		db.session.delete(ri)
		db.session.commit()
		return {'status_code':status.HTTP_200_OK}

	else:
		return {'status_code': status.HTTP_500_BAD_GATEWAY}


# 9. Read db
@app.route('/api/v1/db/read',methods=['POST'])
def Read():
	table = request.json['table']
	where = request.json['where']
	length = len(where)
	if (table=="Ride" and length==1):
		rideId = where[0]
		details = db.session.query(Ride).filter_by(rideId=rideId)
		rideId = details.rideId
		created_by = details.created_by
		users = details.users
		timestamp = details.timestamp
		source = details.source
		destination = details.destination
		users = users.split(';')
		result = {"rideId":rideId,"created_by":created_by,"users": users,"timestamp":timestamp,"source":source,"destination":destination}
		return result
	elif (table=="Ride" and length==2):
		source=where[0]
		destination=where[1]
		upcoming = db.session.query(Ride).filter_by(and_(source=source,destination=destination))
		result = []
		for i in upcoming:
			rideId = i.rideId
			username=i.username
			timestamp=i.timestamp
			up = {"rideId":rideId,"username":username,"timestamp":timestamp}
			result.append(up)
		return result
	elif (table=="User"):
		all_users=User.query.all()
		result=users_schema.dump(all_users)
		return jsonify(result)

if __name__=='__main__':
	app.run(debug=True)