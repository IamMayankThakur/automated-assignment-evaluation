from flask import Flask,request, render_template,\
jsonify,request,abort
import string,requests
import MySQLdb
from constants import Area
import re 
from datetime import datetime
import datetime
import ast
import json

app=Flask(__name__)

#Function to check if password is valid
def isHex(password):
	return all(c in string.hexdigits for c in password)

#------------------1-------------------
@app.route("/api/v1/users",methods=["PUT"])

def add_user():
    
	if(request.method!="PUT"):
		abort(405,description="Method Not Allowed")
	username=request.get_json()["username"]
	password=request.get_json()["password"]
	#Read from db to check if username exists
	payload={'table':'usernames','columns':["username"],'where':'username='+"'"+username+"'"}
	r=requests.request("POST",'http://127.0.0.1:5000/api/v1/db/read',json=payload)
	catalog=json.loads(r.content.decode('utf8'))
	print(catalog)    
	#If username exists, abort
	if(len(catalog["data"])!=0):
        	abort(400,description="Bad Request")
	
	#If password doesn't match specs, abort
	if(len(password)<40 or isHex(password)!=True):
        	abort(400,description="Bad Request")

	#valid username and password, insert into database
	else:
		payload={'table':'usernames','insert':[username,password],'columns':["username","password"],'type':'INSERT'}
		r=requests.post('http://127.0.0.1:5000/api/v1/db/write',json=payload)
		return jsonify({}),201

#-------------------2------------------------
@app.route("/api/v1/users/<username>",methods=["DELETE"])

def remove_user(username):
	if(request.method!="DELETE"):
		abort(405,description="Method Not Allowed")
	
	#Validating if username exists
	payload={'table':'usernames','columns':["username"],'where':'username='+"'"+username+"'"}
	r=requests.post('http://127.0.0.1:5000/api/v1/db/read',json=payload)
	catalog=r.json()

    #Invalid username
	if(len(catalog["data"])==0):
		abort(400,description="Bad Request")

    #Valid username hence delete
	payload={'table':'usernames','insert':[username],'columns':["username"],'type':'DELETE'}
	r=requests.post('http://127.0.0.1:5000/api/v1/db/write',json=payload)
	return jsonify({}),200

#--------------------3--------------------
@app.route("/api/v1/rides",methods=["POST"])

def add_ride():

	if(request.method!="POST"):
		abort(405,description="Method Not Allowed")

	#Extracting ride details from request body
	created_by=request.get_json()["created_by"]
	timestamp=request.get_json()["timestamp"]
	try:
		y=datetime.datetime.strptime(timestamp,"%d-%m-%Y:%S-%M-%H")
	except ValueError as ve:
		abort(400,description="Bad Request")
	else:
		z=datetime.datetime.strftime(y,"%d-%m-%Y:%S-%M-%H")
	if(timestamp!=z):
		abort(400,description="Bad Request")
		
	source=request.get_json()["source"]
	destination=request.get_json()["destination"]
	area_list=[]

	#Extracting all allowed areas from constants.py
	for i in Area:
		area_list.append(i.value)
	
	#Invalid source/destination
	if(int(source) not in area_list or int(destination) not in area_list or int(source)==int(destination)):
		abort(400,description="Bad Request")
	
	#Validating timestamp 
	x=re.search("^([0-2][1-9]|[3][0-1]|([012][0-9])|(3[01]))-([0]{0,1}[1-9]|1[012])-\d\d\d\d:(20|21|22|23|[0-1]?\d)-[0-5]?\d-[0-5]?\d$",timestamp)	
	if(x == None):
		abort(400,description="Bad Request")	

	#Validating username
	payload={'table':'usernames','columns':["username"],'where':'username='+"'"+created_by+"'"}
	r=requests.post('http://127.0.0.1:5000/api/v1/db/read',json=payload)
	catalog=r.json()

	#Invalid username
	if(len(catalog["data"])==0):
		abort(400,description="Bad Request")

	#Add Ride to DB with rideId,users(list) to use in 5
	payload={'table':'ride','insert':[created_by,timestamp,created_by,str(source),str(destination)],'columns':["created_by","timestamp","users","source","destination"],'type':'INSERT'}
	r=requests.post('http://127.0.0.1:5000/api/v1/db/write',json=payload)
	return jsonify({}),201

