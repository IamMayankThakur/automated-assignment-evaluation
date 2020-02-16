from flask import Flask, request, jsonify, abort, Response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
import json
import string
import requests
import datetime
import time
from requests.exceptions import HTTPError


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'cca12.sqlite')
db = SQLAlchemy(app)
ma = Marshmallow(app)


class User(db.Model):
	username = db.Column(db.String, unique=True, primary_key=True)
	password = db.Column(db.String, unique=True)

	def __init__(self, username, password):
		self.username = username
		self.password = password


class UserSchema(ma.Schema):
	class Meta:
		# Fields to expose
		fields = ('username', 'password')


class Ride(db.Model):
	id = db.Column(db.Integer, unique=True, primary_key=True)
	created_by = db.Column(db.String)
	timestamp = db.Column(db.String)
	source = db.Column(db.Integer)
	destination = db.Column(db.Integer)
	users = db.Column(db.String)

	def __init__(self, created_by, timestamp, source, destination, users):
		self.created_by = created_by
		self.timestamp = timestamp
		self.source = source
		self.destination = destination
		self.users = users


class RideSchema(ma.Schema):
	class Meta:
		# Fields to expose
		fields = ('id','created_by', 'timestamp', 'source', 'destination', 'users')


user_schema = UserSchema()
users_schema = UserSchema(many=True)


ride_schema = RideSchema()
rides_schema = RideSchema(many=True)


@app.route("/api/v1/db/write", methods=["POST","DELETE"])#API8
def write_to_db():
	table =  request.get_json()['table']#to choose which table to to write to

	if(request.method == 'POST'):
		if(table == 'Ride'):
			new = request.get_json()['new']
			if(new == 1):#inserting new row given details
				created_by = request.get_json()['created_by']
				timestamp = request.get_json()['timestamp']
				source = request.get_json()['source']
				destination = request.get_json()['destination']
				users = request.get_json()['users']

				new_ride = Ride(created_by, timestamp, source, destination, users)

				db.session.add(new_ride)
				db.session.commit()

			else:#to update users or source or details given column name and updated value
				column = request.get_json()['column']
				value = request.get_json()['value']
				ride_id = request.get_json()['ride_id']
				ride = Ride.query.get(ride_id)
				if(column == 'users'):
					ride.users = value
				elif(column == 'source'):
					ride.source = value
				elif(column == 'destination'):
					ride.destination = value
				db.session.commit()

		elif(table == 'User'):
			new = request.json['new']
			if(new == 1):#inserting new row given details
				username = request.get_json()['username']
				password = request.get_json()['password']

				new_user = User(username, password)

				db.session.add(new_user)
				db.session.commit()

			else:#to update users or source or details given column name and updated value
				column = request.get_json()['column']
				value = request.get_json()['value']
				username = request.get_json()['username']
				user = User.query.get(username)
				if(column == 'password'):
					user.password = value
				db.session.commit()

	elif(request.method == 'DELETE'):
		if(table == 'Ride'):
			ride_id = request.get_json()['ride_id']
			ride = Ride.query.get(ride_id)
			db.session.delete(ride)
			db.session.commit()

		elif(table == 'User'):
			username = request.get_json()['username']
			user = User.query.get(username)
			db.session.delete(user)
			db.session.commit()

	return {"status":"done"}



@app.route("/api/v1/db/read", methods=["POST"])#API9
def read_from_db():
	table =  request.get_json()['table']#to choose which table to read from
	if(table == 'Ride'):
		
		if(request.get_json()['col']==0):
			ride_id = request.json['ride_id']
			res = Ride.query.get(ride_id) #get all row values of a row with that ride_id(primary key)

			response_dict={}
			response_dict["ride_id"]=res.id
			response_dict["created_by"]=res.created_by
			response_dict["timestamp"]=res.timestamp
			response_dict["source"]=res.source
			response_dict["destination"]=res.destination
			response_dict["users"]=res.users

		elif(request.get_json()['col']==1):
			ride_id = request.json['ride_id']
			existing_ride_id = Ride.query.filter(Ride.id == ride_id).all()
			in_json = rides_schema.dump(existing_ride_id)
			return jsonify(in_json)

		elif(request.get_json()['col']==2): #to get details when src and dst is given
			src = request.get_json()['source']
			dst = request.get_json()['destination']
			src=int(src)
			dst=int(dst)

			result=Ride.query.filter(Ride.source == src).filter(Ride.destination == dst).all()
			result_in_json = rides_schema.dump(result)
			response_dict={}
		
			i=0
			for res in result_in_json:
				response_dict[i]=res
				i=i+1
		elif(request.get_json()['col']=='data'):
			ride_id = request.json['ride_id']
			existing_ride = Ride.query.filter(Ride.id == ride_id).all()
			result_in_json = rides_schema.dump(existing_ride)
			return jsonify(result_in_json)
			

	elif(table == 'User'):

		if(request.get_json()['col']==0):
			username = request.json['username']
			res = User.query.get(username)#to get all row values of a row with that username(primary key)

			response_dict={}
			response_dict["username"]=res.username
			response_dict["password"]=res.password

		elif(request.get_json()['col']==1):
			username = request.json['username']
			existing_username = User.query.filter(User.username == username).all()
			in_json = users_schema.dump(existing_username)
			return jsonify(in_json)

		elif(request.get_json()['col']==2):
			password = request.json['password']
			existing_password = User.query.filter(User.password == password).all()
			in_json = users_schema.dump(existing_password)
			return jsonify(in_json)

	return jsonify(response_dict)

