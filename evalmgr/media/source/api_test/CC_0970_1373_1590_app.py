from flask import Flask,request,jsonify,make_response,session
from flask_sqlalchemy import SQLAlchemy
import requests
import json
import sys
import re
from constants import Places
from enum import Enum
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:''@localhost/blackpearl'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db =SQLAlchemy(app)
enum_list = list(map(int,Places))

class users(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer,primary_key = True)
	username = db.Column(db.String(100))
	password  = db.Column(db.String(100))
	db.create_all()
	def __init__(self,username,password):
		self.username = username
		self.password = password
class rides(db.Model):
	__tablename__ = 'rides'
	rideId = db.Column(db.Integer,primary_key = True)
	created_by = db.Column(db.VARCHAR(50))
	source  = db.Column(db.Integer)
	destination=db.Column(db.Integer)
	timestamp = db.Column(db.DATETIME(6))
	
	db.create_all()
	def __init__(self,created_by,timestamp,source,destination):
		self.created_by = created_by
		self.source=source
		self.destination=destination
		self.timestamp=timestamp
		
class jtable(db.Model):
	__tablename__ = 'jtable'
	rideId = db.Column(db.Integer,primary_key= True)
	rider_list = db.Column(db.VARCHAR(50),primary_key =True)
	db.create_all()
	def __init__(self,rideId,rider_list):
		self.rideId = rideId
		self.rider_list = rider_list
		
# Writing to database
@app.route('/api/v1/db/write',methods=['POST'])
def write():
	data = request.get_json()
	
	method = data['type']
	#add_user
	if(method == 'PUT'):
		username = data['username']
		password = data['password']
		create_user= users(username,password)
		db.session.add(create_user)
		db.session.commit()
		return make_response("added" ,200)
	#Remove user
	elif(method == 'DELETE'):
		username = data['username']
		db.session.query(users).filter(users.username == username).delete()
		db.session.commit()
		return  make_response("deleted",200)
	#create Ride
	elif(method == 'POST'):
		created_by = data['created_by']
		source=data['source']
		destination=data['destination']
		timestamp=data['timestamp']
		create_ride= rides(created_by,timestamp,source,destination)
		db.session.add(create_ride)
		db.session.commit()
		return make_response("",200)
	#join ride
	elif(method == 'jtable'):
		rideId = data['rideId']
		username = data['username']
		create_ride= jtable(rideId,username)	
		db.session.add(create_ride)
		db.session.commit()
		return make_response("",200)
	#delete ride
	elif(method == 'ride'):
		rideId = data['rideId']
		db.session.query(rides).filter(rides.rideId == rideId).delete()
		db.session.commit()
		return  make_response("deleted",200)
	#delete user in ride table
	elif(method=='second'):
		username = data['username']
		db.session.query(rides).filter(rides.created_by == username).delete()
		db.session.commit()
		return  make_response("deleted",200)
	#delete user in jtable
	elif(method=='third'):
		username = data['username']
		db.session.query(jtable).filter(jtable.rider_list == username).delete()
		db.session.commit()
		return  make_response("deleted",200)

#Reading From the database
@app.route('/api/v1/db/read',methods = ['POST'])
def read():
	data = request.get_json()
	table = data['table']
	#User table
	if(table == 'users'):
		read_data = users.query.all()
		user_data= dict()
		user_data['username'] = []
		user_data['password'] = []
		for user in read_data:
			user_data['username'].append(user.username)
			user_data['password'].append(user.password)
		return user_data
	#Ride table
	elif(table == "rides"):
		read_data = rides.query.all()
		ride_data = dict()
		ride_data['rideId'] = []
		ride_data['created_by'] = []
		ride_data['timestamp'] = []
		ride_data['source'] = []
		ride_data['destination'] = []
		for ride in read_data:
			ride_data['rideId'].append(ride.rideId)
			ride_data['created_by'].append(ride.created_by)
			ride_data['timestamp'].append(ride.timestamp)
			ride_data['source'].append(ride.source)
			ride_data['destination'].append(ride.destination)
		return ride_data
	#rider_list table
	elif(table == 'jtable'):
		read_data = jtable.query.all()
		join_data = dict()
		join_data['rideId'] = []
		join_data['rider_list'] =[]
		for user in read_data:
			join_data['rideId'].append(user.rideId)
			join_data['rider_list'].append(user.rider_list)
		return join_data
	
