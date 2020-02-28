from gevent import monkey
monkey.patch_all()
from flask import Flask, render_template,jsonify,request,abort,Response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import requests
import pandas as pd
from sqlalchemy.orm.exc import NoResultFound
from gevent.pywsgi import WSGIServer

users={}
ride_count=1000
rides={}
ride_numbers=[]
count=0

app=Flask(__name__)

db = SQLAlchemy(app)

class User(db.Model):
	__tablename__ = 'user'
	username = db.Column(db.String(800000000000000000000000000000000000), primary_key=True, nullable=False)
	password = db.Column(db.String(800000000000000000000000000000000000), unique=False, nullable=False)

class Ride(db.Model):
	__tablename__ = 'ride'
	ride_id =  db.Column(db.Integer, primary_key=True)
	created_by = db.Column(db.String(80800000000000000000000000000000000000), unique=False, nullable=False)
	source = db.Column(db.String(80800000000000000000000000000000000000), unique=False, nullable=False)
	destination = db.Column(db.String(80800000000000000000000000000000000000), unique=False, nullable=False)
	timestamp = db.Column(db.String(30800000000000000000000000000000000000))
	
	#@property
	def serialize_ride(self,users):
		return {
				'rideId':self.ride_id,
				'created_by':self.created_by,
				'timestamp': self.timestamp,
				'source':self.source,
				'destination':self.destination,
				'users':users
			}
			
	@property
	def serialize_ride_deets(self):
		return {
				'rideId':self.ride_id,
				'username':self.created_by,
				'timestamp':self.timestamp
			}
	
class User_Ride(db.Model):
		__tablename__='user_ride'
		index = db.Column(db.Integer, nullable=False, primary_key=True)
		ride_id = db.Column(db.Integer, db.ForeignKey("ride.ride_id"),nullable=False)
		user = db.Column(db.String(80), db.ForeignKey("user.username"),nullable=False)


db.create_all()




def validate_pswd(password):
	if len(password)!=40:
		return False
	for i in password:
		if(not i.isdigit() and i not in 'abcdef' and i not in 'ABCDEF'):
			return False
	return True
		

@app.route('/api/v1/users', methods=['PUT'])
def Add_user():
	try:
		data = {}
		type='add'
		data=dict(request.json)
		print(data)
		if(data['username'] not in users.keys()):
			if(validate_pswd(data['password'])):
				users[data["username"]]=data["password"]
				print(users.keys())
				url_request = "http://localhost:5000/api/v1/cd/write"
				headers_request = {'Content-type': 'application/json', 'Accept': 'text/plain'}
				res = json.dumps(data)
				data_request = {'type' : 'add','insert': res}
				response = requests.post(url_request,data=json.dumps(data_request),headers=headers_request)
				print(response)
				check = db.session.query(User).all()
				print(check)
				return Response(json.dumps(dict()),status=201)
			else:
				return jsonify({}),400
		else:
			return jsonify({}),400
	except:
		return jsonify({}),400


@app.route('/api/v1/users/<username>', methods=['DELETE'])
def Remove_user(username):
	try:
		type='removeuser'
		data={}
		data["username"]=username
		if(username in users.keys()):
			del users[username]
			url_request = "http://localhost:5000/api/v1/cd/write"
			headers_request = {'Content-type': 'application/json', 'Accept': 'text/plain'}
			res = json.dumps(data)
			data_request = {'type' : 'removeuser','removeuser': res}
			response = requests.post(url_request,data=json.dumps(data_request),headers=headers_request)
			print(response)
			check = db.session.query(User).all()
			print(check)
			return Response(json.dumps(dict()),status=200)
		else:
			return jsonify({}),400
	except:
		return jsonify({}),400


def valid_src_dest(src,dest):
	df = pd.read_csv("AreaNameEnum.csv")
	print(df["Area No"])
	if(int(src) not in list(df["Area No"]) or int(dest) not in list(df["Area No"]) or src == dest):
		return 0
	else:
		return 1



