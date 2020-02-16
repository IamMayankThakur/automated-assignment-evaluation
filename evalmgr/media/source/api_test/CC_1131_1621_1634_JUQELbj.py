from flask import Flask, render_template,\
jsonify,request,abort
import re
import sqlite3 as sq3
import datetime
import requests
import flask
from datetime import datetime

app=Flask(__name__)





@app.route('/api/v1/db/read',methods=["POST"])
def db_read():
	action=flask.request.values.get('action')
	table=flask.request.values.get('table')

	columns=flask.request.values.get('columns')
	where=flask.request.values.get('where')

	
	userdb_connection=sq3.connect('user_details.db')
	cursor_user=userdb_connection.cursor()
	
	
	if(action == "select" and where == "NA"):
	
		existing_usersdb=cursor_user.execute("SELECT"+ columns+"FROM" +"\'"+table+"\'")
		y=existing_usersdb.fetchall()
		r=""
		if(table=="user_ride"):
			for i in y:
				r=r+"+"+str(i)
		else:
			for i in y:
				r=r+","+str(i[0])

		if(r==""):
			return "NA"
		return r
	elif( where !="NA"):
		where=where.split(";")
		
		if(len(where) == 4):
			
			existing_usersdb=cursor_user.execute("SELECT "+ columns+" FROM" +"\'"+table+"\'"+"WHERE "+where[0]+" = " +"\'"+where[1]+"\'"+" and "+where[2]+" = " +"\'"+where[3]+"\'")
			y=existing_usersdb.fetchall()
			
			r=""
			u=""
			for i in y:
				r=r+"+"+str(i)
		else:
			

		
			existing_usersdb=cursor_user.execute("SELECT "+ columns+" FROM " +table+" WHERE "+where[0]+"=(?)",(where[1],))
			y=existing_usersdb.fetchall()
			r=""
			u=""
			for i in y:
				u=i
				if(u == ""):
					return ""
				for i in u:
					r=r+","+str(i)

		
		if(r==""):
			return "NA"
		return r
	

			
		
		

@app.route('/api/v1/db/write',methods=["POST"])
def db_write():

	action=flask.request.values.get("action")
	scolumn=flask.request.values.get("scolumn")
	table=flask.request.values.get("table")
	where=flask.request.values.get("where")
	values=flask.request.values.get("values")
	
	values.strip(",")
	values=values.split(",")
	userdb_connection=sq3.connect('user_details.db')
	cursor_user=userdb_connection.cursor()
	
	if(action == "delete"):
		
		where=where.split(";")

		
		
		
		existing_usersdb=cursor_user.execute("DELETE FROM  "+table+" WHERE "+where[0] +"=(?)",(where[1],))
		
		userdb_connection.commit()
		return "succesfull",201
	if(action == "update"):
		where=where.split(";")
		
		existing_usersdb=cursor_user.execute("UPDATE "+table+" SET "+scolumn+"="+"\'"+values[0]+"\'"+" WHERE "+where[0] +"=(?)",(where[1],))
		userdb_connection.commit()
		return "uodate success"
	if(action == "insert" and table=="user_ride"):
		
		existing_usersdb=cursor_user.execute("INSERT INTO"+"\'"+table +"\'"+"(username,timestamp,source,destination) "+"VALUES(?,?,?,?)",(values[0],values[1],values[2],values[3]))
		
		userdb_connection.commit()
		return "success"
		
	if(action == "insert" and table=="users"):
		existing_usersdb=cursor_user.execute("INSERT INTO"+"\'"+table+"\'"+"VALUES(?,?)",(values[0],values[1]))
		userdb_connection.commit()
		return "success"

	userdb_connection.close()


	

#URL Routing:
@app.route('/api/v1/users',methods=["PUT"])
def add_user():
	username=request.get_json()["username"]
	password=request.get_json()["password"]
	post={"action":"select","table":"users","columns":"*","where":"NA"}
	url= 'http://3.222.120.11/api/v1/db/read'
	p=requests.post(url,data=post)
	if(p.text!="NA"):
		
		r=p.text
		
		r=r.strip(",")
		
		existing_users=r.split(",")
		for i in existing_users:
			if(i == username):
				
				return "",400
				break
	
	





	
	if(not re.search("^[a-fA-F0-9]{40}$",password)):

		
		abort(400)
	
	
	values=username+","+password
	post={"action":"insert","table":"users","columns":"*","where":"NA","values":values}
	url= 'http://3.222.120.11/api/v1/db/write'
	p=requests.post(url,data=post)
	t=p.text
	return "",201

	
		
	
