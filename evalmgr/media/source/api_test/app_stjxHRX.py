from flask import Flask, render_template,\
jsonify,request,abort,redirect
from flask_sqlalchemy import SQLAlchemy
import random
import csv
from datetime import datetime
import requests
import json
import time

import re

with open('AreaNameEnum.csv', mode='r') as infile:
    reader = csv.reader(infile)
    with open('coors_new.csv', mode='w') as outfile:
        writer = csv.writer(outfile)
        mydict = {rows[0]:rows[1] for rows in reader}


app=Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
db = SQLAlchemy(app)

class User(db.Model):
    username = db.Column(db.String(80), unique=True,primary_key=True)
    password = db.Column(db.String(40), nullable=False)

class Rides(db.Model):
    RideID = db.Column(db.Integer, unique=True,primary_key=True)
    Created_by = db.Column(db.String(40), nullable=False)
    #Users = db.Column(db.ARRAY(db.Integer))
    Timestamp = db.Column(db.String(20), nullable=False)
    Source = db.Column(db.Integer, nullable=False)
    Destination = db.Column(db.Integer, nullable=False)

class Share(db.Model):
	ID=db.Column(db.Integer, primary_key=True)
	RideID=db.Column(db.Integer,nullable=False)
	User=db.Column(db.String(40),nullable=False)

db.create_all()
client = app.test_client()


@app.route('/api/v1/users',methods=['PUT'])
def add_user():
	x=request.get_json()
	pattern=re.compile("^[a-fA-F0-9]{40}$")
	if(not("username" in x.keys() and "password" in x.keys())):
		abort(400,"Wrong request parameters recieved")
	user=request.get_json()["username"]
	password=request.get_json()["password"]
	if(not(pattern.match(password))):
		abort(400,"Password not valid SHA1 hash rex")

	url='/api/v1/db/read'
	obj={
		"table": "User",
		"columns": ["username","password"],
		"where": "username="+user
		}
	response = client.post(url, json=obj).get_json()
	

	check=response["info"]
	if(check):
		return "Request succesfully recieved but username already exists",200
	else:
		url='/api/v1/db/write'
		obj = {
				"insert_data": [
				{
					"col": "username",
					"data": user
				},
				{
					"col": "password",
					"data": password
				}
			],
		"table": "User"
		}
		response = client.post(url, json=obj).get_json()
	return {},201 #succesful PUT

@app.route('/api/v1/users/<username>',methods=["DELETE"])
def delete_user(username):
	url='/api/v1/db/read'
	obj={
		"table": "User",
		"columns": ["username","password"],
		"where": "username="+username
		}
	response = client.post(url, json=obj).get_json()
	check=response["info"]
	if(check):
		url='/api/v1/db/write'
		obj = {
				"delete_data": [
				{
					"col": "username",
					"data": username
				}
			],
		"table": "User"
		}
		response = client.post(url, json=obj).get_json()
		url='/api/v1/db/write'
		obj = {
				"delete_data": [
				{
					"col": "Created_by",
					"data": username
				}
			],
		"table": "Rides"
		}
		response = client.post(url, json=obj).get_json()
		url='/api/v1/db/write'
		obj = {
				"delete_data": [
				{
					"col": "User",
					"data": username
				}
			],
		"table": "Share"
		}
		response = client.post(url, json=obj).get_json()
		#db.session.delete(User.query.filter_by(username=username).first())
		#db.session.commit()
	else:
		abort(400,"Username not registered")
	return {},200

