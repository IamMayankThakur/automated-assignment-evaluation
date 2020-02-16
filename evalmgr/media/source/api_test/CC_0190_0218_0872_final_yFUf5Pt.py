from flask import Flask, render_template,jsonify,request,abort,Response
from sqlalchemy import create_engine
import re
import datetime
from datetime import datetime
import json
from sqlalchemy.sql import text
from collections import OrderedDict
import requests
import random
import datetime

# Scheme: "postgres+psycopg2://<USERNAME>:<PASSWORD>@<IP_ADDRESS>:<PORT>/<DATABASE_NAME>"
DATABASE_URI = 'postgres+psycopg2://postgres:postgres@localhost:5432/rideshare'
db = create_engine(DATABASE_URI)
db.execute("CREATE TABLE IF NOT EXISTS userdata (uname text, pwd text, created_ride text)")
db.execute("CREATE TABLE IF NOT EXISTS rides (rideId INT,created_by text,passengers text[],source text, dest text, time_stamp timestamp)")

app=Flask(__name__)


#1)Add user
@app.route('/api/v1/users',methods=["PUT"])
def add_user():

	if not request.json:
		abort(400,description="Mention userdetails in request")
	 
	
	u_name=request.get_json()["username"]
	u_pwd=request.get_json()["password"]
	
	pass_data={"table":"userdata","columns":"uname,pwd,created_ride","where":"uname="+"'"+str(u_name)+"'"}
	pass_api="http://localhost:5000/api/v1/db/read/"
	r=requests.post(url=pass_api,json=pass_data)
	resp=r.text
	resp=json.loads(resp)
	

	pattern = re.compile(r'\b[0-9a-fA-F]{40}\b')
	match = re.match(pattern,u_pwd)

	# tests for pwd to be in sha1
	if(type(match)== type(None)):
		abort(400,description="Password not in SHA1 form")
	#tests for unique
	if(len(resp) > 0 ):
		return Response("User Already Exists",status=400, mimetype='application/json') #LOOK AGAIN!!!
	else:
		# db.execute("INSERT INTO userdata (uname,pwd,created_ride) VALUES (%s,%s,%s)",u_name,u_pwd,"N")
		pass_data={"table":"userdata (uname,pwd,created_ride)","cond":"",
					"vals":"("+"'"+str(u_name)+"'"+","+"'"+str(u_pwd)+"'"+","+"'N'"+")",
					"check":"insert"}
		pass_api="http://localhost:5000/api/v1/db/write/"
		r=requests.post(url=pass_api,json=pass_data)
		return Response("{}",status=201,mimetype='application/json')

#2)Remove User
@app.route('/api/v1/users/<username>',methods=["DELETE"])
def remove_user(username):
	
	
	pass_data={"table":"userdata","columns":"*","where":"uname="+"'"+str(username)+"'"}
	pass_api="http://localhost:5000/api/v1/db/read/"
	r=requests.post(url=pass_api,json=pass_data)
	resp=r.text
	resp=json.loads(resp)
	if(len(resp)==0):
		abort(400,description="User does not exist")
	else:
		pass_data={"table":"rides",
					"columns":"created_by",
					"where":"created_by="+"'"+str(username)+"'"}
		pass_api="http://localhost:5000/api/v1/db/read/"
		r=requests.post(url=pass_api,json=pass_data)
		resp1=r.text
		resp1=json.loads(resp1)
		if(len(resp1)>0):
			abort(400,description="Cannot Delete User")
		else:
			pass_data={"table":"userdata",
						"cond":"uname="+"'"+str(username)+"'",
						"vals":"",
						"check":"delete"}
			pass_api="http://localhost:5000/api/v1/db/write/"
			r=requests.post(url=pass_api,json=pass_data)


			pass_data_update={"table":"rides",
				"cond":"1=1",
				"vals":"passengers=array_remove(passengers,"+"'"+username+"'"+")",
				"check":"update"}
			pass_api_update="http://localhost:5000/api/v1/db/write/"
			r=requests.post(url=pass_api_update,json=pass_data_update)
			return Response("{}",status=200 , mimetype='application/json')

#3)Create Ride
@app.route('/api/v1/rides',methods=["POST"])

