from flask import Flask, render_template,\
jsonify,request,abort

app=Flask(__name__)

import sqlite3
import requests
import random
import datetime

RS400=400

RS405=405
RS200=200
RS201=201
RS204=204
f = open("AreaNameEnum.csv", "r")
l = f.readlines()
source = "1"
arealist = []
destination = "20"
m = [0, 0]
for i in l:
    i = i.split(",")
    arealist.append(i[0])
arealist=arealist[1:]

shalist=['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f']
def checksha(string):
	if(len(string)!=40):
		return True
	else:
		for i in list(string):
			if i not in shalist:
				return True
	return False

@app.route("/api/v1/rides",methods=["POST"])
def newride():
	print("HI")
	if(request.method!="POST"):
		return jsonify({}),RS405
	RIDEIDreq={"table":"rides","columns":["rideid"],"where":[]}
	RIDEID=requests.post('http://localhost:5000/api/v1/db/read',json=RIDEIDreq)
	print("###########################")
	print(RIDEID)
	print("##########################")
	if(len(eval(RIDEID.text))==0):
		RIDEID=0
	else:
		RIDEID=max(eval(RIDEID.text))
	req=request.get_json()
	if(RIDEID==0):
		rideid=0
	else:
		rideid=max(list(map(int,(RIDEID))))+1
	print(rideid)
	if(not("created_by" in req and "timestamp" in req and "source" in req and "destination" in req )):
		return jsonify({}),RS400
	username=req["created_by"]
	timestamp=req["timestamp"]
	try:
		time=datetime.datetime.strptime(timestamp,"%d-%m-%Y:%S-%M-%H")
	except:
		return jsonify({}),RS400
	source=req["source"]
	destination=req["destination"]
	if(source not in arealist or destination not in arealist):
		return jsonify({}),RS400
	#if ("username" in req):
	#	return "Yesss"
	req1={"where":["username='%s'" % username],"columns":["username"],"table":"user"}
	r1 = requests.post('http://localhost:5000/api/v1/db/read',json=req1)
	l=eval(r1.text)
	if(len(l)==0):
		d=RS400
		return jsonify({}),d
	users='["%s"]' % username
	req={"table":"rides","columns":["rideid","username","timestamp","source","destination","users"],"insert":[rideid,username,timestamp,source,destination,users]}
	r = requests.post('http://localhost:5000/api/v1/db/write',json=req)
	print(str(r))
	if('200' in str(r)):
		return jsonify({}),RS201
	else:
		return jsonify({}),RS400
	#return "donee"

@app.route("/api/v1/rides",methods=["GET"])
def upcomingrides():
	
	if(request.method!="GET"):
		return jsonify({}),RS405
	

	source=request.args.get("source")
	destination=request.args.get("destination")
	print("#########################")
	print(source,type(source))
	if(source not in arealist or destination not in arealist):
		return jsonify({}),RS400

	if(source.isalpha() or destination.isalpha()):
		print("QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQq")
		print("oops")
		return jsonify({}),RS400
	print("QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQq")
	print("yayayyaya")
	#if ("username" in req):
	#	return "Yesss"
	req1={"where":["source='%s'" % source,"destination='%s'" % destination],"columns":["source","destination"],"table":"rides"}
	r1 = requests.post('http://localhost:5000/api/v1/db/read',json=req1)
	print("#########################")
	print(r1)
	
	l=eval(r1.text)

	c=0
	for i in l:
		if source==i[0] and destination==i[1]:
			c=1
	if(c==0):
		return jsonify({}),RS204
	req={"table":"rides","where":["source='%s'" % source,"destination='%s'" % destination],"columns":["rideid","username","timestamp"]}
	r = requests.post('http://localhost:5000/api/v1/db/read',json=req)
	# return r.text
	print("RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRr")
	print(r)
	l=eval(r.text)
	print("#########################")
	print(l)
	
	if('200' in str(r)):
		responselist=[]

		for i in l:
			d2=datetime.datetime.strptime(i[2],"%d-%m-%Y:%S-%M-%H")
			n=datetime.datetime.now()
			if (n<d2):
				responselist.append({"rideId":i[0],"username":i[1],"timestamp":i[2]})
		print("#########################")
		print("IF ")
	
		return jsonify(responselist),RS200
	else:
		return jsonify({}),RS400
		print("#########################")
		print("ELSE ")
	
	#return "donee"
	

