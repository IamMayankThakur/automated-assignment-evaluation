from flask import Flask,request,jsonify
import json
from flask_sqlalchemy import SQLAlchemy
import requests
import re
from datetime import datetime
from placesEnum import placeList
import ast


app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

db = SQLAlchemy(app)

#class for user table
class User(db.Model):
	id = db.Column(db.Integer,primary_key = True)
	username = db.Column(db.String(800),nullable = False)
	password = db.Column(db.String(800),nullable=False)

	def __init__(self,username,password):
		self.username = username
		self.password = password

#class for rides table
class Rides(db.Model):
	rideid = db.Column(db.Integer,primary_key = True)
	created_by = db.Column(db.String(800), nullable = False) 
	timestamp = db.Column(db.String(800), nullable = False) 
	source = db.Column(db.Integer,nullable = False)
	destination = db.Column(db.Integer,nullable =False)
	#string containing semicolon seperated usernames part of the ride
	users = db.Column(db.String(7000))

	def __init__(self,created_by,timestamp,source,destination,users=""):
		self.created_by = created_by
		self.timestamp = timestamp
		self.source = source
		self.destination = destination 
		self.users = users


#API to perform DB write operations
@app.route('/api/v1/db/write', methods = ["POST"])
def db_write():
	new_json=request.get_json()
	table_name = new_json['table_name']
	db_action = new_json['db_action']
	db_data = new_json['db_data']


	if table_name == "Rides":
		if db_action == "add":
			created_by = db_data['created_by']
			timestamp = db_data['timestamp']
			source = db_data['source']
			destination = db_data['destination']
			#creating an instance of class rides
			new_action = Rides(created_by,timestamp,source,destination,created_by)
			db.session.add(new_action)
			db.session.commit()
			return "created", 201

		elif db_action == "delete":
			db.session.query(Rides).filter(Rides.rideid == db_data).delete()
			db.session.commit()
			return "deleted",200

		elif db_action == "adduser":
			newride = new_json['ridenum']
			db.session.query(Rides).filter(Rides.rideid==newride).update({Rides.users:Rides.users+";"+db_data}, synchronize_session = False)
			db.session.commit()
			return {},200

		elif db_action == "rideswithuser":
			#converting string of list to list
			res = ast.literal_eval(db_data)
			#extracting username from json body
			uname=new_json['username']
			sepval=';'
			#iterating through list of rideIds user is a part of
			for i in res:
				#Extracting row from the table with corresponding rideid
				rec=db.session.query(Rides).filter(Rides.rideid==i)
				#splitting string based on ;
				userlist=str(rec[0].users).split(";")
				#If empty, continue with the next iteration
				if userlist==['']:
					continue
				#remove username from the list
				userlist.remove(uname)
				#join list elements into ; seperated string
				strvalue=sepval.join(userlist)
				#update the row values
				db.session.query(Rides).filter(Rides.rideid==i).update({Rides.users:strvalue}, synchronize_session = False)
				db.session.commit()
			return {},200

		elif db_action == "ridescreatedbyuser":
			db.session.query(Rides).filter(Rides.created_by == db_data).delete()
			db.session.commit()
			return "deleted",200


	elif table_name == "User":
		if db_action == "add":
			name = db_data['username']
			password = db_data['password']
			#creating an instance of class user
			new_action = User(name,password)
			db.session.add(new_action)
			db.session.commit()
			return "created",201

		elif db_action == "delete":
			db.session.query(User).filter(User.username == db_data).delete()
			db.session.commit()
			return "deleted",200


