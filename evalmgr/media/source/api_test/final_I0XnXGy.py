from flask import Flask, request, jsonify, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy   
import requests 
import os 
import sys
import csv
import json
from time import strftime
from time import strptime
from datetime import datetime


# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
# Database           
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model): 
	
	username = db.Column(db.Text, unique=True, nullable=False, primary_key=True)
	password = db.Column(db.Text,  nullable=False)

class Ride(db.Model):

	rideID = db.Column(db.Integer, unique=True, nullable=False, primary_key=True,autoincrement=True)
	username = db.Column(db.Text, nullable=False)
	timestamp = db.Column(db.DateTime, nullable=False)
	source = db.Column(db.Integer, nullable=False)
	destination = db.Column(db.Integer, nullable=False)

	def __init__(self, timestamp, username, source, destination):
		#self.rideID = rideID
		self.timestamp = timestamp
		self.username = username
		self.source = source
		self.destination = destination


class JoinRide(db.Model):

	rid = db.Column(db.Integer, nullable=False)
	username = db.Column(db.Text, nullable=False, primary_key=True)

class Area(db.Model):
	enum = db.Column(db.Integer, primary_key=True)
	a_name = db.Column(db.Text, nullable = False)
	
# db.drop_all()
db.create_all()

def read_csv():
	filename = "AreaNameEnum.csv"
	with open(filename,'r') as csvfile:
		csvreader = csv.reader(csvfile)
		next(csvreader)
		d={}
		for row in csvreader:
			en1 = int(row[0])
			dest = row[1]
			d[en1]=dest
	return d

def add_enum():
	filename = "AreaNameEnum.csv"
	with open(filename,'r') as csvfile:
		csvreader = csv.reader(csvfile)
		next(csvreader)

		for row in csvreader:
			en1 = int(row[0])
			dest = row[1]
			#print(en1,dest)
			newfield = Area(enum=en1,a_name=dest)
			try:
				#print(1)
				db.session.add(newfield)
				db.session.commit()
			except:
				continue
				
def dat_str_dattime(sample):
	date,time = sample.split(':')
	dd,mm,yy = date.split('-')
	dd,mm,yy = int(yy),int(mm),int(dd)
	ss,m,hh = time.split('-')
	ss,m,hh = int(ss),int(m),int(hh)
	print(dd,mm,yy,hh,m,ss)
	sample = (datetime(dd,mm,yy,hh,m,ss))
	return sample
	
#1. Add User

@app.route('/api/v1/users', methods=['PUT'])
def add_user():

	if request.method != 'PUT':
		return jsonify({}),405

	req= request.get_json()
	uname =req["username"]
	pword = req["password"]  

	if uname == "":
		return jsonify({}),400

	flag=True
	a=['A','B','C','D','E','F','a','b','c','d','e','f','0','1','2','3','4','5','6','7','8','9']
	if(len(pword)!=40 ):
		flag=False
	else:
		for i in pword:
			if(not(i in a)):
				flag=False

	if(flag==False):
		#Invalid Password
		return jsonify({}),400
	user={
		"insert":[uname, pword],
		"column":["username", "password"],
		"table" : "User"
	}

	r = requests.post(url=" http://127.0.0.1:5000/api/v1/db/read", json=user)

	resp = r.json()

	if(resp == "Yes"):
		#User Exist
		return jsonify({}),400
	else:
		w = requests.post(url=" http://127.0.0.1:5000/api/v1/db/write", json=user)
		if(w):
			return jsonify({}),201
			# return jsonify("User Added"),201
		else:
			#Server Error
			return jsonify({}),500

#2. Remove User
@app.route('/api/v1/users/<uname>', methods=['DELETE'])
def removeUser(uname):	
	if request.method != 'DELETE':
		return jsonify({}),405

	uname = "{}".format(uname)
	R_user = {
		"insert" : uname,
		"column" : "delete",
		"table" : "User"
	}

	r = requests.post(url=" http://127.0.0.1:5000/api/v1/db/read", json=R_user)
	
	a = r.json()
	if(a == "Yes"):

		w = requests.post(url=" http://127.0.0.1:5000/api/v1/db/write", json=R_user)
		if(w):
			#User Removed
			return jsonify({}),200
		else:
			#Server Error
			return jsonify({}),500
	else:
		#User does Not Exist
		return jsonify({}),400