#Add user API
@app.route('/api/v1/users',methods=['PUT'])
def add_user():
	if(request.method!='PUT'):
		return jsonify( {}),405
	data = request.get_json()
	username = data['username']
	password = data['password']
	user_data = requests.post('http://127.0.0.1:80/api/v1/db/read',json={"table":"users"})
	user_data = user_data.json()
	pattern = re.compile(r'\b[0-9a-f]{40}\b')

	for i in range(len(user_data["username"])):
		if(username == user_data["username"][i] or not(re.match(pattern,password))):
			return jsonify({}),400
	write = requests.post('http://127.0.0.1:80/api/v1/db/write',json={"type":request.method,"username":username,"password":password})
	if(write):
		return jsonify({}),201
	else:
		return jsonify({}),500
	
#Remove user API
@app.route('/api/v1/users/<username>',methods=['DELETE'])
def remove_user(username):
	if(request.method!='DELETE'):
		return jsonify( {}),405
	
	user_data = requests.post('http://127.0.0.1:80/api/v1/db/read',json={"table":"users"})
	user_data = user_data.json()
	ride_data = requests.post('http://127.0.0.1:80/api/v1/db/read',json={"table":"rides"})
	ride_data = ride_data.json()
	join_data = requests.post('http://127.0.0.1:80/api/v1/db/read',json={"table":"jtable"})
	join_data = join_data.json()

	for i in range(len(user_data["username"])):	
		if(username == user_data["username"][i]):
			if username in ride_data['created_by']:	
				sec_write = requests.post('http://127.0.0.1:80/api/v1/db/write',json={"type":"second","username":username})
			if(username in join_data['rider_list']):
				third_write = requests.post('http://127.0.0.1:80/api/v1/db/write',json={"type":"third","username":username})
			write = requests.post('http://127.0.0.1:80/api/v1/db/write',json={"type":request.method,"username":username})
			return jsonify({}),200
	else:
		return jsonify({}),400
#^(0[1-9]|[12][0-9]|3[01])[- /.](0[1-9]|1[012])[- /.](19|20)\d\d[: /.](?:[012345]\d)-(?:[012345]\d)-(?:[01]\d|2[0123])$
#Creating a ride
@app.route('/api/v1/rides',methods=['POST'])
def create_ride():
	if(request.method!='POST'):
		return jsonify({}),405
	
	data = request.get_json()
	created_by = data['created_by']
	timestamp=data['timestamp']
	pattern = re.compile(r'^(0[1-9]|[12][0-9]|3[01])[- /.](0[1-9]|1[012])[- /.](19|20)\d\d:(?:[012345]\d)-(?:[012345]\d)-(?:[01]\d|2[0123])$')
	
	if(not (re.match(pattern,timestamp))):
		return jsonify({}),400
	else:
		time1 = datetime.strptime(timestamp,"%d-%m-%Y:%S-%M-%H" )
		time = datetime.strftime(time1,"%Y-%m-%d %H:%M:%S")
		source=data['source']
		destination=data['destination']
		read_data = requests.post('http://127.0.0.1:80/api/v1/db/read',json={"table":"users"})
		read_data = read_data.json()
		for i in range(len(read_data["username"])):
			if(created_by == read_data["username"][i] and source in enum_list and destination in enum_list):
				response = requests.post('http://127.0.0.1:80/api/v1/db/write',json={"type":request.method,"created_by":created_by,"timestamp":time,"source":source,"destination":destination})
				if(response):
					return jsonify({}),201
		else:
			return jsonify({}),400