@app.route("/api/v1/rides/<rideId>",methods=["GET"])
def listrides(rideId):
	# req=request.get_json()
	# rideid=1234
	# username=req["created_by"][0]
	# timestamp=req["timestamp"]
	rideID=rideId
	if(rideID.isalpha()):
		return jsonify(RS400)
	#if ("username" in req):
	#	return "Yesss"
	req1={"where":["rideid='%s'" % rideID],"columns":["rideid"],"table":"rides"}
	r1 = requests.post('http://localhost:5000/api/v1/db/read',json=req1)
	l=eval(r1.text)
	if(len(l)==0):
		return jsonify({}),RS400

	req={"table":"rides","where":["rideid='%s'" % rideID],"columns":["rideid","username","timestamp","source","destination","users"]}
	r = requests.post('http://localhost:5000/api/v1/db/read',json=req)
	#print("?????????????????????????????????????")
	#print(r)
	l=eval(r.text)
	others=l[0][5]
	others=eval(others)

	if("200" in str(r)):
		
		return jsonify({"rideId":rideID,"created_by":l[0][1],"users":others,"timestamp":l[0][2],"source":l[0][3],"destination":l[0][4]})
	else:
		return jsonify(RS400)
	
	# return r.text
	#return "donee"

@app.route("/api/v1/rides/<rideId>",methods=["POST"])
def joinride(rideId):
	if(request.method!="POST"):
		return jsonify({}),RS405
	req=request.get_json()
	if(rideId.isalpha()):
		return jsonify({}),RS400
	if("username" not in req):
		return jsonify({}),RS400
	# rideid=1234
	username=req["username"]
	# timestamp=req["timestamp"]
	rideID=rideId
	#if ("username" in req):
	#	return "Yesss"
	req1={"where":["rideid='%s'" % rideID],"columns":["rideid"],"table":"rides"}
	r1 = requests.post('http://localhost:5000/api/v1/db/read',json=req1)
	l=eval(r1.text)
	print(l)
	if(len(l)==0):
		return jsonify({}),RS400
	req1={"where":["username='%s'" % username],"columns":["username"],"table":"user"}
	r1 = requests.post('http://localhost:5000/api/v1/db/read',json=req1)
	l=eval(r1.text)
	print(l)
	if(len(l)==0):
		return jsonify({}),RS400
	timestamp=datetime.datetime.now()
	Timestamp=str(timestamp.day)+"-"+str(timestamp.month)+"-"+str(timestamp.year)+":"+str(timestamp.second)+"-"+str(timestamp.minute)+"-"+str(timestamp.hour)
	rreq={"table":"rides","where":["rideid='%s'" % rideID],"columns":["users"]}
	r = requests.post('http://localhost:5000/api/v1/db/read',json=rreq)
	
	#return(r.text)
	if("200" in str(r)):
		lot=eval(r.text)
		l=eval(lot[0][0])
		if username in  l:
			return jsonify({}),RS400
		l.append(username)
		names=str(l)
		#rint("::::::::::::::::::::::::")
		#print(names)
		req={"table":"rides","sset":['users="%s"'% names],"where":["rideid='%s' "%rideID]}
		r = requests.post('http://localhost:5000/api/v1/db/write',json=req)
		return jsonify({}),RS200
	else:
		return jsonify({}),RS400


@app.route("/api/v1/rides/<rideId>",methods=["DELETE"])
def delride(rideId):
	if(request.method!="DELETE"):
		return jsonify({}),RS405
	if(rideId.isalpha()):
		return jsonify({}),RS400
	req1={"where":["rideid='%s'" % rideId],"columns":["rideid"],"table":"rides"}
	r1 = requests.post('http://localhost:5000/api/v1/db/read',json=req1)
	l=eval(r1.text)
	if len(l)!=0:
		req2={"table":"rides","delete":rideId,"columns":"rideid"}
		r = requests.post('http://localhost:5000/api/v1/db/write',json=req2)
		# return r.json()
		if("200" in str(r)):
			return jsonify({}),RS200
	

	d={"400":"Not allowed"}
	return jsonify({}),RS400	

@app.route("/api/v1/users",methods=["PUT"])
def adduser():
	req=request.get_json()
	if(request.method!="PUT"):
		return jsonify({}),RS405
	if(not("username" in req and "password" in req)):
		return jsonify({}),RS400
	username=req["username"]
	#if ("username" in req):
	#	return "Yesss"
	password=req["password"]
	if username=="":
		return jsonify({}),RS400
	if(checksha(password)):
		return jsonify({}),RS400
	
	req1={"where":["username='%s'" % username],"columns":["username"],"table":"user"}
	r1 = requests.post('http://localhost:5000/api/v1/db/read',json=req1)
	l=eval(r1.text)
	if(len(l)!=0):
		# d={"405":"Not allowed"}
		return jsonify({}),RS400
	
	
	req2={"table":"user","columns":["username","password"],"insert":[username,password]}
	r2 = requests.post('http://localhost:5000/api/v1/db/write',json=req2)
	# return r2.json()     
	if("200" in str(r2)):
		return jsonify({}),RS201
	else:
		return jsonify({}),RS500