@app.route('/api/v1/users/<user>',methods=["DELETE"])
def remove_user(user):
	post={"action":"select","table":"users","columns":"*","where":"NA"}
	url= 'http://3.222.120.11/api/v1/db/read'
	p=requests.post(url,data=post)
	
	if(p.text == "NA"):
		abort(400)
	r=p.text
	r=r.strip(",")
	
	
	existing_users=r.split(",")
	
	if(user in existing_users):
		t="username;"+user
	
		post={"action":"delete","table":"users","columns":"NA","where":t,"values":"NA"}
		url= 'http://3.222.120.11/api/v1/db/write'
		p=requests.post(url,data=post)
		
		
		
		
		post={"action":"select","table":"user_ride","columns":"*","where":"NA"}
		url= 'http://3.222.120.11/api/v1/db/read'
		p=requests.post(url,data=post)
		t=p.text
		

		
		if(p.text != "NA" ):
			t=p.text
			
			t=t.strip("+")
			t=t.split("+")
			f=0
			for i in t:
				
				i=i.strip("()")
				i=i.split(",")
				
				if(user in i[5]):
					t="ride;"+i[0]
					f=1
					
					p1=i[5].replace(user,"")
					p1=p1.replace("\'","")
					p1=p1.split(";")
					
					
					p2=""
					for j in p1:
						
						if(j!=" "):
							p2=p2+";"+j
					p2=p2.strip(";")
				
					post={"action":"update","table":"user_ride","scolumn":"ride_mate","where":t,"values":p2}
					url= 'http://3.222.120.11/api/v1/db/write'
					p=requests.post(url,data=post)
					t=p.text
					
				i[1]=i[1].replace("\'","")
				i[1]=i[1].strip(" ")
				
				if(user in i):
					
					t="ride;"+i[0]
					
					post={"action":"delete","table":"user_ride","columns":"NA","where":t,"values":"NA"}
					url= 'http://3.222.120.11/api/v1/db/write'
					p=requests.post(url,data=post)
					t=p.text
					return t+"succesfully deleted in user rides if any rides",200
		

			
			return "out",200
		else:
			return "empty",200
	else:
		abort(400)

		
		
		
	
	
	
@app.route('/api/v1/rides',methods=["POST"])
def new_ride():
	username=request.get_json()["created_by"]
	timestamp=request.get_json()["timestamp"]
	source=request.get_json()["source"]
	destination=request.get_json()["destination"]
	userdb_connection=sq3.connect('user_details.db')
	cursor_user=userdb_connection.cursor()
	f = open("AreaNameEnum.csv", "r")
	Lines = f.readlines() 
	for i in Lines:
		p=i.replace("\"","")
		p=p.split(",")
		if(str(source) == p[0]):
			source=p[1].strip("\n")
		if(str(destination) == p[0]):
			destination=p[1].strip("\n")


	post={"action":"select","table":"users","columns":"*","where":"NA"}
	url= 'http://3.222.120.11/api/v1/db/read'
	p=requests.post(url,data=post)
	if(p.text == "NA"):
		abort(400)
	r=p.text
	r=r.strip(",")
	
	existing_users=r.split(",")
	
	if(username in existing_users):
		
		values=username+","+timestamp+","+source+","+destination
		post={"action":"insert","table":"user_ride","columns":"NA","where":"NA","values":values}
		url= 'http://3.222.120.11/api/v1/db/write'
		p=requests.post(url,data=post)
		t=p.text
		return "",201



	else:
		abort(400)
@app.route('/api/v1/rides/<rideId>',methods=["GET"])
def ride_details(rideId):
	
	t="ride;"+rideId
	post={"action":"select","table":"user_ride","columns":"*","where":t}
	url= 'http://3.222.120.11/api/v1/db/read'
	p=requests.post(url,data=post)
	
	
	if(p.text == "NA"):
		return "",400
	u=p.text
	p=u.strip(",")
	p=p.split(",")
	
	
	

	rides={}
	values = ["rideId","created_by","timestamp","source","destination","users"]
	index = 0
	
	
		
	for j in p:
		if index == 5:
		
			if(j!="None"):
				
				riders=j.split(";")
				
				rides[values[5]]=riders
			else:
				rides[values[index]] = []
		else:
			rides[values[index]] = j
		index +=1
	if("users" not in rides):
		rides["users"]=[]
	return jsonify(rides),200