#add a user given username and password
@app.route("/api/v1/users", methods=["PUT"])#API1
def add_user():

	username = request.json['username']
	password = request.json['password']
	password=password.lower()
	d={}
	d["table"]="User"
	d["new"]=1
	d["username"]=username
	d["password"]=password

	url = 'http://0.0.0.0:80/api/v1/db/write'
	urlr = 'http://0.0.0.0:80/api/v1/db/read'
	
	existing_username = requests.post(url=urlr, json={"table":"User","col":1,"username":username})
	existing_password = requests.post(url=urlr, json={"table":"User","col":2,"password":password})

	not_hexa=False
	for ch in password:
		if ch not in string.hexdigits:
			not_hexa=True

	if existing_username.json():
		abort(400, description="username already exists")

	elif existing_password.json():
		abort(400, description="password already exists")
		
	elif(len(password)!= 40 or not_hexa):
		abort(400, description="password is not SHA1 hash hex")
		
	else:
		response = requests.post(url=url, json=d)
		d1=response.text
		#return Response(d1, status=201, mimetype='application/json')
		return jsonify(),201


#delete a user given username
@app.route("/api/v1/users/<username>", methods=["DELETE"])#API2
def remove_user(username):

	urlr = 'http://0.0.0.0:80/api/v1/db/read'
	existing_username = requests.post(url=urlr, json={"table":"User","col":1,"username":username})
	url = 'http://0.0.0.0:80/api/v1/db/write' 
	if existing_username.json():
		requests.delete(url = url,json={"table":"User","username":username})
		#return Response({"status":"done"}, status = 200, mimetype='application/json')
		return jsonify(),200
	else:
		abort(400, description="username does not exists")


#create a ride
@app.route("/api/v1/rides", methods=["POST"]) #API3
def create_ride():
	
	createdby = request.get_json()['created_by']
	timestamp = request.get_json()['timestamp']
	source = request.get_json()['source']
	destination = request.get_json()['destination']
	username=createdby

	url = 'http://0.0.0.0:80/api/v1/db/write'

	if(request.method != 'POST'):
		abort(400, description="this method is not allowed")

	else:
		try:
			datetime.datetime.strptime(timestamp, '%d-%m-%Y:%S-%M-%H')
		except ValueError:
			abort(400,description="timestamp format not correct")
			#raise ValueError("Incorrect data format, should be dd-mm-yyyy:ss-mm-hh")

	my_time = datetime.datetime.strptime(timestamp, "%d-%m-%Y:%S-%M-%H")

	urlr = 'http://0.0.0.0:80/api/v1/db/read'
	
	existing_username = requests.post(url=urlr, json={"table":"User","col":1,"username":username})

	if (datetime.datetime.today() - my_time).days > 0:
		abort(400, description="you can't create ride for date that is over")
		
	elif (source==destination):
		abort(400,description="same source and destination is not allowed")
	elif (source<1 or source>198):
		abort(400,description="source is invalid")
	elif (destination<1 or destination>198):
		abort(400,description="destination is invalid")

	elif existing_username.json():
		response = requests.post(url=url, json={"table": "Ride", "new": 1, "created_by": createdby, "timestamp": timestamp , "source":source , "destination":destination , "users":""})
        
		return jsonify(),201
	else:
		abort(400, description="username doesn't exist")


