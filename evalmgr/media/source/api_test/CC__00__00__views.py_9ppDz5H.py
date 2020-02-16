from flask import Flask,url_for,redirect, render_template,jsonify,request,abort	
from datetime import datetime
import requests
import sqlite3
from sqlite3 import Error
import re

METHODS = ["GET","POST","PUT","PATCH","DELETE","COPY","HEAD","OPTIONS","LINK","UNLINK","PURGE","LOCK","UNLOCK","PROPFIND","VIEW"]
# now = datetime.now().strftime("%d-%m-%Y:%S-%M-%H")

def checkdatetime(todb):
	nowtime=datetime.now()
	try:
		todb=datetime.strptime(todb,"%d-%m-%Y:%S-%M-%H")
		if(nowtime<todb):
			return 1
		return 0
	except:
		return 0
    

app=Flask(__name__)

conn = sqlite3.connect('Ride.db',check_same_thread=False)
if(not conn):
	abort(500)

conn.execute("PRAGMA foreign_keys=ON")

#user table
conn.execute('''CREATE TABLE IF NOT EXISTS Users(
           username TEXT PRIMARY KEY NOT NULL,
           password TEXT NOT NULL
            );''')


#Rides table
conn.execute('''CREATE TABLE IF NOT EXISTS Rides(
	rideId INTEGER  PRIMARY KEY,
	username TEXT NOT NULL ,
	"timestamp" DATETIME NOT NULL,
	source INTEGER NOT NULL,
	destination INTEGER NOT NULL,
	CONSTRAINT "usr" FOREIGN KEY (username) REFERENCES Users(username) ON DELETE CASCADE
	);''')


#join rides table
conn.execute('''CREATE TABLE IF NOT EXISTS JoinRides(
	rideId INT NOT NULL,
	username TEXT PRIMARY KEY ,
	CONSTRAINT "ride" FOREIGN KEY (rideId) REFERENCES Rides(rideId) ON DELETE CASCADE,
	CONSTRAINT "user" FOREIGN KEY (username) REFERENCES Users(username) ON DELETE CASCADE
	);''')

def read_csv():
    f=open("AreaNameEnum.csv","r")
    k=f.read().splitlines()
    a=[]
    b=dict()
    for i in k[1:]:
        l=i.split(",")
        l[0]=int(l[0])
        b[l[0]]=l[1]
    # print(b)
    return b

def password_sha1_check(pwd):
	matches=re.findall("^[A-Fa-f0-9]{40}$",pwd)
	if(len(matches)==1):
		return 1
	return 0


def get_with_and(cond):
	c=[]
	for i in cond:
		a=i.split("=")
		b="'{}'".format(a[1])
		c.append(a[0]+" = "+b)
	c=" AND ".join(c)
	return c


@app.route('/api/v1/users',methods=["PUT"])
def adduser():
	'''
	Input
	{
	"username":"user5",
	"password":"password1"
	}
	'''
	# if request.method!='PUT':
	# 	return jsonify({}),405

	d=request.get_json()
	username=d["username"]
	password=d["password"]

	#check for null username
	if(not username):
		return jsonify({}),400

	table="Users"
	to_pass={
	"table":table,
	"columns":["username"],
	"where":["username={}".format(username)]
	}

	read_req=requests.post(url='http://127.0.0.1:5000/api/v1/db/read',json=to_pass)
	data=read_req.json()

	#username already exists
	if(data):
		return jsonify({}),400

	if(not password_sha1_check(password)):
		return jsonify({}),400
	write_data={
		"action": "insert",
		"insert" : [username,password],
		"column" : ["username","password"],
		"table" : table
	}
	write_req=requests.post(url="http://127.0.0.1:5000/api/v1/db/write",json=write_data)
	data=write_req.json()
	if(data == "500"):
		return jsonify({}),500

	return jsonify({}),201


@app.route('/api/v1/users/<user_name>',methods=["DELETE"])
def removeuser(user_name):
	# if request.method!='DELETE':
	# 	return jsonify({}),405

	# if(user_name==None):
	#     return jsonify({}),400

	table='Users'
	to_pass={
		"table":table,
		"columns":["username"],
		"where":["username={}".format(user_name)]
	}
	read_req=requests.post(url='http://127.0.0.1:5000/api/v1/db/read',json=to_pass)
	data=read_req.json()

	#username not present
	if(not data):
		return jsonify({}),404

	#delete user
	write_data={
		"action":"delete",
		"table" : table,
		"where" : ["username={}".format(user_name)]
	}

	write_req1=requests.post(url="http://127.0.0.1:5000/api/v1/db/write",json=write_data)
	data=write_req1.json()
	if(data == "500"):
		return jsonify({}),500

	#get rideid of user from rides table in order to delete entire ride from joinrides table
	to_pass={
		"table":"Rides",
		"columns":["rideid"],
		"where":["username={}".format(user_name)]
	}
	read_req2=requests.post(url='http://127.0.0.1:5000/api/v1/db/read',json=to_pass)
	data1=read_req2.json()

	#delete from rides table
	write_data={
		"action":"delete",
		"table" : "Rides",
		"where" : ["username={}".format(user_name)]
	}

	write_req2=requests.post(url="http://127.0.0.1:5000/api/v1/db/write",json=write_data)
	data=write_req2.json()
	if(data == "500"):
		return jsonify({}),500


	write_data={
		"action":"delete",
		"table" : "JoinRides",
		"where" : ["username={}".format(user_name)]
	}

	write_req3=requests.post(url="http://127.0.0.1:5000/api/v1/db/write",json=write_data)
	data=write_req3.json()
	if(data == "500"):
		return jsonify({}),500

	#delete from joinrides table
	if(data1):
		rideid = data1[0]['rideid']
		write_data={
			"action":"delete",
			"table" : "JoinRides",
			"where" : ["rideid={}".format(rideid)]
		}

		write_req3=requests.post(url="http://127.0.0.1:5000/api/v1/db/write",json=write_data)
		data=write_req3.json()
		if(data == "500"):
			return jsonify({}),500

	return jsonify({}),200


