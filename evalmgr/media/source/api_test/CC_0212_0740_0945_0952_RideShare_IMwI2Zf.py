from flask import Flask, request , jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import INTEGER
#from werkzeug.security import generate_password_hash ,check_password_hash
#import uuid
import requests
import re
import constants
import datetime

app = Flask(__name__)

#{"created_by" : "shreya","timestamp" : "02-02-2020:18-29-12", "source":"123","destination":"12"}

#app.config['SECRET_KEY'] = 'thisissecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///a1.db'

# Tables Creation : 
db = SQLAlchemy(app)
UnsignedInt = db.Integer()
UnsignedInt = UnsignedInt.with_variant(INTEGER(unsigned=True), 'sqlite')

class Users(db.Model):
	username = db.Column(db.String,primary_key = True, nullable=False)
	password = db.Column(db.String, nullable = False)

class Rides(db.Model):
	rideId = db.Column(UnsignedInt,primary_key = True,autoincrement = True)
	created_by = db.Column(db.String, nullable = False)
	timestamp = db.Column(db.String, nullable = False)
	source = db.Column(db.Integer, nullable = False)
	destination = db.Column(db.Integer, nullable = False)
	users_list = db.Column(db.String)

class Userrides(db.Model):
	id = db.Column(db.Integer,primary_key = True)
	rideId = db.Column(UnsignedInt,nullable=False)
	username = db.Column(db.String,nullable=False)

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# API to Write Database :

@app.route('/api/v1/db/write',methods = ['POST'])
def write_to_db():
	data = request.get_json()
	op1 = data['op']
	tab1=data['table']

	if (op1=='Insert'):
		col1 = data['column']
		val1 = data['value']
		l = len(col1)
		query = 'eval(tab1)('
		for i in range(l):
			query += col1[i] + '='+ '\'' + val1[i] + '\'' + ','
		query = query.strip(',')
		query += ')'
		new_user = eval(query)
		db.session.add(new_user)
		db.session.commit()
		return jsonify({'Error' : 'insertion complete'})


	elif(op1=="Delete"):
		
		conds = data['where'].split(',')
		query = 'eval(tab1).query.filter_by('
		for i in (conds):
			x = i.split('=')
			query += x[0] +'='+'\''+x[1]+'\''+','
		query = query.strip(',')
		query += ').all()'
		del_user = eval(query)
		for du in del_user:
			db.session.delete(du)
		db.session.commit()
		return jsonify({'Error' : 'deletion complete'})
		#query = eval(tab1).query.filter_by(w='').update(dict(email=''))
	
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# API to Read Database :
	
@app.route('/api/v1/db/read',methods = ['POST'])
def read_from_db():
	data = request.get_json()
	tab1=data['table']
	col1 = data['columns']
	conds = data['where'].split(',')
	query = 'eval(tab1).query.filter_by('
	for i in conds:
		x = i.split('=')
		query += x[0] +'='+'\''+x[1]+'\''+','
	query = query.strip(',')
	query += ').with_entities('
	for i in range(len(col1)):
		query+= 'eval(tab1).'+col1[i]+','
	query = query.strip(',')
	query+= ').all()'
	read_user = eval(query)

	#read_user=Users.query.filter_by(username='shreya').with_entities(Users.username,Users.password).all()
	return jsonify(read_user)

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# API to Add User :

@app.route('/api/v1/users',methods = ['PUT'])
def add_user():
	if request.method != 'PUT':
    		return jsonify({}),405
	data = request.get_json()

	try :
		cond = "username =" + data["username"]
		reply = list(requests.post("http://127.0.0.1:5000/api/v1/db/read",json = {"table":"Users","columns":["username"],"where": cond }).json())
	
	except :
		return jsonify({"Error":" Invalid request body"}),400

	l=len(reply)
	if(l==0):
		#k=re.compile(1
		if(len(data['password'])==40):
			m=re.findall("[a-fA-F0-9]{40}",data['password']) 
			#return jsonify(m)
			if(len(m)!=0 and len(m[0])==40 ):
				ans = requests.post("http://127.0.0.1:5000/api/v1/db/write",json ={"op":"Insert","table":"Users","column":["username","password"],"value":[data['username'],data['password']]})
				return jsonify({}),201
			else:
				return jsonify({"Error":"Password not in SHA1 hash hex format"}),400
		else:
			return jsonify({"Error":"Password not in SHA1 hash hex format"}),400
	else:
		return jsonify({"Error":"Username exists"}),400

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# API to remove user :