#3. Create ride
@app.route('/api/v1/rides', methods=['POST'])
def add_ride():
	if request.method != 'POST':
		return jsonify({}),405

	req = request.get_json()
	created_by = req["created_by"]
	timestamp = req["timestamp"]
	source = req["source"]
	destination = req["destination"]

	try:
		source = int(source)
		destination = int(destination)
		timestamp1 = datetime.strptime(timestamp,"%d-%m-%Y:%S-%M-%H")
	except Exception as e:
		
		return jsonify({}),400
		#return "Invalid Input",400	
	
	d=read_csv()
	if(source not in d.keys() or destination not in d.keys() or source == destination):
		return jsonify({}),400
		#return "Invalid area",400

	ride = {
		"insert":[created_by, timestamp, source, destination],
		"column":["username", "timestamp", "source", "destination"],
		"table" : "Ride"
	}
	now = datetime.now()
	date = dat_str_dattime(timestamp)
	
	if(date<now):
		return jsonify({}),400
		# return "invalid timestamp",400

	r = requests.post(url=" http://127.0.0.1:5000/api/v1/db/read", json=ride)
	
	a = r.json()
	
	if(a == "Yes"):
		#Ride already Exist
		return jsonify({}),400

	else:
		user = {
			"insert":[created_by],
			"column":"",
			"table" : "User"
 		}
 		#check username in User table
	
		u = requests.post(url=" http://127.0.0.1:5000/api/v1/db/read", json=user)
		print("finished reading")
		b = u.json()
		print("Going to write")
		if b == "Yes":
			w = requests.post(url=" http://127.0.0.1:5000/api/v1/db/write", json=ride)
			if(w):
				#Ride Created
				return jsonify({}),201
			else:
				#server Error
				return jsonify({}),500
		else:
			#No Username
			return jsonify({}),400
			
	return jsonify({}),500
	#Server Error

#4.List all upcoming rides for a given source and destination

@app.route('/api/v1/rides',methods = ['GET'])
def view_rides():

	if request.method != 'GET':
		return jsonify({}),405
	
	s = request.args.get('source')
	d = request.args.get('destination')

	input_read = {
		"table" : "Ride",
		"insert" : "",
		"column" : "get_ride",
		"source" : s,
		"destination" : d
	} 
	response = requests.post(url = "http://127.0.0.1:5000/api/v1/db/read",json=input_read)
	r = response.json()
	if(len(r) == 0):
		return jsonify({}),204
	return jsonify(response.json()),200

#5. List all the details of a given ride		

@app.route('/api/v1/rides/<r>',methods = ['GET'])
def view_users(r):

	if request.method != 'GET':
		return jsonify({}),405

	input_read = {
		"table" : "Ride",
		"insert" : r,
		"column" : "get_users",
		} 
	response = requests.post(url = "http://127.0.0.1:5000/api/v1/db/read",json=input_read)
	r = response.json()
	if(len(r) == 0):
		return jsonify({}),204
	return jsonify(response.json()),200
	
#6. Join an existing ride

@app.route('/api/v1/rides/<rideID>', methods=['POST'])
def joinride(rideID):

	if request.method != 'POST':
		return jsonify({}),405

	req = request.get_json()
	uname = req["username"]

	J_ride = {
		"insert":[rideID, uname],
		"column":["rid", "username"],
		"table": "JoinRide"
	} 
	r = requests.post(url=" http://127.0.0.1:5000/api/v1/db/read", json=J_ride)

	a = r.json()

	if(a == "Yes"):
		#Ride Exist
		return jsonify({}),400
	else:
		user = {
			"insert":[uname],
			"column":"",
			"table" : "User"
 		}
 		#check username in User table
		u = requests.post(url=" http://127.0.0.1:5000/api/v1/db/read", json=user)

		b = u.json()

		if b == "Yes":
			w = requests.post(url=" http://127.0.0.1:5000/api/v1/db/write", json=J_ride)
			if(w):
				#Ride Joined
				return jsonify({}),200
			else:
				#Write Error
				return jsonify({}),500
		else:
			#No Username
			return jsonify({}),400
	return jsonify({}),500
	#Server Error

#7. Delete a ride

@app.route('/api/v1/rides/<rideId>', methods=["DELETE"])
def delete_ride(rideId):

	if request.method != 'DELETE':
		return jsonify({}),405

	D_ride = {
		"insert" : rideId,
		"column" : "delete",
		"table" : ["Ride", "JoinRide"]
	}
	
	r = requests.post(url=" http://127.0.0.1:5000/api/v1/db/read", json=D_ride)
	a=r.json()

	if(a == "InRide" or a == "InJoin"):
		w = requests.post(url=" http://127.0.0.1:5000/api/v1/db/write", json=D_ride)
		print(w.json())
		if(w):
			#Deleted
			return jsonify({}),200
		else:
			#Server Error
			return jsonify({}),500
	else:
		#Ride Does Not Exist
		return jsonify({}),204

#8.Write to db