@app.route('/api/v1/rides',methods=["POST"])
def newride():
	
	'''
	Input
	{
		"created_by":"user1",
		"timestamp":"23-12-2020:12-12-12",
		"source":23,
		"destination":24
	}
	'''
	# if request.method!='POST':
	# 	return jsonify({}),405

	d=request.get_json()
	user_created=d["created_by"]
	ts=d["timestamp"]
	source=d["source"]

	destination=d["destination"]

	l=read_csv()

	if(not checkdatetime(ts)):
		return jsonify({}),400

	if(int(source) not in l.keys() or int(destination) not in l.keys()):
		return jsonify({}),400

	table="Rides"
	to_pass={
		"table":"Users",
		"columns":["username"],
		"where":["username={}".format(user_created)]
	}
	
	read_user=requests.post(url="http://127.0.0.1:5000/api/v1/db/read",json=to_pass)
	to_ride_table={
		"table":table,
		"columns":["username"],
		"where":["username={}".format(user_created)]
	}
	read_copy_user=requests.post(url="http://127.0.0.1:5000/api/v1/db/read",json=to_ride_table)
	
    #not a user
	if(not read_user.json()	):
		return jsonify({}),400

    #source and destination are the same
	if(source==destination):
		return jsonify({}),400	

    #duplicate rides not allowed
	if(read_copy_user.json()):
		return jsonify({}),400

	to_write={
		"action":"insert",
		"insert":[user_created,ts,source,destination],
		"column":["username","timestamp","source","destination"],
		"table":table		
	}
	write_to_ride=requests.post(url="http://127.0.0.1:5000/api/v1/db/write",json=to_write)
	data=write_to_ride.json()
	if(data == "500"):
		return jsonify({}),500
	return jsonify({}),201


@app.route('/api/v1/rides',methods=["GET"])
def upcomingrides():
	# if request.method!='GET':
	# 	return jsonify({}),405

	l=read_csv()

	#check if source and dest exist
	source=request.args.get('source')
	destination=request.args.get('destination')
	if(source is None or destination is None):
		return jsonify({}),400

	#source and dst not in file and int('string') error
	try:
		if(int(source) not in l.keys() or int(destination) not in l.keys()):
			return jsonify({}),404	
	except :
		print("hi")
		return jsonify({}),400

	table="Rides"
	to_pass={
		"table":table,
		"columns":["rideId","username","timestamp"],
		"where":["source={}".format(source),"destination={}".format(destination)]
	}

	read_req=requests.post(url='http://127.0.0.1:5000/api/v1/db/read',json=to_pass)
	data=read_req.json()

	ret=[]
	if data:
		for i in data:
			if(checkdatetime(i["timestamp"])):
				ret.append(i)
		# return jsonify(ret),200
	if(ret):
		return jsonify(ret),200

	#if no rides present
	return jsonify({}),204


@app.route('/api/v1/rides/<rideId>',methods=["GET"])
def listdetailsride(rideId):
	# if request.method!='GET':
	# 	return jsonify({}),405

	#check if rideid exists
	table="Rides"
	to_pass={
		"table":table,
		"columns":["rideId","username","timestamp","source","destination"],
		"where":["rideId={}".format(rideId)]
	}
	read_req=requests.post(url='http://127.0.0.1:5000/api/v1/db/read',json=to_pass)
	data=read_req.json()

	#rideid doesn't exist
	if(not data):
		return jsonify({}),400
	
	# l=read_csv()
	# # print(l)
	# sr,dt=l[int(data[0]['source'])],l[int(data[0]['destination'])]
	# data[0]['source'],data[0]['destination']=sr,dt


	#username => createdby
	Created_by=data[0]['username']
	data[0].pop('username',None)
	data[0]['Created_by']=Created_by

	#get all users of given ride
	table="JoinRides"
	to_pass_join={
		"table":table,
		"columns":["username"],
		"where":["rideid={}".format(rideId)]
	}
	read_req2=requests.post(url='http://127.0.0.1:5000/api/v1/db/read',json=to_pass_join)
	users=read_req2.json()

	joinedUsers = []
	for i in users:
		joinedUsers.append(i['username'])

	data[0]['users']=joinedUsers
	return jsonify(data[0]),200