@app.route('/api/v1/users/<string:username>',methods = ['DELETE'])
def remove_user(username):
	if request.method != 'DELETE':
    		return jsonify({}),405

	cond = "username =" + username
	reply = list(requests.post("http://127.0.0.1:5000/api/v1/db/read",json = {"table":"Users","columns":["username"],"where": cond }).json())
	l=len(reply)
	#return jsonify(l)
	if(l==1):
		cond_r = "created_by =" + username
		c_ride_id = list(requests.post("http://127.0.0.1:5000/api/v1/db/read",json = {"table":"Rides","columns":["rideId"],"where": cond_r }).json())
		for c in c_ride_id:
			rc = 'rideId ='+str(c[0])
			a = requests.post("http://127.0.0.1:5000/api/v1/db/write",json ={"op":"Delete","table":"Userrides","where":rc}).json()
		rem_r = requests.post("http://127.0.0.1:5000/api/v1/db/write",json ={"op":"Delete","table":"Rides","where":cond_r}).json()
		cond_r_u = "username =" + username
		rem_r_u = requests.post("http://127.0.0.1:5000/api/v1/db/write",json ={"op":"Delete","table":"Userrides","where":cond_r_u}).json()
		rem_u = requests.post("http://127.0.0.1:5000/api/v1/db/write",json ={"op":"Delete","table":"Users","where":cond}).json()

		return jsonify({}),200
	else:
		return jsonify({"Error":"Username does not exist"}),400


#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# API to Create ride :

@app.route('/api/v1/rides',methods = ['POST'])
def create_ride():
	if request.method != 'POST':
    		return jsonify({}),405
	
	data = request.get_json()
	
	try :
		cond = "username =" + data["created_by"]
		ts = data['timestamp']
		tf = '%d-%m-%Y:%S-%M-%H'
		s = int(data['source'])
		d = int(data['destination'])
	except :
		return jsonify({"Error":"Invalid request body"}),400

	values = [item.value for item in constants.Places]
	#return jsonify(values)

	# Checking if source and destination is valid
	if(s not in values):
		return jsonify({"Error":"Invalid source"}),400
	if(d not in values):
		return jsonify({"Error":"Invalid destination"}),400
	if(s==d):
		return jsonify({"Error":"Source and destination can't be same"}),400
	
	# Checking if timestamp is valid and in proper format
	try:
		datetime.datetime.strptime(ts,tf)
	except:
		return jsonify({"Error":"Invalid timestamp. Enter valid date and time or try entering in the format DD-MM-YYYY:SS-MM-HH"}),400
		
	cond = "username =" + data["created_by"]
	reply = list(requests.post("http://127.0.0.1:5000/api/v1/db/read",json = {"table":"Users","columns":["username"],"where": cond }).json())
	l=len(reply)
	if(l==1):
		ans = requests.post("http://127.0.0.1:5000/api/v1/db/write",json ={"op":"Insert","table":"Rides","column":["created_by","timestamp","source","destination"],"value":	[data['created_by'],data['timestamp'],data['source'],data['destination']]})
		return jsonify({}),201
			
	else:
		return jsonify({"Error":"Username does not exist"}),400


#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# API to List upcoming rides
		
	
@app.route('/api/v1/rides',methods=["GET"])
def up_rides():
	if request.method != 'GET':
    		return jsonify({}),405

    # Checking for source and destination in url
	try:
		s=request.args['source']
		d=request.args['destination']
	except:
		return jsonify({"Error":"Source and destination not provided"}),400

	s = int(s)
	d = int(d)
	values = [item.value for item in constants.Places]

	# Checking for valid source and destination
	if(s not in values):
		return jsonify({"Error":"Invalid source"}),400
	if(d not in values):
		return jsonify({"Error":"Invalid destination"}),400
	if(s==d):
		return jsonify({"Error":"Source and destination can't be same"}),400
	
	cond = "source="+ str(s) +","+"destination="+ str(d)
	#return jsonify(cond)
	reply = list(requests.post("http://127.0.0.1:5000/api/v1/db/read",json = {"table":"Rides","columns":["rideId","created_by","timestamp"],"where": cond }).json())
	#return jsonify(reply)

	# CHecking if time is greater than current time
	tf = '%d-%m-%Y:%S-%M-%H'
	t = datetime.datetime.now()
	ct = t.strftime(tf)
	for r in reply:
		if(datetime.datetime.strptime(r[2],tf)< datetime.datetime.strptime(ct,tf)):
			reply.remove(r)

	no_of_rows = len(reply)
	if(no_of_rows == 0):
		return jsonify({}),204
		
	else:
		output = []
		for r in reply:
			ride = {}
			ride['rideId'] = r[0]
			ride['username'] = r[1]
			ride['timestamp'] = r[2]
			output.append(ride)
		return jsonify(output),200

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# API to get details of rides
		