def create_ride():
	if not request.json:
		abort(400,description="Mention userdetails in request")
	source=request.get_json()["source"]
	dest=request.get_json()["destination"]
	time_stamp=request.get_json()["timestamp"]
	f='%d-%m-%Y:%S-%M-%H'
	time_obj=datetime.datetime.strptime(time_stamp,f)
	u_name=request.get_json()["created_by"]
	vd=0
	vs=0
	with open("AreaNameEnum.csv") as obj:
		for row in obj:
			row=row.split(",")
			if row[0]== source:
				vs=1
			if row[0]==dest:
				vd=1
	if(vd==1 and vs==1 and source!=dest):
		pass_data={"table":"userdata","columns":"*","where":"uname="+"'"+str(u_name)+"'"}
		pass_api="http://localhost:5000/api/v1/db/read/"
		r=requests.post(url=pass_api,json=pass_data)
		resp=r.text
		resp=json.loads(resp)
		ridelist = list()
		for i in range(10000):
			ridelist.append(i)
		rideId=random.sample(ridelist,1)
		#if user doesnt exist
		if(len(resp)==0):
			abort(400,description="user doesnt exist")
		else:
			pass_data={"table":"rides(rideId,created_by,passengers,source,dest,time_stamp)",
						"cond":"",
						"vals":"("+"'"+str(rideId[0])+"'"+","+"'"+str(u_name)+"'"+","+"'{}'"+","+"'"+str(source)+"'"+","+"'"+str(dest)+"'"+","+"'"+str(time_obj)+"'"+")",
						"check":"insert"}
			pass_api="http://localhost:5000/api/v1/db/write/"
			r=requests.post(url=pass_api,json=pass_data)


			pass_data={"table":"userdata",
						"cond":"uname="+"'"+str(u_name)+"'",
						"vals":"created_ride="+"'Y'",
						"check":"update"}
			pass_api="http://localhost:5000/api/v1/db/write/"
			r=requests.post(url=pass_api,json=pass_data)
			#adding the created_by user to the passenger list
			pass_data={"table":"rides",
						"cond":"created_by="+"'"+str(u_name)+"'",
						"vals":"passengers=array_cat(passengers,"+"'{"+u_name+"}'"+")",
						"check":"update"}
			pass_api="http://localhost:5000/api/v1/db/write/"
			r=requests.post(url=pass_api,json=pass_data)
			return Response("{}",status=201,mimetype='application/json')
	else:
		abort(400,description="Source and Destination are the same, or are invalid")

#4) prints data about upcoming rides
@app.route('/api/v1/rides',methods=["GET"])
def details_upcoming():
	source = request.args.get('source')
	dest = request.args.get('destination')
	vs=0
	vd=0
	with open("AreaNameEnum.csv") as obj:
		for row in obj:
			row=row.split(",")
			if row[0]== source:
				vs=1
			if row[0]==dest:
				vd=1
	if(vs==0 or vd==0):
		return Response("No content to show",status=204,mimetype='application/json')

	if(vd==1 and vs==1 and source!=dest):
   
		pass_api="http://localhost:5000/api/v1/db/read/"
		pass_data={"columns":"rideid,created_by,time_stamp","table":"rides","where":"source=" + "'"+str(source)+"'" + "" + " and " + "dest=""'" + str(dest) + "'" + " and " + "time_stamp >" + "CURRENT_TIMESTAMP"}
		res=requests.post(url=pass_api,json=pass_data)
		resp=res.text
		resp=json.loads(resp)
		if(len(resp)==0):
			return Response("No content to show",status=204,mimetype='application/json')
		r=[]
	   
		for row in resp:
		    
			d=OrderedDict() 
			d['rideid']=row["rideid"]
			d['username']=row['created_by']
			d['time_stamp']=row["time_stamp"]
			r.append(d)

		# return Response(jsonify(r),status=200,mimetype='application/json')
		return jsonify(r)
	else:
		abort(400,description="Source and Destination are the same, or are invalid")

#5) Details of a given ride
@app.route('/api/v1/rides/<rideId>', methods=["GET"])
def  ride_details(rideId):
	pass_data={"table":"rides","columns":"rideid, created_by, source, dest, time_stamp, passengers","where":"rideid="+rideId}
	pass_api="http://localhost:5000/api/v1/db/read/"
	
	res=requests.post(url=pass_api,json=pass_data)
	resp=res.text
	resp=json.loads(resp)
	
	if(len(resp)==0):
		abort(400,description="rideID does not exist")
	
	r=list()
	
	for row in resp:
		d=OrderedDict()
		d['rideID']=row['rideid']
		d['Created_by']=row['created_by']
		d['Timestamp']=row['time_stamp']
		d['Source']=row['source']
		d['Destination']=row['dest']
		d['Timestamp']=str(d['Timestamp'])
		d['Users'] = row['passengers']
		# print(d)
		r.append(d)
	return jsonify(r)
	# return Response(jsonify(r),status=200,mimetype='application/json')