@app.route('/api/v1/rides/<rideId>',methods=["POST"])
def join_ride(rideId):

	username_requesting=request.get_json()["username"]
	

	



	

	post={"action":"select","table":"users","columns":"*","where":"NA"}
	url= 'http://3.222.120.11/api/v1/db/read'
	p=requests.post(url,data=post)
	if(p.text == "NA"):
		return "",400
	r=p.text
	r=r.strip(",")
	
	existing_users=r.split(",")
	if(not username_requesting in existing_users):
		return "",400
	
	post={"action":"select","table":"user_ride","columns":"*","where":"NA"}
	url= 'http://3.222.120.11/api/v1/db/read'
	p=requests.post(url,data=post)
	if(p.text == "NA"):
		return "",400
	t=p.text
	r=1
	t=t.strip("+")
	t=t.split("+")
	for i in t:
		p=i.strip("()")
		p=p.split(",")
		if str(rideId) in p:
			r=0
			break
	
	

	
	if r:
		return "",400
	else:
		t="ride;"+rideId
		post={"action":"select","table":"user_ride","columns":"*","where":t}
		url= 'http://3.222.120.11/api/v1/db/read'
		p=requests.post(url,data=post)
		u=p.text
		p=u.strip(",")
		p=p.split(",")
		if(p[1] == username_requesting):
			return "",400
		
		

	
	
	if(len(p) < 6):
		updated_ride_mates=username_requesting
	else:
		updated_ride_mates= username_requesting + ";"+p[5]
		if(p[5]=="None"):
			updated_ride_mates=username_requesting
		res = p[5].split(";")
		if(username_requesting in res):
			return "alraedy there",200
	
	

		
	
	
	"""post={"action":"select","table":"user_ride","columns":"*","where":"NA"}
	url= 'http://3.222.120.11/api/v1/db/read'
	p=requests.post(url,data=post)
	if(p.text != "NA" ):
		t=p.text
		
		t=t.strip("+")
		t=t.split("+")
		for i in t:
			
			i=i.strip("()")
			i=i.split(",")
			if(username_requesting in i[5]):
				return "",200"""
					
	t="ride;"+rideId
	post={"action":"update","table":"user_ride","scolumn":"ride_mate","where":t,"values":updated_ride_mates}
	url= 'http://3.222.120.11/api/v1/db/write'
	p=requests.post(url,data=post)
	return p.text,200



@app.route('/api/v1/rides/<ridesId>',methods=["DELETE"])
def ride_delete(ridesId):
	


	
	
	post={"action":"select","table":"user_ride","columns":"*","where":"NA"}
	url= 'http://3.222.120.11/api/v1/db/read'
	p=requests.post(url,data=post)
	if(p.text == "NA"):
		abort(400)
	t=p.text
	r=0
	t=t.strip("+")
	t=t.split("+")
	for i in t:
		p=i.strip("()")
		p=p.split(",")
		if str(ridesId) in p:
			r=1
			break
	
	

	
	if r:
		
		
		t="ride;"+ridesId

		post={"action":"delete","table":"user_ride","columns":"i","where":t,"values":"NA"}
		url= 'http://3.222.120.11/api/v1/db/write'
		p=requests.post(url,data=post)
		t=p.text
		return p.text,200
		
	else:
		return "Ride Id does not exist",400

@app.route('/api/v1/rides',methods=["GET"])
def uprides():
	 args = request.args
	 source=args["source"]
	 destination=args["destination"]
	 if(source == "" or destination == ""):
		 abort(400)
    
	 f = open("AreaNameEnum.csv", "r")
	 Lines = f.readlines() 
	 for i in Lines:
		 p=i.replace("\"","")
		 p=p.split(",")
		 if(str(source) == p[0]):
			 source=p[1].strip("\n")
		 if(str(destination) == p[0]):
			 destination=p[1].strip("\n")
	
	
     
	 t="source;"+source+";"+"destination"+";"+destination
	 if(source == "" or destination == ""):
		 abort(400)

	 post={"action":"select","table":"user_ride","columns":"*","where":t}
	 url='http://3.222.120.11/api/v1/db/read'
	 p=requests.post(url,data=post)
	 if(p.text == "NA"):
		 return "",204
	 y=[]
	 
	 urides={}
	 t=p.text
	 t=t.strip("+")
	 t=t.split("+")
	 
	 
	 for i in t:
		 i=i.strip("()")
		 i=i.replace("\'","")
		 i=i.split(",")
		 i[2]=i[2].strip(" ")
		 i[1]=i[1].strip(" ")
		
		 
		 p=datetime.strptime(i[2],'%d-%m-%Y:%S-%M-%H')
		 now =datetime.now()
		 
		
		 if(p > now):
			 urides["rideId"]=i[0]
			 urides["username"]=i[1]
			 urides["timestamp"]=i[2]
			 y.append(urides)
			 urides={}

			 
	 if(len(y)==0):
		 return "",204	
	 return jsonify(y),200
			 

	

			

#delete a ride when username if deleted			
if __name__ == '__main__':	
	app.debug=True
	app.run()
        