@app.route('/api/v1/db/write', methods=['POST'])
def DB_Write():

	if request.method != 'POST':
		return jsonify({}),405

	data=request.get_json()
	insert=data["insert"]
	column=data["column"]
	table=data["table"]
	
	#Delete Ride from Ride table (rideID is given)	
	if((table[0] == "Ride" or table[1] == "JoinRide") and column == "delete"):		
		r1 = Ride.query.get(insert)
		r2 = JoinRide.query.filter_by(rid = insert).first()
		if r1:
			db.session.delete(r1)
		if r2:
			db.session.delete(r2)
		db.session.commit()
		return jsonify("del")

	#Remove User from User table (usename is given)	
	if(table == "User" and column == "delete"):
		r = User.query.get(insert)
		db.session.delete(r)
		db.session.commit()
		return jsonify("del")
	
	#Add new User to User table 	
	if(table=="User"):
		newuser=User(username=insert[0], password=insert[1])
		try:
			db.session.add(newuser)
			db.session.commit()
		except:
			return jsonify({}),405
		return jsonify("Done"),201

	#Add new Ride to Ride table 	
	elif table=="Ride":
		now = strftime("%d-%m-%y:%S-%M-%H")
		now = "{}".format(now)
		print("inside ride")
		new_ride = Ride(timestamp=dat_str_dattime(insert[1]), username=insert[0], source=insert[2] ,destination=insert[3])
		try:
			db.session.add(new_ride)
			db.session.commit()		
		except:
			return jsonify({}),405		
		return jsonify("Done"),201

	#Join existing ride / Add existing ride by adding new row to the JoinRide column 	
	elif table == "JoinRide":
		u = "{}".format(insert[1])
		try:
			join=JoinRide(rid=insert[0], username=u)
			db.session.add(join)
			db.session.commit()
		except:
			return jsonify({}),405
		return jsonify("Done"),201

#9. Read from db

@app.route('/api/v1/db/read', methods=['POST'])
def DB_Read():

	if request.method != 'POST':
		return jsonify({}),405

	data = request.get_json()
	table = data["table"]
	column = data["column"]
	insert = data["insert"]
		
	#Read rideID before delete from Ride Table
	if(table[0] == "Ride" or table[1] == "JoinRide" ) and (column == "delete"):	
		joinResponse = JoinRide.query.filter_by(rid = insert).first() 
		RideResponse = Ride.query.get(insert)
		if RideResponse :
			return jsonify("InRide")
		elif joinResponse:
			return jsonify("InJoin")
		else:
			return jsonify("No")

	#Read username to before deleting from User Table
	elif(table == "User" and column == "delete"):	
		r = User.query.get(insert)
		if r:
			return jsonify("Yes")
		else:
			return jsonify("No")

	#Read from JoinRide table before adding new ride (given ride ID)
	elif(table == "JoinRide" ):
		ride_tab_u = JoinRide.query.get(insert[1])
		r = Ride.query.filter_by(username = insert[1]).first()
		if r:
			return jsonify("Yes")
		elif ride_tab_u:
			return jsonify("Yes")
		return jsonify("No")

	#Read username from User or Ride table befor inserting new User or Ride
	elif(table == "User"):
		name = User.query.get(insert[0])
		if name:
			return jsonify("Yes")
		else:
			return jsonify("No")

	elif (table == "Ride" and column == "get_ride"):
		s = data["source"]
		d = data["destination"]
		row = Ride.query.filter(Ride.source == s,Ride.destination == d,Ride.timestamp > datetime.now()) 
		results = [] # list of dicionaries
		for row in row:
			result = {} 
			result["rideID"] = row.rideID
			result["username"] = row.username
			str_date = row.timestamp.strftime("%d-%m-%Y:%S-%M-%H")
			result["timestamp"] = str_date		
			results.append(result)
		return json.dumps(results)

	elif table == "Ride" and column =="get_users":
		r = data["insert"]
		res = Ride.query.filter_by(rideID = r)
		res1 = JoinRide.query.filter_by(rid = r)
		users= []
		result = {}
		for row in res:
			result["rideID"] = row.rideID
			result["created_by"] = row.username
			str_date = row.timestamp.strftime("%d-%m-%Y:%S-%M-%H")
			result["timestamp"] = str_date
			for row1 in res1:
				users.append(row1.username)
			result["users"] = users
			result["source"] = row.source
			result["destination"] = row.destination
		return json.dumps(result)		


	elif table == "Ride":
		
		r = Ride.query.filter_by(username = insert[0]).first()
		
		if r: 
			return jsonify("Yes")
		else:
			return jsonify("No")
	
# Run Server
if __name__ == '__main__':
	add_enum()
	app.run(debug=True)