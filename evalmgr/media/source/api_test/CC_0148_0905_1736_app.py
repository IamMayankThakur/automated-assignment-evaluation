from flask import Flask, request , jsonify,Response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
import os
import re
#import os
import ast
import requests
import json
import csv
import collections
from flask_api import status
import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy import and_,or_,not_
from flask_marshmallow import Marshmallow
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from flask import Flask, jsonify, request, abort,redirect, url_for, session
from flask import Flask, request, jsonify
#from flask.ext.sqlalchemy import SQLAlchemy
#from sqlalchemy.dialects.postgresql import ARRAY
import csv
import re



#import ARRAY
#init app
app=Flask(__name__)
basedir= os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(basedir,'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False 
db = SQLAlchemy(app)
ma=Marshmallow(app)

Area = []
f = open('AreaNameEnum.csv')
#enum = csv.reader(f)
try:
    enum = csv.reader(f)
    next(f)     # Skip the first 'title' row.
    for row in enum:
    	a = [int(row[0]),row[1]]
    	Area.append(a)
finally:
    # Close files and exit cleanly
    f.close()


class User(db.Model):
	__tablename__ ='User'
	id = db.Column(db.Integer,primary_key=True)
	username=db.Column(db.String(100))
	password=db.Column(db.String(50))

	def __init__(self,username,password):
		self.username=username
		self.password=password

class UserSchema(ma.Schema):
	class Meta:
		fields=('id','username','password')

user_schema=UserSchema()
users_schema=UserSchema(many=True)



class Ride(db.Model):
	__tablename__='Ride'
	rideId = db.Column(db.Integer,primary_key=True)
	created_by=db.Column(db.String(100))
	timestamp=db.Column(db.String(50))
	source=db.Column(db.Integer)
	destination=db.Column(db.Integer)
	#users=db.Column(MutableList.as_mutable(ARRAY(db.String(50))))

	def __init__(self,created_by,timestamp,source,destination):
		self.created_by=created_by
		self.timestamp=timestamp
		self.source=source
		self.destination=destination
		#self.users=users


class RideSchema(ma.Schema):
	class Meta:
		fields=('rideId','created_by','timestamp','source','destination')

ride_schema=RideSchema()
rides_schema=RideSchema(many=True)

@app.route('/hi',methods=['GET'])
def hello():
	return {'status_code':status.HTTP_200_OK}

# 1. ADD USER API
@app.route('/api/v1/users',methods=['PUT'])
def addUser():
	if request.method=='PUT':
		username=request.json['username']
		password=request.json['password']
		Exists = db.session.query(User).filter_by(username=username)
		if (Exists.scalar() is not None ):
			return Response(status=400)
		else:
		
	#newUser=User(username,password)
			length = len(password)
			if (length == 40):
				reg = r'[0-9a-fA-F]+'
				m = re.match(reg,password)
				if not m:
					return Response(status=400)
				data={"table" : "User" , "method":"put","username":username,"password":password}
				response=(requests.post('http://localhost:5000/api/v1/db/write',json=data))
				return Response(status=201)
			else:
				return Response(status=400)
	else:
		return Response(status=405)

# 3. API FOR CREATING A NEW RIDE
@app.route('/api/v1/rides',methods=['POST'])
def addRide():
	if request.method=='POST':
		created_by=request.json['created_by']
	#timestamp=request.json['timestamp']
		timestamp=request.json['timestamp']
		#timestamp=str(timestamp)
		#z=re.match("(0[1-9]|[1-2][0-9]|3[0-1]-(0[1-9]|1[0-2])-[0-9]{4}):[0-5][0-9]-[0-5][0-9]-(2[0-3]|[01][0-9])",timestamp)
		z=re.match("(0[1-9]|[1-2][0-9]|3[0-1])-(0[1-9]|1[0-2])-[0-9]{4}:[0-5][0-9]-[0-5][0-9]-(2[0-3]|[01][0-9])",timestamp)
		if not z:
			abort(401)

		source=request.json['source']
		destination=request.json['destination']
		Exists = db.session.query(User).filter_by(username=created_by)
		if (Exists.scalar() is not None ):
			data={"table" : "Ride" , "method":"post","created_by":created_by,"timestamp":timestamp,"source":source,"destination":destination}
			print(data)
			response=(requests.post('http://localhost:5000/api/v1/db/write',json=data))
			return Response(status=201)
		else:
	#newUser=User(username,password)
			return Response(status=400)
		
	else:
		return Response(status=405)


#7. TO DELETE A RIDE
@app.route('/api/v1/rides/<rideId>',methods=['DELETE'])
def deleteRide(rideId):
	if request.method=='DELETE':
		Exists = db.session.query(Ride).filter_by(rideId=rideId)
		if (Exists.scalar() is not None):
			rideId1=int(rideId)
			data={"table":"Ride","method":"delete","rideId":rideId1}
			print (data)
			response=(requests.post('http://localhost:5000/api/v1/db/write',json=data))
			return Response(status=200)
		else:
			return Response(status=400)
	else:
		return Response(status=405)
	

	

# 3. DELETE USER
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
#6. to list ride
@app.route('/api/v1/rides',methods=['GET'])
def upcomingRide():
	source=request.args.get('source')
	dest=request.args.get('destination')

	rides=db.session.query(Ride).filter(and_(Ride.source==int(source)),(Ride.destination==int(dest)))
	result=rides_schema.dump(rides)
	return jsonify(result)
	
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


#5. details of given ride
@app.route('/api/v1/rides/<rideId>', methods=['GET'])
def details(rideId):
    if method == "get":
        exists = db.session.query(User.id).filter_by(name='davidism').scalar() is not None
        print(exists)
        return {'status_code':status.HTTP_200_OK}
'''
@app.route('/api/v1/rides/<rideId>',methods=['POST'])
def join():
	rideId = request.args.get('rideId')
	username = request.json['username']
	ride=db.session.query(Ride).filter_by(rideId=rideId)
	#ride.users = ride.users.append(username)
	users = ride.users
	users = users.append[username]
	ride.users = users
	db.session.commit()
	return ("Joined Ride")
'''
# 6. join ride
@app.route('/api/v1/rides/<rideId>',methods=['POST'])
def join(rideId):
	if (request.method=='POST'):
		rideId = request.args.get('rideId')
		username = request.json['username']
		ride = db.session.query(Ride).filter_by(rideId=rideId)
		created_by = ride.created_by
		source = ride.source
		destination = ride.destination
		users = ride.users
		users = users.append(username)
		timestamp = ride.timestamp
		newRide = Ride(rideId,created_by,users,timestamp, source,destination)
		requests.post('http://localhost:5000/api/v1/db/write',json={"table":"Ride","method":"delete","rideId":rideId})
		response = requests.post('http://localhost:5000/api/v1/rides',json=newRide)
		return {'status_code':status.HTTP_200_OK}
	else:
		return { jsonify({'status_code':status.HTTP_405_METHOD_NOT_ALLOWED})}

	
# 8. WRITE TO DB API	
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
		newRide=Ride(created_by,timestamp,source,destination)
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
		#print("hi")
		username=req['username']
		user = User.query.filter_by(username=username).first_or_404()
		print("######################"+str(user))
		#ri=User.query.get(user)
		db.session.delete(user)
		db.session.commit()
		return {'status_code':status.HTTP_200_OK}
	
		
	elif(table=="Ride" and method=="delete"):
		ride_Id=req['rideId']
		ri=Ride.query.get(ride_Id)
		db.session.delete(ri)
		db.session.commit()
		#return user_schema.jsonify()
		return {'status_code':status.HTTP_200_OK}
		

	else:
		return {'status_code': status.HTTP_500_BAD_GATEWAY}

# 9. READ FROM USER TABLE

@app.route('/api/v1/db/read/try',methods=['GET'])
def readfromdb1():

	all_users=User.query.all()
	result=users_schema.dump(all_users)
	return jsonify(result)

@app.route('/api/v1/db/read',methods=['POST'])
def readfromdb():
	req=request.get_json()
	print(req)
	table=req['table']
	method=req['method']
	if(table=='User' and method=='put'):
		username=req['username']
		Exists = db.session.query(User).filter_by(username=username)
		if (Exists.scalar() is not None ):
			return "1"
		else:
			return "0"
	else:
		return { jsonify({'status_code':status.HTTP_405_METHOD_NOT_ALLOWED})}
#7. TEMPORARY API- TO READ RIDE DATABASE
@app.route('/api/v1/db/readride',methods=['GET'])
def read():
	all_rides=Ride.query.all()
	result=rides_schema.dump(all_rides)
	return jsonify(result)


# read api try
'''
@app.route('/api/v1/db/read/try',methods=['GET'])
def readfromdb():
	req=get_json()
	table=req['table']
	column=req['column']

'''

	





if __name__=='__main__':
	app.run(debug=True)





'''
@app.route('/user/<uid>',methods=['PUT'])
def updateuser(uid):
	user=db.session.query(User.uid).filter_by(uid=uid)
	username=request.json['username']
	user.username=username
	db.session.commit()
	return users_schema.jsonify(user)


@app.route('/userdel/<rideId>',methods=["DELETE"])
def deleteuser(rideId):
	
		user=Ride.query.get(rideId)
		db.session.delete(user)
		db.session.commit()
		return user_schema.jsonify(user)
@app.route('/userdel/<username>',methods=["DELETE"])
def deleteuser(username):
	
		user = User.query.filter_by(username=username).first_or_404()
		db.session.delete(user)
		db.session.commit()
		return user_schema.jsonify(user)

@app.route('/user/<uid>',methods=['PUT'])
def updateuser(uid):
	uid=int(uid)
	user=db.session.query(User.uid).filter_by(uid=uid)
	
	#user=User.query.get(uid)
	username1=request.json['username']
	print("****"+username1)
	user.username=username1
	db.session.commit()
	return user_schema.jsonify(user)

'''
#run server
#9. FINAL READ API
'''
@app.route('/api/v1/db/read',methods=['GET'])
def read():
	req=request.get_json()
	table=req['table']
	column=req['column']
	if(table=="user" and )

'''

'''
@app.route('/api/v1/rides?source=<source>&destination=<destination>',methods=['GET'])
def upcoming(source,destination):
    rides = db.session.query(Ride).filter(and_(Ride.source == int(source)),(Ride.destination == int(destination)))
    print(rides)
    return {'status_code':status.HTTP_200_OK}
'''