#6) join an existing ride
@app.route('/api/v1/rides/<rideId>', methods=["POST"])
def join_existing_ride(rideId):
	u_name=request.get_json()["username"]
	"""
	To check if rideid and uname is valid
	query="select rideid from rides where rideid=rideid"
	query="select uname from userdata where uname=uname"
	"""
	pass_data={"table":"userdata","columns":"uname","where":"uname="+"'"+str(u_name)+"'"}
	pass_api="http://localhost:5000/api/v1/db/read/"
	r1=requests.post(url=pass_api,json=pass_data)
	resp1=r1.text
	resp1=json.loads(resp1)
	# print("hello")

	pass_data={"table":"rides","columns":"rideid","where":"rideid="+"'"+rideId+"'"}
	pass_api="http://localhost:5000/api/v1/db/read/"
	r2=requests.post(url=pass_api,json=pass_data)
	resp2=r2.text
	resp2=json.loads(resp2)
	if(len(resp1)==0):
		print("hello")
		abort(400,description="user does not exist")
	if(len(resp2)==0):
		print("hello")
		abort(400,description="rideID does not exist")
	pass_data={"table":"rides","columns":"passengers","where":"rideid="+"'"+str(rideId)+"'"}
	pass_api="http://localhost:5000/api/v1/db/read/"
	r=requests.post(url=pass_api,json=pass_data)
	dup=r.text
	dup=json.loads(dup)
	# print(dup)
	existing_pas = dup[0]['passengers']
	if u_name not in existing_pas:
    		 
	#query="update rides set passengers = array_cat(topics, '{uname}' where rideid=rideid);"
		pass_data={"table":"rides",
					"cond":"rideid="+rideId,
					"vals":"passengers=array_cat(passengers,"+"'{"+u_name+"}'"+")",
					"check":"update"}
		pass_api="http://localhost:5000/api/v1/db/write/"
		r=requests.post(url=pass_api,json=pass_data)
		return Response("{}",status=200,mimetype='application/json')
	else:
		print("you're already part of the ride")
	return Response("{}",status=200,mimetype='application/json')
	






#7. Delete a ride 

@app.route('/api/v1/rides/<rideId>', methods=["DELETE"])
def del_ride(rideId):

	

	
	pass_data={"table":"rides","columns":"*","where":"rideid="+rideId}
	pass_api="http://localhost:5000/api/v1/db/read/"
	r=requests.post(url=pass_api,json=pass_data)
	resp=r.text

	if(len(resp)>0):
		resp=json.loads(resp)


		
		pass_data={"table":"rides",
				   "cond":"rideid="+"'"+rideId+"'",
				   "vals":"",
				   "check":"delete"}
		pass_api="http://localhost:5000/api/v1/db/write/"
		r=requests.post(url=pass_api,json=pass_data)
		return Response("{}",status=200,mimetype='application/json')
	else:

		return Response("{}",status=400,mimetype='application/json')
	


#8) Write to db

@app.route('/api/v1/db/write/', methods=["POST"])
def write_db():
	
	table=request.get_json()["table"]
	cond=request.get_json()["cond"]
	vals=request.get_json()["vals"]
	check=request.get_json()["check"]

	if(check=="delete"):
		command="DELETE FROM "+table+" WHERE "+cond
	if(check =="insert"):
		command="INSERT INTO "+table+" VALUES "+vals
	if(check=="update"):
		command=" UPDATE "+table+" SET "+vals+" WHERE "+cond
	
	r= db.execute(command)
	return Response("{}",status=200,mimetype='application/json')

#9. Read from db

@app.route('/api/v1/db/read/', methods=["POST"])
def read_db():
	table=request.get_json()["table"]
	columns=request.get_json()["columns"]
	where=request.get_json()["where"]
	if(where==""):
		command="SELECT "+columns+" FROM "+table
	else:
		command="SELECT "+columns+" FROM "+table+" WHERE "+where
	
	r= db.execute(command)
	res=r.fetchall()
	row_headers=r.keys()
	json_data=[]
	
	for result in res:
		d = dict(result.items())
		if("time_stamp" in row_headers):
			k=datetime.datetime.strftime(d['time_stamp'],"%d-%m-%Y:%S-%M-%H")
			d['time_stamp']=k
		json_data.append(d)
		
	return jsonify(json_data)
   



if __name__ == '__main__':	
	app.debug=True
	app.run()