#--------------------------4----------------------
@app.route("/api/v1/rides",methods=["GET"])

def list_rides():
	if(request.method!="GET"):
		abort(405,description="Method Not Allowed")

	#Extracting source and destination from request
	source=request.args.get('source')
	destination=request.args.get('destination')
	area_list=[]
	for i in Area:
		area_list.append(i.value)

	#Invalid source/destination
	if((int(source) not in area_list) or (int(destination) not in area_list) or (int(source)==int(destination))):
		abort(400,description="Bad Request")
	
	#Read from ride tables for all possible existing rides
	payload={'table':'ride','columns':["rideId","created_by","timestamp"],'where':'source='+"'"+source+"'"+' and '+'destination='+"'"+destination+"'"}
	r=requests.post('http://127.0.0.1:5000/api/v1/db/read',json=payload)
	catalog=r.json()
	
	#No ride exists
	if(len(catalog["data"])==0):
		return jsonify({}),204

	#Get all the rows(rideID,username,timestamp) with source and destination

	rides=[]
	cat=catalog["data"]
	present_time=datetime.datetime.now()
		
		
	for i in cat:
		date_type1=datetime.datetime.strptime(i[2],'%d-%m-%Y:%H-%M-%S')
		#If upcoming ride, add it to list of results

		if(date_type1>present_time):
			x={"rideId":i[0],"username":i[1],"timestamp":i[2]}
			rides.append(x)

	#None amongst the suitable rides are upcoming
	if (len(rides)==0):
		return jsonify({}),204
	
	#For filtering identical dictionaries
	result=[ast.literal_eval(i) for i in set(map(str,rides))] 
	#Add to rides(dictionary containing dictionaries)
	return (jsonify(result),200)

#-----------------------5---------------------
methods=["GET","POST","DELETE"]

@app.route("/api/v1/rides/<string:rideId>",methods=["GET"])

def full_details(rideId):
	if(request.method not in methods):
		abort(405,"Method Not Allowed")
	#Check for valid rideId
	payload={'table':'ride','columns':["rideId","created_by","users","timestamp","source","destination"],'where':'rideId='+str(rideId)+";"}
	r=requests.post('http://127.0.0.1:5000/api/v1/db/read',json=payload)
	catalog=r.json()
	
	#Invalid ride, empty response
	if(len(catalog["data"])==0):
		return jsonify({}),204

	#Valid rideId
	l1=[]
	for i in catalog['data']:
		if(i[2]!=i[1]):#ensuring to not add the user that created the ride
			l1.append(i[2])
	#Extracting common part of rideId, createdby, timestamp etc
	ride_details=catalog["data"][0]
	
	x={"rideId":str(ride_details[0]), "created_by" :ride_details[1],"users" : l1,"timestamp":ride_details[3],"source":ride_details[4],"destination":ride_details[5]} 
	return (jsonify(x),200)

#-------------------6-----------------------
@app.route("/api/v1/rides/<string:rideId>",methods=["POST"])