@app.route('/api/v1/rides/<rideId>',methods = ['GET'])
def details_of_ride(rideId):
	if request.method != 'GET':
    		return jsonify({}),405
	
	try:
		cond = "rideId =" + rideId
	except :
		return jsonify({"Error":"RideID not provided"}),400
	
	reply1 = list(requests.post("http://127.0.0.1:5000/api/v1/db/read",json = {"table":"Rides","columns":["rideId","created_by","timestamp","source","destination"],"where": cond }).json())
	reply2 = list(requests.post("http://127.0.0.1:5000/api/v1/db/read",json = {"table":"Userrides","columns":["username"],"where": cond }).json())
	l1 = len(reply1)
	l2 = len(reply2)
	s = {}
	if(l1 != 0):
		output = []
		username = []
		for u in reply2:
			username.extend(u)
			
		for i in reply1:
			s['rideId'] = str(i[0])
			s['created_by'] = str(i[1])
			s['users'] = username
			s['timestamp'] = str(i[2])
			s['source'] = str(i[3])
			s['destination'] = str(i[4])
		
			return jsonify(s),200
		
	else:
		return jsonify({"Error":"RideId does not exist"}),400
	#return jsonify(reply1)	

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# API to Join existing rides :

@app.route('/api/v1/rides/<rideId>',methods = ['POST'])
def join_ride(rideId):
	if request.method != 'POST':
		return jsonify({}),405

	try:
		cond = "rideId =" + rideId
	except :
		return jsonify({"Error":"RideID not provided"}),400

	data = request.get_json()

	try:
		cond1 = "username =" + data['username']
	except :
		return jsonify({"Error":"Username not provided"}),400

	# Reading db for rides with relevant ride id:
	cond = "rideId =" + rideId
	reply1 = list(requests.post("http://127.0.0.1:5000/api/v1/db/read",json = {"table":"Rides","columns":["rideId"],"where": cond }).json())
	if(len(reply1) == 0):
		return jsonify({"Error":"Ride Id doesnt exist"}),400

	cond1 = "username =" + data['username']
	reply2 = list(requests.post("http://127.0.0.1:5000/api/v1/db/read",json = {"table":"Users","columns":["username"],"where": cond1 }).json())
	if(len(reply2) == 0):
		return jsonify({"Error":"Username doesnt exist"}),400
	reply3 = list(requests.post("http://127.0.0.1:5000/api/v1/db/read",json = {"table":"Rides","columns":["created_by"],"where": cond }).json())
	cu = str(reply3[0]).strip('[').strip(']').strip('\'')
	if(cu==data['username']):
		return jsonify({"Error":"Ride creator can't join ride"}),400
	
	reply4 = requests.post("http://127.0.0.1:5000/api/v1/db/read",json = {"table":"Userrides","columns":["username"],"where": cond }).json()
	flag =1
	for i in reply4:
		#return jsonify(i)
		if(data['username']==i[0]):
			flag=0
	if(flag):
		ans = requests.post("http://127.0.0.1:5000/api/v1/db/write",json ={"op":"Insert","table":"Userrides","column":["rideId","username"],"value":[rideId,data['username']]})
		return jsonify({}),200
	else:
		return jsonify({"Error":"User already present in the ride"}),400

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# API to delete rides :
	