@app.route("/api/v1/users/<name>",methods=["DELETE"])
def deluser(name):
	if(request.method!="DELETE"):
		return jsonify({}),RS405

	#'''
	#check if there is username in user table
	#'''
	req1={"where":["username='%s'" % name],"columns":["username"],"table":"user"}
	r1 = requests.post('http://localhost:5000/api/v1/db/read',json=req1)
	l=eval(r1.text)

	if len(l)!=0:

		#'''
		#delete from user table
		#'''
		req2={"table":"user","delete":name,"columns":"username"}
		r = requests.post('http://localhost:5000/api/v1/db/write',json=req2)


		if("200" not in str(r)):
			return jsonify({}),RS500
		#else:
		#	return jsonify({}),RS500
		#deleting if name is creator 
		newreq={"table":"rides","delete":name,"columns":"username"}
		newr=requests.post('http://localhost:5000/api/v1/db/write',json=newreq)


		req4={"where":[],"columns":["users","rideid"],"table":"rides"}
		r4= requests.post('http://localhost:5000/api/v1/db/read',json=req4)

		mylist=eval(r4.text)
		#print("MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM")
		#print(name)
		for i in range(len(mylist)):
			myusers=eval(mylist[i][0])
			print("MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM")
			print(mylist[i][0])
			if name in myusers :
				myusers.remove(name)
				rid=mylist[i][1]
				mystr=str(myusers)
				newreq={"table":"rides","sset":['users="%s"'% mystr],"where":["rideid='%s'" % rid]}
				newr=requests.post('http://localhost:5000/api/v1/db/write',json=newreq)
		

		return jsonify({}),RS200
			

	d={"405":"Not allowed"}
	return jsonify({}),RS400

	#return "donee"

#######
@app.route("/api/v1/db/read",methods=["POST"])
def readdb():
	con=sqlite3.connect("/home/ubuntu/rideshare.db")
	cursorobj=con.cursor()	
	req=request.get_json()
	where=req["where"] #list
	cols=req["columns"] #list
	table=req["table"]
	sstr="select "
	if(len(cols)==0):
		sstr+=" *,"
	for i in range(len(cols)):
		sstr+="%s ," % cols[i]
	sstr=sstr[:-1]
	sstr+="from %s " % table
	if(len(where)!=0):
		sstr+="where "	
		for i in range(len(where)):
			sstr+= where[i]
			sstr+=" and "
		sstr=sstr[:-4]
	sstr+=";"

	res=cursorobj.execute(sstr)
	return str(list(res))


@app.route("/api/v1/db/write",methods=["POST"])
def writedb():
	con=sqlite3.connect("/home/ubuntu/rideshare.db")
	cursorobj=con.cursor()	
	#sstr="insert into user values('abishek','123sg');"

	req=request.get_json()
	if "insert" in req:
		insert=req["insert"] #list
		cols=req["columns"] #list
		table=req["table"]
		sstr="insert into %s(" % table
		 

		for i in range(len(cols)):
			sstr+=cols[i]+","
		sstr=sstr[:-1]
		sstr+=") values("

		for i in range(len(insert)):
			sstr+="'%s'," %insert[i]
		sstr=sstr[:-1]
		sstr+=");"
		#return sstr
		cursorobj.execute(sstr)
		con.commit()
		dok={"201":"ok"}
		return jsonify(dok)		

	elif("delete" in req):
		data=req["delete"]
		table=req["table"]
		col=req["columns"]
		#data=req["data"]
		sstr="delete from %s where " %table
		sstr+=col+"= '%s';" %data
		cursorobj.execute(sstr)
		con.commit()
		dok={"201":"ok"}
		return jsonify(dok)		
	elif ("sset" in req ):
		table=req["table"]
		sset=req["sset"] #list
		where=req["where"] #list
		sstr="UPDATE %s set " % table
		
		for i in range(len(sset)):
			sstr+=" %s," % sset[i]
		sstr=sstr[:-1]
		if(len(where)!=0):
			sstr+=" where "	
			for i in range(len(where)):
				sstr+=  where[i]
				sstr+=" and "
			sstr=sstr[:-4]
		sstr+=";"
		print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		print(sstr)
		cursorobj.execute(sstr)
		con.commit()
		dok={"201":"ok"}
		return jsonify(dok)
	
	
if __name__ == '__main__':	
	app.debug=True
	#app.bind(9000)
	#app.run(host="0.0.0.1",port=5000)
	app.run()