def join_ride(rideId):
	if(request.method not in methods):
		abort(405,"Method Not Allowed")
	
	#Validating user name by reading from DB
	username=request.get_json()["username"]
	payload={'table':'usernames','columns':["username"],'where':'username='+"'"+username+"'"}
	r=requests.post('http://127.0.0.1:5000/api/v1/db/read',json=payload)
	catalog=r.json()

	#Invalid username, empty response
	if(len(catalog["data"])==0):
		return jsonify({}),204

	#Validating rideId
	payload={'table':'ride','columns':["rideId","created_by","users","timestamp","source","destination"],'where':'rideId='+str(rideId)+";"}
	r=requests.post('http://127.0.0.1:5000/api/v1/db/read',json=payload)
	catalog=r.json()

	#Invalid rideId, empty response
	if(len(catalog["data"])==0):
		return jsonify({}),204

	#Joining the ride created by itself, not allowed
	for i in catalog['data']:
		if(i[2]==username):
			abort(400,description="Bad Request")
	
	#Insert entry into ride table
	payload={'table':'ride','insert':[str(catalog['data'][0][0]),catalog['data'][0][1],username,catalog['data'][0][3],catalog['data'][0][4],catalog['data'][0][5]],'columns' :["rideId","created_by","users","timestamp","source","destination"],'type':"INSERT"}
	r=requests.post('http://127.0.0.1:5000/api/v1/db/write',json=payload)
	return jsonify({}),200
	

#-------------------7---------------------------
@app.route("/api/v1/rides/<string:rideId>",methods=["DELETE"])

def delete_ride(rideId):
	if(request.method not in methods):
		abort(405,"Method Not Allowed")
	
	#Validating rideId
	payload={'table':'ride','columns':["rideId"],'where':'rideId='+str(rideId)+";"}
	r=requests.post('http://127.0.0.1:5000/api/v1/db/read',json=payload)
	catalog=r.json()

	#Invalid rideId
	if(len(catalog["data"])==0):
		abort(400,description="Bad Request")

	#Delete rideId from DB
	payload={'table':'ride','insert':[str(rideId)],'columns':["rideId"],'type':'DELETE'}
	r=requests.post('http://127.0.0.1:5000/api/v1/db/write',json=payload)
	return jsonify({}),200

#-------Database connection-------------
def connection():
	
	conn = MySQLdb.connect(host="localhost",
                           user = "root",
                           passwd = "root",
                           db = "assig1")
	c = conn.cursor()

	return c, conn

#-------------------8---------------------------
@app.route("/api/v1/db/write",methods=["POST"])

def write_db():
	c, conn = connection()
	tablename=request.get_json()["table"]
	data=request.get_json()["insert"]
	column=request.get_json()["columns"]
	type1 = request.get_json()["type"] #INSERT/DELETE/UPDATE

	col_string_1=""
	for i in column:#Columns to write to
		col_string_1=col_string_1+i+','
	col_string=col_string_1[:-1]

	val_string_1=""
	for i in data:#Data to write in corresponding columns
		val_string_1=val_string_1+"'"+i+"'"+','
	val_string=val_string_1[:-1]

	if(type1=="INSERT"):
			sql = "Insert into "+tablename+'('+col_string+')'+" values "+'('+val_string+');'
	elif(type1=="DELETE"):
			sql = "Delete from "+tablename+" Where "+column[0] +"=" +"'"+data[0]+"'"+";"
	
	c.execute(sql)
	conn.commit()
	
	return("OK",200)

#-------------------9------------------------
@app.route("/api/v1/db/read",methods=["POST"])

def read_db():
	c, conn = connection()
	tablename=request.get_json()["table"]
	column_list=request.get_json()["columns"]
	condition = request.get_json()["where"]

	col_string_1=""
	for i in column_list:
		col_string_1=col_string_1+i+','
	col_string=col_string_1[:-1]
	
	if(len(condition)!=0):#If condition specified
		sql = "select " +col_string+" from " + tablename+" where "+str(condition)+";"

	else:#General select* query
		sql = "select " +col_string+" from " + tablename+";"
	
	c.execute(sql)
	conn.commit()
	return (jsonify(data=c.fetchall()),200)

#----------------------------MAIN-----------------------------
if __name__=='__main__':
	app.debug=True
	app.run(host='0.0.0.0',port='5000')