@app.route('/api/v1/rides',methods=['POST'])
def add_ride():
	x=request.get_json()
	pattern=re.compile("((0[1-9]|[12][0-9]|3[01])-(0[13578]|1[02])-(18|19|20)[0-9]{2})|(0[1-9]|[12][0-9]|30)-(0[469]|11)-(18|19|20)[0-9]{2}|(0[1-9]|1[0-9]|2[0-8])-(02)-(18|19|20)[0-9]{2}|29-(02)-(((18|19|20)(04|08|[2468][048]|[13579][26]))|2000) [0-5][0-9]:[0-5][0-9]:(2[0-3]|[01][0-9])")
	if(not("created_by" in x.keys() and "timestamp" in x.keys() and "source" in x.keys() and "destination" in x.keys())):
		abort(400,"Wrong request parameters recieved")
	username=x["created_by"]
	url='/api/v1/db/read'
	obj={
		"table": "User",
		"columns": ["username","password"],
		"where": "username="+username
		}
	response = client.post(url, json=obj).get_json()
	check=response["info"]
	if(check):
		time_=x["timestamp"]
		#if(not(pattern.match(time))):
		#	abort(400, "Timestamp is of wrong format")
		try:
			time.strptime(time_, '%d-%m-%Y:%S-%M-%H')
		except ValueError:
			abort(400, "Timestamp is of wrong format")
	
		#check valid date
		source=x["source"]
		dest=x["destination"]

		if(not(source in mydict.keys() and dest in mydict.keys()) or source==dest):
			abort(400,"Invalid source and destination codes")


		ride_id=random.randint(1000,2000)
		url='/api/v1/db/read'
		obj={
			"table": "Rides",
			"columns": ["RideID"],
			"where": ""
		}
		response = client.post(url, json=obj).get_json()
		check=response["info"]
		'''
		ride_id=random.randint(1000,2000)
		while(ride_id in list(map(lambda x:x["RideID"],check))):
			ride_id=random.randint(1000,2000)
		'''

		url='/api/v1/db/write'
		obj = {
				"insert_data": [
				#{
				#	"col": "RideID",
				#	"data": ride_id
				#},
				{
					"col": "Created_by",
					"data": username
				},
				{
					"col": "Timestamp",
					"data": time_
				},
				{
					"col": "Source",
					"data": source
				},
				{
					"col": "Destination",
					"data": dest
				}
			],
		"table": "Rides"
		}
		response = client.post(url, json=obj).get_json()
		url='/api/v1/db/write'
		obj = {
				"insert_data": [
				{
					"col": "RideID",
					"data": ride_id
				},
				{
					"col": "User",
					"data": username
				}
			],
		"table": "Share"
		}
		response = client.post(url, json=obj).get_json()
		return {},201#successful POST
	else:
		abort(400,"User doesn't exist")

@app.route('/api/v1/rides',methods=['GET'])
def list_ride():
	source = request.args.get('source')
	destination = request.args.get('destination')
	if(source=="" or destination==""):
		abort(400,"Give the required source and destination parameters")
	if(not(source in mydict.keys() and destination in mydict.keys())):
			abort(400,"Invalid source or destination codes")
	response=[]
	f=0
	url='/api/v1/db/read'
	obj={
		"table": "Rides",
		"columns": ["RideID","Created_by","Timestamp"],
		"where": "Source="+source+"&Destination="+destination
	}
	response = client.post(url, json=obj).get_json()
	try:
		check1=response["info"]
	except:
		return "hello"
	#return str(check1)
	response=[]
	for x in check1:
			f=1
			details={}
			details["rideId"]=x["RideID"]
			details["username"]=x["Created_by"]
			details["timestamp"]=x["Timestamp"]
			response.append(details)
			#return details

	if(f==0):
		return 'There are no upcoming rides from the given source to destination',204 #no content
	else:
		return jsonify(response),200