#List all upcoming rides for a given source and destination
@app.route('/api/v1/rides',methods=['GET'])
def list_rides():
	if(request.method!='GET'):
		return jsonify({}),405
	source = int(request.args.get("source"))
	destination = int(request.args.get("destination"))
	read_data = requests.post('http://127.0.0.1:80/api/v1/db/read',json={"table":"rides"})
	read_data = read_data.json()
	upcoming = []
	current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	current_time = datetime.now().strptime(current_time,"%Y-%m-%d %H:%M:%S")
	for i in range(len(read_data["created_by"])):
		time1 = datetime.strptime(read_data['timestamp'][i],"%a, %d %b %Y %H:%M:%S %Z" )
		if(source == read_data['source'][i] and destination == read_data['destination'][i] and time1>current_time):
			time1 = datetime.strptime(read_data['timestamp'][i],"%a, %d %b %Y %H:%M:%S %Z" )
			time = datetime.strftime(time1,"%d-%m-%Y:%S-%M-%H")
			upcoming.append({"rideId":read_data['rideId'][i],"username":read_data['created_by'][i],"timestamp":time})
	if(len(upcoming)!=0):
		return jsonify(upcoming),200
	elif(len(upcoming)==0):
		return jsonify({}),204
	else:
		return jsonify({}),400

#List all the details of the given ride
@app.route('/api/v1/rides/<rideId>',methods=['GET'])
def ride_details(rideId):
	read_data = requests.post('http://127.0.0.1:80/api/v1/db/read',json={"table":"rides"})
	read_data = read_data.json()
	join_data = requests.post('http://127.0.0.1:80/api/v1/db/read',json={"table":"jtable"})
	join_data = join_data.json()
	rideId = int(rideId)
	jlist=[]
	for i in range(len(join_data['rideId'])):
		if rideId==join_data['rideId'][i]:
			jlist.append(join_data['rider_list'][i])
	for i in range(len(read_data["rideId"])):
		if(rideId == read_data["rideId"][i]):
			time1 = datetime.strptime(read_data['timestamp'][i],"%a, %d %b %Y %H:%M:%S %Z" )
			time = datetime.strftime(time1,"%d-%m-%Y:%S-%M-%H")
			return jsonify({"rideId":rideId,"created_by":read_data['created_by'][i],"users":jlist,"timestamp":time,"source":read_data['source'][i],"destination":read_data['destination'][i]})
	else:
		return jsonify({}),204

#Join an existing ride
@app.route('/api/v1/rides/<rideId>',methods = ['POST'])
def join_ride(rideId):
	if(request.method!='POST'):
		return jsonify({}),405
	rideId = int(rideId)
	data = request.get_json()
	username = data['username']
	ride_data = requests.post('http://127.0.0.1:80/api/v1/db/read',json={"table":"rides"})
	ride_data = ride_data.json()
	user_data = requests.post('http://127.0.0.1:80/api/v1/db/read',json={"table":"users"})
	user_data = user_data.json()
	jtable_data = requests.post('http://127.0.0.1:80/api/v1/db/read',json={"table":"jtable"})
	jtable_data = jtable_data.json()
	current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	current_time = datetime.now().strptime(current_time,"%Y-%m-%d %H:%M:%S")
	if(username in user_data['username']):
		for i in range(len(ride_data['rideId'])):
			time1 = datetime.strptime(ride_data['timestamp'][i],"%a, %d %b %Y %H:%M:%S %Z" )
			if(rideId == ride_data['rideId'][i] and time1>current_time and username != ride_data['created_by'][i]):
				write = requests.post('http://127.0.0.1:80/api/v1/db/write',json={"type":"jtable","rideId":rideId,"username":username})
				if(write):
					return jsonify({}),200
		else:
			return jsonify({}),204
	else:
		return jsonify({}),400
#Delete a ride
@app.route('/api/v1/rides/<rideId>',methods = ['DELETE'])
def delete_ride(rideId):
	if(request.method!='DELETE'):
		return jsonify({}),405
	user_data = requests.post('http://127.0.0.1:80/api/v1/db/read',json={"table":"rides"})
	user_data = user_data.json()
	rideId =int(rideId)
	for i in range(len(user_data['rideId'])):	
		if rideId == user_data['rideId'][i]:
			write = requests.post('http://127.0.0.1:80/api/v1/db/write',json={"type":"ride","rideId":rideId})
			if(write):
				return jsonify({}),200
			return jsonify({}),400
	else:
		return jsonify({}),204
if __name__=="__main__":
	app.run()