@app.route('/api/v1/rides', methods=['POST'])
def New_ride():
	try:
		type = 'createride'
		ridedict={}
		ridedict=dict(request.json)
		
		if(valid_src_dest(ridedict["source"],ridedict["destination"]) == 0):
			return jsonify({}),400
		
		if(ridedict["created_by"] in users.keys()):
			global ride_count
			ride_count+=1
			ridedict["rideId"]=ride_count
			data={}
			data["username"]=ridedict["created_by"]
			data["rideId"]=ride_count
			global count
			data["index"]=count
			count+=1
			ride_numbers.append(ride_count)
			print(ride_numbers)
			rides[ride_count]={}
			rides[ride_count]["rideId"]=ride_count
			rides[ride_count]["created_by"]=ridedict["created_by"]
			rides[ride_count]["timestamp"]=ridedict["timestamp"]
			rides[ride_count]["users"]=[]
			rides[ride_count]["users"].append(ridedict["created_by"])
			rides[ride_count]["source"]=ridedict["source"]
			rides[ride_count]["destination"]=ridedict["destination"]
			print("successful")
			url_request = "http://localhost:5000/api/v1/cd/write"
			headers_request = {'Content-type': 'application/json', 'Accept': 'text/plain'}
			res = json.dumps(ridedict)
			data_request = {'type' : 'createride','insert': res}
			response = requests.post(url_request,data=json.dumps(data_request),headers=headers_request)
			print(response)
			check = db.session.query(Ride).all()
			print(check)
			url_request = "http://localhost:5000/api/v1/cd/write"
			headers_request = {'Content-type': 'application/json', 'Accept': 'text/plain'}
			res = json.dumps(data)
			data_request = {'type' : 'createuserride','insert': res}
			response = requests.post(url_request,data=json.dumps(data_request),headers=headers_request)
			print(response)
			check = db.session.query(User_Ride).all()
			print(check)
			return Response(json.dumps(dict()),status=201)
		else:
			return jsonify({}),400
	except:
		return jsonify({}),400


@app.route('/api/v1/rides', methods=['GET'])
def upcoming_rides():
	try:
		type='readride'
		data={}
		#data['source']=source
		#data['destination']=destination
		data['source']=request.args.get('source')
		data['destination']=request.args.get('destination')		
		
		if not(valid_src_dest(data['source'],data['destination'])):
			return jsonify({}),400	
		
		url_request = "http://localhost:5000/api/v1/cd/read"
		headers_request = {'Content-type': 'application/json', 'Accept': 'text/plain'}
		res = json.dumps(data)
		data_request = {'type' : 'readride','getride': res}
		response = requests.post(url_request,data=json.dumps(data_request),headers=headers_request)
		print("this is working \t\t\n\n\n")
		ride = response.json()
		
		
		print(ride)
		print("this works as well \n\n\n")
		
		if len(ride) == 0:
			return Response(status=204)
		#print("response ka json \t\n",response.json())	
		#print("jsonified response \t",jsonify(ride))	
		return jsonify(ride), 200
	except:
		return jsonify({}),400
	
	
	

@app.route('/api/v1/rides/<rideId>', methods=['GET'])
def ride_details(rideId):
	try:
		type='ridedetails'
		data={}
		data['rideId']=rideId
		global ride_numbers
		print(ride_numbers)
		print(int(rideId) in ride_numbers)
		if(int(rideId) in ride_numbers):
			url_request = "http://localhost:5000/api/v1/cd/read"
			headers_request = {'Content-type': 'application/json', 'Accept': 'text/plain'}
			res = json.dumps(data)
			data_request = {'type' : 'ridedetails','getride': res}
			response = requests.post(url_request,data=json.dumps(data_request),headers=headers_request)
			ride = response.json()["rides"]	
			return jsonify(ride),200
		else:
			return jsonify({}),204
	except:
		return jsonify({}),400
	
	

@app.route('/api/v1/rides/<rideId>', methods=['POST'])
def join_existing_ride(rideId):
	global ride_numbers
	global users
	global count
	print(ride_numbers)
	print(users)
	type_='addusertoride'
	data={}
	data=dict(request.json)
	data["Ride_Id"]=rideId
	data["index"]=count
	count+=1
	flag=0
	try:
		a=db.session.query(User_Ride).filter_by(user=data['username'],ride_id = data['Ride_Id']).one()
	except NoResultFound:
		flag=1
	if(flag!=1):
		return jsonify({}),400
	try:
		print(data)
		print(int(rideId) in ride_numbers)
		print(data["username"] in users.keys())
		# a=db.session.query(User_Ride).filter_by(user=data['username'],ride_id = data['Ride_Id']).one()
		# if(len(a)!=0):
		# 	return jsonify({}),400
		if(int(rideId) in ride_numbers and data["username"] in users.keys()):
			# a=db.session.query(User_Ride).filter_by(user=data['username'],ride_id = data['Ride_Id']).one()
			# if(len(a)!=0):
			# 	return jsonify({}),400
			print("in the loop")
			url_request = "http://localhost:5000/api/v1/cd/write"
			headers_request = {'Content-type': 'application/json', 'Accept': 'text/plain'}
			res = json.dumps(data)
			data_request = {'type' : 'addusertoride','insert': res}
			response = requests.post(url_request,data=json.dumps(data_request),headers=headers_request)
			print(response)
			check = db.session.query(User_Ride).all()
			print(check)
			return Response(json.dumps(dict()),status=200)
		else:
			return jsonify({}),204
	except:
		print("hello")
		return jsonify({}),204
	