@app.route('/api/v1/rides/<rideId>',methods=['GET','POST','DELETE'])
def get_rides(rideId):
	rideId=int(rideId)
	if(request.method=='GET'):
		url='/api/v1/db/read'
		obj={
			"table": "Rides",
			"columns": ["RideID","Created_by","Timestamp","Source","Destination"],
			"where": "RideID="+str(rideId)
			}
		response = client.post(url, json=obj).get_json()
		check=response["info"][0]
		if(check):
			url='/api/v1/db/read'
			obj={
				"table": "Share",
				"columns": ["User"],
				"where": "RideID="+str(rideId)

				}
			response = client.post(url, json=obj).get_json()
			check1=response["info"]
			y=list(map(lambda x:x["User"],check1))
			y=list(filter(lambda x:x!=check["Created_by"],y))
			details={}
			details["rideId"]=check["RideID"]
			details["created_by"]=check["Created_by"]
			details["timestamp"]=check["Timestamp"]
			details["users"]=y
			details["source"]=check["Source"]
			details["destination"]=check["Destination"]
		else:
			abort(400,"Ride Id is not valid")
			details={}
		return jsonify(details),200
	
	elif(request.method=='POST'):
		x=request.get_json()
		if(not("username" in x.keys())):
			abort(400,"Wrong request parameters recieved")
		user=x["username"]
		url='/api/v1/db/read'
		obj={
			"table": "Rides",
			"columns": ["RideID"],
			"where": "RideID="+str(rideId)
			}
		response = client.post(url, json=obj).get_json()
		check=response["info"]

		url='/api/v1/db/read'
		obj={
			"table": "User",
			"columns": ["username","password"],
			"where": "username="+user
		}
		response = client.post(url, json=obj).get_json()
		check1=response["info"]

		url='/api/v1/db/read'
		obj={
			"table": "Share",
			"columns": ["RideID","User"],
			"where": "User="+user+"&RideID="+str(rideId)
		}
		response = client.post(url, json=obj).get_json()
		check2=response["info"]
		if(check2):
			abort(400,"User has already joined the ride")
		#check1=User.query.filter_by(username=user).first()
		if(check and check1):
			url='/api/v1/db/write'
			obj = {
					"insert_data": [
					{
						"col": "RideID",
						"data": rideId
					},
					{
						"col": "User",
						"data": user
					}
				],
				"table": "Share"
			}
			response = client.post(url, json=obj).get_json()
			return {},200
		else:
			abort(400,"Incorrect rideid or username")

	elif(request.method=='DELETE'):
		url='/api/v1/db/read'
		obj={
			"table": "Rides",
			"columns": ["RideID"],
			"where": "RideID="+str(rideId)
			}
		response = client.post(url, json=obj).get_json()
		check=response["info"]
		if(not(check)):
			abort(400,"RideId is incorrect")
		else:
			url='/api/v1/db/write'
			obj = {
					"delete_data": [
					{
						"col": "RideID",
						"data": rideId
					}
					],
				"table": "Rides"
				}
			response = client.post(url, json=obj).get_json()
			url='/api/v1/db/write'
			obj = {
					"delete_data": [
						{
						"col": "RideID",
						"data": rideId
						}
					],
				"table": "Share"
			}
			response = client.post(url, json=obj).get_json()
			
		return {},200
	else:
		abort(405,"Wrong method")
		  

@app.route('/api/v1/db/write',methods=['POST'])
def write_db():
	x=request.get_json()
	if("insert_data" in x):
		insert_data=x["insert_data"]
		tab=x["table"]
		newentry=eval(tab)()
		#return str(newentry)
		for i in insert_data:
			hi=i["col"]
			setattr(newentry,hi,i["data"])
		db.session.add(newentry)
	elif("delete_data" in x):
		delete_data=x["delete_data"]
		tab=eval(x["table"])
		d1=getattr(tab,delete_data[0]["col"])
		x=tab.query.filter(d1==delete_data[0]["data"]).delete()
		#db.session.delete(x)
	db.session.commit()
	return '',200

@app.route('/api/v1/db/read',methods=['POST'])
def read_db():
	x=request.get_json()
	flag=0
	cols=x["columns"]
	tab=eval(x["table"])
	if(not(x["where"])):
		q=tab.query.all()
	else:
		if('&' in x["where"]):
			d_form="%d-%m-%Y:%S-%M-%H"
			curr_time=time.strftime(d_form)
			
			#return {"info":[curr_time]}
			sp=x["where"].split('&')
			lhs1=sp[0].split("=")[0]
			d1=getattr(tab,lhs1)
			rhs1=sp[0].split("=")[1]
			lhs2=sp[1].split("=")[0]
			d2=getattr(tab,lhs2)
			rhs2=sp[1].split("=")[1]
			if(x["table"]=="Share"):
				q=tab.query.filter((d1==rhs1)&(d2==rhs2)).all()
			else:
				flag=1
				d3=getattr(tab,"Timestamp")
				d4=getattr(tab,"RideID")
				#return {"info":"hi"}
				#q=tab.query.filter((d1==rhs1)&(d2==rhs2)&((datetime.strptime(getattr(tab,"Timestamp"),d_form)-datetime.strptime(curr_time,d_form)).total_seconds()>0)).all()
				q=tab.query.filter((d1==rhs1)&(d2==rhs2)).all()
				#return {"info":[hi]}

		else:
			lhs=x["where"].split("=")[0]
			d=getattr(tab,lhs)
			rhs=x["where"].split("=")[1]
			q=tab.query.filter(d==rhs).all()
	response={"info":[]}
	for j in q:
		#return {"info":str(j)}
		temp={}
		for i in cols:
			col=i
			if(i=="Timestamp" and flag==1):
				if((datetime.strptime(getattr(j,i),d_form)-datetime.strptime(curr_time,d_form)).total_seconds()>0):
					temp[i]=getattr(j,i)
					continue
				else:
					temp={}
					break
				#return {"info":str(type(getattr(j,i)))}
			temp[i]=getattr(j,i)
		if(temp):
			response["info"].append(temp)
	return response
if __name__ == '__main__':	
	app.debug=True
	app.run()