#query string: 127.0.0.1:5000/api/v1/rides?source=13&destination=15
@app.route("/api/v1/rides", methods=["GET"])#API4
def list_upcompingrides():
	src = request.args.get('source')
	dst = request.args.get('destination')
	src=int(src)
	dst=int(dst)

	urlr = 'http://0.0.0.0:80/api/v1/db/read'

	response_ride = requests.post(url=urlr, json={"table": "Ride", "source": src, "destination":dst, "col":2 })

	if(src<1 or src>198):
		abort(400,description="source is invalid")

	elif(dst<1 or dst>198):
		abort(400,description="destination is invalid")

	elif(src==dst):
		abort(400,description="same source and destination is not allowed")

	elif response_ride.json():

		res1=response_ride.json()
		res=[]
		i=0
		d_val = res1.values()
		current_time = datetime.datetime.today()
		for item in d_val:
			if((current_time - datetime.datetime.strptime(item['timestamp'],'%d-%m-%Y:%S-%M-%H')).days < 0):
				res.append(item)
		
		if(res=={}):
			return Response(res1, status=204, mimetype='application/json')#no rides between that source and destination

		else:
			return jsonify(res), 200
	else:
		abort(400,description="there are no rides between this source and destination")

	

@app.route("/api/v1/rides/<ride_id>", methods=["GET"])#API5
def list_ride_details(ride_id):

	urlr = 'http://0.0.0.0:80/api/v1/db/read'
	existing_ride_id = requests.post(url=urlr, json={"table":"Ride","col":1,"ride_id":ride_id})

	if existing_ride_id.json():
		response_ride = requests.post(url=urlr, json={"table": "Ride", "ride_id": ride_id, "col":0 })
        	# If the response was successful, no Exception will be raised
		res = response_ride.text
		
		return Response(res, status=200, mimetype='application/json')
			
	else:
		abort(400, description="there are no rides with this ride_id")


@app.route("/api/v1/rides/<ride_id>", methods=["POST"])#API6
def join_ride(ride_id):

	username = request.json['username']
	urlr = 'http://0.0.0.0:80/api/v1/db/read'
	
	existing_username = requests.post(url=urlr, json={"table":"User","col":1,"username":username})

	if existing_username.json():
		existing_rides = requests.post(url=urlr, json={"table":"Ride","col":1,"ride_id":ride_id})
		
		url = 'http://0.0.0.0:80/api/v1/db/write'
		if existing_rides.json():
			delim=","
			existing_rides_data = requests.post(url=urlr, json={"table":"Ride","col":"data","ride_id":ride_id})

			for row in existing_rides_data.json():
				s = row['users']
				created_user = row['created_by'] 

			if(created_user == username):
				abort(400,"this user has created the ride, he cannot join the ride again")

			elif(username in s):
				abort(400,"this user has already joined this ride")

			else:
				if s=="":
					delim=""
				ans = s +delim+username
				d = {}
				d['value'] = ans
				d['table'] = "Ride"
				d['new']=0
				d['column']="users"
				d['ride_id']=ride_id
				response = requests.post(url = url,json = d)
				d1 = response.text
				#return Response({}, status = 200, mimetype='application/json')
				return jsonify(),200
		else:
			abort(400,"ride_id does not exist")
	else:
		abort(400, description="username doesn't exists")


#delete a ride given ride id	
@app.route("/api/v1/rides/<ride_id>", methods=["DELETE"])#API7
def delete_ride(ride_id):
	#existing_ride_id = Ride.query.filter(Ride.id == ride_id).all()
	urlr = 'http://0.0.0.0:80/api/v1/db/read'
	url = 'http://0.0.0.0:80/api/v1/db/write'
	existing_ride_id = requests.post(url=urlr, json={"table":"Ride","col":1,"ride_id":ride_id})
	
	if existing_ride_id.json():
		requests.delete(url = url,json={"table":"Ride","ride_id":ride_id})
		#return Response({"status":"done"}, status = 200, mimetype='application/json')
		return jsonify(),200
	else:
		abort(400, description="ride_id does not exist")


@app.route("/api/v1/allusers", methods=["GET"])
def get_user():
    all_users = User.query.all()
    result = users_schema.dump(all_users)
    return jsonify(result)

@app.route("/api/v1/allrides", methods=["GET"])
def get_ride():
    all_rides = Ride.query.all()
    result = rides_schema.dump(all_rides)
    return jsonify(result)


@app.route('/hello', methods=["POST"])
def hello_world():	
	#name = request.json['name']
	#return "H
	#return "hi"
	#d=request.get_json()['name']
	d={}
	d['name']='prakruti'
	return jsonify(d)


@app.route("/api/v1/trial", methods=["PUT"])
def trial():
	d=request.get_json()
	#response = requests.post(url ='http://127.0.0.1:5000/hello',json={'name':'prakruti'})
	#json_response = response.json()
	response = requests.post(url ='http://0.0.0.0:80/hello',json=d)
	return response.text


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80, threaded=True)