@app.route('/api/v1/rides/<rideId>', methods=['DELETE'])
def delete_ride(rideId):
	try:
		type='removeride'
		data={}
		data['rideId']=rideId
		if(int(rideId) in ride_numbers):
			del rides[int(rideId)]
			ride_numbers.remove(int(rideId))
			url_request = "http://localhost:5000/api/v1/cd/write"
			headers_request = {'Content-type': 'application/json', 'Accept': 'text/plain'}
			res = json.dumps(data)
			data_request = {'type' : 'removeride','removeride': res}
			response = requests.post(url_request,data=json.dumps(data_request),headers=headers_request)
			print(response)
			check = db.session.query(Ride).all()
			print(check)
			url_request = "http://localhost:5000/api/v1/cd/write"
			headers_request = {'Content-type': 'application/json', 'Accept': 'text/plain'}
			res = json.dumps(data)
			data_request = {'type' : 'removeridefromother','removeride': res}
			response = requests.post(url_request,data=json.dumps(data_request),headers=headers_request)
			print(response)
			check = db.session.query(User_Ride).all()
			print(check)
			return Response(json.dumps(dict()),status=200)
		else:
			return jsonify({}),400
	except:
		return jsonify({}),400	


@app.route('/api/v1/cd/write', methods=['POST'])
def write_to_db():
	type_ = request.json['type']
	if type_ == 'add':
		user = request.json['insert']
		data = json.loads(user)
		adduser = User(username=data["username"], password=data["password"])
		db.session.add(adduser)
		db.session.commit()
		return Response(json.dumps(dict()),status=200)
	elif type_ == 'createride':
		ride = request.json['insert']
		data = json.loads(ride)
		addride = Ride(ride_id=data["rideId"],created_by=data["created_by"],source=data["source"],destination=data["destination"],timestamp=data["timestamp"])
		db.session.add(addride)
		db.session.commit()
		return Response(json.dumps(dict()),status=200)
	elif type_ == 'addusertoride':
		userride = request.json['insert']
		data = json.loads(userride)
		addusertoride = User_Ride(ride_id=data["Ride_Id"],user = data["username"],index=data["index"])
		db.session.add(addusertoride)
		db.session.commit()
		return Response(json.dumps(dict()),status=200)
	elif type_ == 'removeuser':
		user = request.json['removeuser']
		data = json.loads(user)
		usertodelete = db.session.query(User).filter_by(username = data['username']).one()
		db.session.delete(usertodelete)
		db.session.commit()
		usertodelete = db.session.query(User_Ride).filter_by(user = data['username']).all()
		for i in usertodelete:
			db.session.delete(i)
		db.session.commit()
		return Response(json.dumps(dict()),status=200)
	elif type_ == 'removeride':
		ride = request.json['removeride']
		data = json.loads(ride)
		usertodelete = db.session.query(Ride).filter_by(ride_id = data['rideId']).one()
		db.session.delete(usertodelete)
		db.session.commit()
		return Response(json.dumps(dict()),status=200)
	elif type_ == 'removeridefromother':
		ride = request.json['removeride']
		data = json.loads(ride)
		usertodelete = db.session.query(User_Ride).filter_by(ride_id = data['rideId']).all()
		for i in usertodelete:
			db.session.delete(i)
		db.session.commit()
		return Response(json.dumps(dict()),status=200)
	elif type_ == 'createuserride':
		userride =  request.json['insert']
		data = json.loads(userride)
		userrideadd = User_Ride(user=data["username"],ride_id=data["rideId"],index=data["index"])
		db.session.add(userrideadd)
		db.session.commit()
		return Response(json.dumps(dict()),status=200)
		

def datetimeconvert(datestring):
	datetime_object = datetime.strptime(datestring, '%d-%m-%Y:%S-%M-%H')
	return datetime_object
	
	
@app.route('/api/v1/cd/read', methods=['POST'])
def read_from_db():
	type_ = request.json['type']
	if type_ == 'ridedetails':
		user = request.json['getride']
		data = json.loads(user)
		rides=db.session.query(Ride).filter_by(ride_id=data['rideId']).one()
		db.session.commit()
		user_rides = db.session.query(User_Ride).filter_by(ride_id=data['rideId']).all()
		users=list()
		for u in user_rides:
			users.append(u.user)
		print(users)
		#print(rides)
		return  jsonify(rides=rides.serialize_ride(users))

	elif type_ == 'readride':
		user = request.json['getride']
		data = json.loads(user)
		rides=db.session.query(Ride).filter_by(source=data['source'], destination=data['destination']).all()
		db.session.commit()

		serialised_rides = []
		for indv_ride in rides:
			print("hello \t\t")
			indv_ride = indv_ride.serialize_ride_deets
			print("bye \t\t")
			if datetimeconvert(indv_ride["timestamp"]) > datetime.now():
				serialised_rides.append(indv_ride)
		print("ser_rides \t\t",serialised_rides)
		#print("hey",rides_temp)
		return jsonify(serialised_rides), 200

	

if __name__=='__main__':
	app.debug=True
	#app.run()
	http_server = WSGIServer(("",5000),app)
	http_server.serve_forever()
	