@app.route('/api/v1/rides/<rideId>', methods = ['DELETE'])	
def delete_ride(rideId):
	if request.method != 'DELETE':
    		return jsonify({}),405
	try:
		cond = "rideId =" + rideId
	except :
		return jsonify({"Error":"RideID not provided"}),400

	reply = list(requests.post("http://127.0.0.1:5000/api/v1/db/read",json = {"table":"Rides","columns":["rideId"],"where": cond }).json())
	l = len(reply)
	if(l == 1):
		ans = requests.post("http://127.0.0.1:5000/api/v1/db/write",json ={"op":"Delete","table":"Rides","where":cond}).json()
		ans = requests.post("http://127.0.0.1:5000/api/v1/db/write",json ={"op":"Delete","table":"Userrides","where":cond}).json()
		return jsonify({}),200
	else:
		return jsonify({"Error":"Invalid Ride id"}),400
	

'''
@app.route('/api/v1/rides/<rideId>',methods = ['GET'])
def details_of_ride(rideId):
	if request.method != 'DELETE':
    		return jsonify({"Error":"Method not allowed"}),405
	
	cond = "rideId =" + rideId
	
	reply = list(requests.post("http://127.0.0.1:5000/api/v1/db/read",json = {"table":"Rides","column":["rideId","created_by","timestamp","source","destination"],"where": cond }).json())
	l = len(reply)
	if(l != 0):
		output = []
		username = []
		for u in reply:
			username.extend(u.created_by)
			
		s = {}
		s["rideId"] = reply[0]["rideId"]
		s["created_by"] = reply[0]["created_by"]
		s["users"] = username
		s["timestamp"] reply[0]["timestamp"]
		s["source"] = reply[0]["source"]
		s["destination"] = reply[0]["destination"]
		
		return 
		
	else:
		return jsonify({"Error":"rideId doesnt exist"}),400

@app.route('/api/v1/rides/<rideId>',methods = ['POST'])
def join_ride(rideId):
	if request.method != 'POST':
    		return jsonify({"Error":"Method not allowed"}),405
    		
    	data = request.get_json()
    	
    	cond1 = "rideId =" + rideId
    	cond2 = "username =" + data['username']
	
	reply1 = list(requests.post("http://127.0.0.1:5000/api/v1/db/read",json = {"table":"Rides","column":["rideId"],"where": cond1 }).json())
	reply2 = list(requests.post("http://127.0.0.1:5000/api/v1/db/read",json = {"table":"Users","column":["username"],"where": cond2 }).json())
	if(len(reply1)==1 and len(reply2)==1):
		ans = requests.post("http://127.0.0.1:5000/api/v1/db/write",json ={"op":"Insert","table":"UserRide","column":["rideId","username"],"value":[data['username'],data['password']]})
			return jsonify({"Error":"Insertion done"}),201

	
def get_rides(source,destination):
	if request.method != 'GET':
    		return jsonify(405)
    	
    	#-------------------------------------------------------------------------------
    	#Check for the valid source and destination
    	
	reply = requests.post("http://127.0.0.1.5000/api/v1/db/read",json = {'table':'Sode','columns':['area'],'where':'areaname'})
	exist = len(reply)
	#exist holds the int value saying 2 => both s&d exist, 0 => both s&d not valid, 1 => anyone exist
	if(exist != 2):
		return #bad request
	
	#--------------------------------------------------------------------------------
	#Get the rides for given source and destination
	
	s_cond = 'source = '+ source
	d_cond = 'destination = '+ destination
	condition = s_cond + d_cond
	
	ans = requests.post("http://127.0.0.1:5000/api/v1/db/read",json = {'table':'Rides','columns':['source','destination'],'where':condition})
	#read will give the output
	no_of_rows = len(ans)
	if(no_of_rows == 0):
		return #204 if works fine but no row satisfy the condition that is No content
	else:
		return #200 if works fine	
'''		
@app.route('/api/v1/user',methods = ['GET'])
def get_all():
	users = Userrides.query.all()
	output = []

	for u in users:
		user_data = {}
		
		user_data['username'] = u.username
		user_data['rideId'] = u.rideId
		output.append(user_data)
	return jsonify({"users" : output})


@app.route('/api/v1/r')
def get():
	users = Rides.query.all()
	output = []

	for u in users:
		user_data = {}
		
		user_data['rideId'] = u.rideId
		user_data['created_by'] = u.created_by
		user_data['source'] = u.source
		user_data['destination'] = u.destination
		user_data['timestamp'] = u.timestamp
		output.append(user_data)
	return jsonify({"users" : output})


if __name__=='__main__':
	app.run(debug=True)
	
	