@app.route('/api/v1/rides/<rideId>',methods=["POST"])
def joinride(rideId):
	# if request.method!='POST':
	# 	return jsonify({}),405
	
	username = request.get_json()["username"]

	#check if username exists
	table='Users'
	to_pass={
		"table":table,
		"columns":["username"],
		"where":["username={}".format(username)]
	}
	read_req=requests.post(url='http://127.0.0.1:5000/api/v1/db/read',json=to_pass)
	data=read_req.json()
	
    #user not present
	if(not data):
		return jsonify({}),400

	#check if rideid exists and also if the user is again joining the same ride
	table='Rides'
	to_pass={
		"table":table,
		"columns":["rideid","username"],
		"where":["rideid={}".format(rideId)]
	}
	read_req=requests.post(url='http://127.0.0.1:5000/api/v1/db/read',json=to_pass)
	data2=read_req.json()
	check_user_in_ridetable={
		"table":table,
		"columns":["rideid","username"],
		"where":["username={}".format(username)]
	}
	read_req2=requests.post(url='http://127.0.0.1:5000/api/v1/db/read',json=check_user_in_ridetable)
	data3=read_req2.json()
    
    #rideid not present
	if(not data2):
		return jsonify({}),400

    #already in ride 
	if(data3):
		return jsonify({}),400

	#add user to the specified ride
	table="JoinRides"
	write_data={
		"action":"insert",
		"insert":[rideId,username],
		"column":["rideId","username"],
		"table":table	
	}
	write_req=requests.post(url="http://127.0.0.1:5000/api/v1/db/write",json=write_data)
	data=write_req.json()
	if(data == "500"):
		return jsonify({}),500

	return jsonify({}),200


@app.route('/api/v1/rides/<rideId>',methods=["DELETE"])
def deleteride(rideId):
	# if request.method!='DELETE':
	# 	return jsonify({}),405

	#check if rideid exists
	table='Rides'
	to_pass={
		"table":table,
		"columns":["rideid"],
		"where":["rideid={}".format(rideId)]
	}
	read_req=requests.post(url='http://127.0.0.1:5000/api/v1/db/read',json=to_pass)
	data=read_req.json()
	
    #rideid not present
	if(not data):
		return jsonify({}),400
	
	#Delete a ride from Rides TABLE(it should automatically delete from joinrides table)
	write_data={
		"action":"delete",
		"table" : table,
		"where" : ["rideid={}".format(rideId)]
	}
	
	write_req1=requests.post(url="http://127.0.0.1:5000/api/v1/db/write",json=write_data)
	data=write_req1.json()
	if(data == "500"):
		return jsonify({}),500

	#delete users from joinrides table
	write_data={
		"action":"delete",
		"table" : "JoinRides",
		"where" : ["rideid={}".format(rideId)]
	}
	
	write_req2=requests.post(url="http://127.0.0.1:5000/api/v1/db/write",json=write_data)
	data=write_req2.json()
	if(data == "500"):
		return jsonify({}),500

	return jsonify({}),200


@app.route('/api/v1/db/read',methods=["POST"])
def read():

    '''
    {
    "table" : "Users",
    "columns" : ["username","password"],
    "where" : "username=user1"
    }

    '''
    d=request.get_json()
    table=d["table"]
    column_to_select=d["columns"]

    cs=column_to_select

    t=len(column_to_select)

    column_to_select= ",".join(column_to_select)

    cond=d["where"]

    c=get_with_and(cond)

    query="SELECT "+column_to_select+" FROM "+table+" WHERE "+"( "+c+");"
    try:
        result=conn.execute(query)
        b=[]
        j=0
        for i in result:
            a=dict()
            for j in range(t):
                a[cs[j]]=i[j]
            b.append(a)
        
        return jsonify(b),200

    except Error as e:
        return jsonify("500"),500

@app.route('/api/v1/db/write',methods=["POST"])
def write():
	'''
	Input
	{
	"insert" : ["user1","password1"],
	"column" : ["username","password"],
	"table" : "Users"
	}
	'''
	conn = sqlite3.connect('Ride.db',check_same_thread=False)
	if(not conn):
		return jsonify({}),500

	d=request.get_json()
	action = d["action"]

	if(action == "insert"):
		data=d["insert"]
		data=",".join("'{}'".format(i) for i in data)
		column=",".join(d["column"])
		table=d["table"]
		query="INSERT INTO "+table+" (" +column+ ") "+"VALUES ( " + data + " );"
	
	else:
		table = d["table"]
		cond=d["where"]
		c=get_with_and(cond)
		query="DELETE FROM "+table+" WHERE "+"( "+c+");"

	try:
		conn.execute(query)
		conn.commit()
		conn.close()
		return jsonify({}),200

	except Error as e:

		return jsonify("500"),500


if(__name__=="__main__"):
    app.run(debug=True)