#API to perform DB read operations
@app.route('/api/v1/db/read', methods=['POST'])
def db_read():
	new_json=request.get_json()
	table_name = new_json['table_name']
	db_action = new_json['db_action']
	db_data = new_json['db_data']

	if table_name == "User":
		if db_action == "check":
			records = db.session.query(User).filter(User.username == db_data).all()
			if(records!=[]):
				return "exists", 200
			else:
				return "does not exist",200

	elif table_name=="Rides":
		if db_action=="list":
			records = db.session.query(Rides).filter(Rides.rideid == db_data).all()
			if(records!=[]):
				a={"rideId":str(records[0].rideid),"Created_by":str(records[0].created_by),"Timestamp":str(records[0].timestamp),"users":str(records[0].users).split(";"),"Source":str(records[0].source),"Destination":str(records[0].destination)}
				#converting to JSON
				return json.dumps(a),200
			else:
				return "NA",400

		elif db_action == "check":
			records = db.session.query(Rides).filter(Rides.rideid == db_data).all()
			if(records!=[]):
				return "exists", 200
			else:
				return "Does not exist", 200 

		elif db_action == "get":
			records = db.session.query(Rides).filter(Rides.source == db_data["src"]).all()
			up_rides = []
			for r in records:
			#	if(datetime.strptime(r.timestamp,"%d-%m-%Y:%S-%M-%H")< datetime.strptime(db_data["dtime"],"%d-%m-%Y:%S-%M-%H")):
			#		continue
				if(r.destination != db_data["dst"]):
					continue
				rd = {"rideId": r.rideid, "username": r.created_by, "timestamp": r.timestamp}
				up_rides.append(rd)
			#converting to JSON
			return json.dumps(up_rides),200

		elif db_action == "rideswithuser":
			a=[]
			records = db.session.query(Rides)
			for r in records:
				rlist=str(r.users).split(";")
				if db_data in rlist:
					a.append(r.rideid)
			#converting to JSON
			return json.dumps(a)

		'''elif db_action == "ridescreatedbyuser":
			a=[]
			records = db.session.query(Rides).filter(Rides.created_by==db_data)
			for r in records:
				a.append(r.rideid)
			return json.dumps(a)'''



#API to create new user
@app.route('/api/v1/users',methods = ["PUT"])
def add_user():
	#Getting request body
	req=request.get_json()
	#Sending request to read to check if username exits
	to_chk = requests.post('http://127.0.0.1:80/api/v1/db/read', json={'table_name':'User','db_action':'check','db_data':req["username"]})
	#validating SHA password
	passd_val=re.match("^[a-fA-F0-9]{40}$",req["password"])
	if(to_chk.text=="exists"):
		return "Username already exists", 400
	elif(passd_val==None):
		return "Invalid password", 400
	else:
		#Sending request to write to add user to DB
		r = requests.post('http://127.0.0.1:80/api/v1/db/write', json={'table_name':'User','db_action':'add','db_data':request.json})
		return {},201


#API to delete user
@app.route('/api/v1/users/<name>',methods = ["DELETE"])
def remove_user(name):
	#Sending request to read to check if user exits
	to_chk = requests.post('http://127.0.0.1:80/api/v1/db/read', json={'table_name':'User','db_action':'check','db_data':name})
	if(to_chk.text=="exists"):
		#Sending request to write, removing user from Users table
		r = requests.post('http://127.0.0.1:80/api/v1/db/write', json={'table_name':'User','db_action':'delete','db_data':name})

		#r1 = requests.post('http://127.0.0.1:80/api/v1/db/read', json={'table_name':'Rides','db_action':'ridescreatedbyuser','db_data':name})

		r4 = requests.post('http://127.0.0.1:80/api/v1/db/write', json={'table_name':'Rides','db_action':'ridescreatedbyuser','db_data':name})
		#Sending request to read, getting all rides that user is part of
		r2 = requests.post('http://127.0.0.1:80/api/v1/db/read', json={'table_name':'Rides','db_action':'rideswithuser','db_data':name})
		#Sending request to write, deleting user from the corresponding rides
		r3 = requests.post('http://127.0.0.1:80/api/v1/db/write', json={'table_name':'Rides','db_action':'rideswithuser','db_data':r2.text,'username':name})
		return {},200
	else:
		return "user does not exist",400


#API to create a ride
@app.route('/api/v1/rides',methods = ["POST"])
def create_ride():
	#Getting request body
	req=request.get_json()
	#Getting enum from constants file
	allplaces = placeList()
	avail = 0
	#Validating source and destination
	if int(req["source"]) in allplaces and int(req["destination"]) in allplaces:
		avail =1
	#Sending request to read, checking if user who is creating ride exists
	to_chk = requests.post('http://127.0.0.1:80/api/v1/db/read', json={'table_name':'User','db_action':'check','db_data':req["created_by"]})
	if(to_chk.text=="exists" and avail == 1):
		#Sending request to write, adding new ride to Rides table
		r = requests.post('http://127.0.0.1:80/api/v1/db/write', json={'table_name':'Rides','db_action':'add','db_data':req})
		return {},201
	else:
		return "Invalid user/source or destination",400


#API to list details of ride
@app.route('/api/v1/rides/<rideid>',methods = ["GET"])
def ride_dets(rideid):
	#Sending request to read, checking if given ride id is present
	to_chk = requests.post('http://127.0.0.1:80/api/v1/db/read', json={'table_name':'Rides','db_action':'list','db_data':rideid})
	if(to_chk.text=="NA"):
		return "Ride not present",400
	return to_chk.text,200


#API to list upcoming rides for a given source and destination
@app.route('/api/v1/rides',methods = ["GET"])
def list_rides():
	#Getting enum from constants file
	allplaces = placeList()
	#extracting source and destination from url
	src = request.args.get("source")
	dst = request.args.get("destination")
	avail=0
	#Validating source and destination
	if int(src) in allplaces and int(dst) in allplaces:
		avail =1
	if avail==0:
		return "Invalid source/destination",400
	#obtaining current date-time
	current = datetime.now()
	cur_str = current.strftime("%d-%m-%Y:%S-%M-%H")
	cur_dt = datetime.strptime(cur_str,"%d-%m-%Y:%S-%M-%H")
 	#JSON of required data
	req = {
	"src" : int(src),
	"dst" : int(dst),
	"dtime" : cur_str
	}
	#Sending request to read, obtaining details of upcoming rides
	to_chk = requests.post("http://127.0.0.1:80/api/v1/db/read",json={'table_name':'Rides','db_action':'get','db_data':req})
	if(to_chk.text=='[]'):
		return {},200
	return to_chk.text,200


#API to join a ride
@app.route('/api/v1/rides/<rideid>',methods = ["POST"])
def join_ride(rideid):
	#getting request body
	req=request.get_json()
	#Sending request to read, checking if it is a valid ride id
	to_chkRide = requests.post('http://127.0.0.1:80/api/v1/db/read', json={'table_name':'Rides','db_action':'list','db_data':rideid})
	if(to_chkRide.text=="NA"):
		return "Ride not present",400
	#Sending request to read, checking if it is a valid username
	to_chkUser=requests.post('http://127.0.0.1:80/api/v1/db/read', json={'table_name':'User','db_action':'check','db_data':req["username"]})
	if(to_chkRide.text=="NA"):
		return "Invalid user",400
	#Sending request to write, adding user to corresponding ride
	add_req = requests.post('http://127.0.0.1:80/api/v1/db/write', json={'table_name':'Rides','db_action':'adduser','db_data':req["username"],'ridenum':rideid})
	return {},200


#API to delete a ride
@app.route('/api/v1/rides/<rideid>',methods = ["DELETE"])
def delete_ride(rideid):
	#Sending request to read, checking if it is a valid ride id
	chk = requests.post('http://127.0.0.1:80/api/v1/db/read', json={'table_name':'Rides','db_action':'check','db_data':rideid})
	if(chk.text=="exists"):
		#Sending request to write, deleting corresponding ride
		r = requests.post('http://127.0.0.1:80/api/v1/db/write', json={'table_name':'Rides','db_action':'delete','db_data':rideid})
		return {},200
	else:
		return "ride does not exist",400



if __name__ == '__main__':
	app.run(debug = True)
