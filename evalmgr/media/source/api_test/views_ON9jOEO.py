from flask import Flask, render_template,jsonify,request,abort,url_for,Response
import re
import psycopg2
import requests
import json
import datetime
from waitress import serve
ip = "http://52.72.15.183"
pg_ip = "localhost"
locations = {}

def testdate(timestamp):
	halves = timestamp.split(":")
	#print("halves:", halves)
	if len(halves)!=2:
		return False
	datepart = halves[0].split("-")
	if len(datepart)!=3:
		return False
	day = datepart[0]
	month = datepart[1]
	year = datepart[2]
	#print(year,month,day)
	timepart = halves[1].split("-")
	if len(timepart)!=3:
		return False
	sec = timepart[0]
	mins = timepart[1]
	hr = timepart[2]
	#print(sec,mins,hr)
	try:
		datetime.datetime(int(year),int(month),int(day),int(hr),int(mins), int(sec))
	except:
		return False
	return True

def makedt(timestamp):
	halves = timestamp.split(":")
	datepart = halves[0].split("-")
	timepart = halves[1].split("-")
	day = int(datepart[0])
	month = int(datepart[1])
	year = int(datepart[2])
	sec = int(timepart[0])
	mins = int(timepart[1])
	hr = int(timepart[2])
	return datetime.datetime(year,month,day,hr,mins,sec)

with open("./AreaNameEnum.csv") as f:
	lines = f.readlines()
	lines = lines[1:]
	for l in lines:
		line = l.split(",")
		locations[int(line[0])] = line[1].rstrip("\r").rstrip("\n")
#print(locations)
app=Flask(__name__)
prepost = "out"
@app.route('/api/v1/users', methods=["PUT"])
def adduser():
	prepost = 0
	try:
		#prepost = "a"
		data = request.json
		#prepost = "b"
		pattern = re.compile(r'\b[0-9a-f]{40}\b')
		prepost = str(data)
		match = re.match(pattern, data['password'])
		prepost = 1
		r = requests.post(ip + "/api/v1/db/read",json={"table":"users","username":data["username"]})
		prepost = 2
		r = r.json()
		l = len(r['username'])
		if(match != None)  and (l == 0):
			r = requests.post(ip + "/api/v1/db/write",json={"table":"user","operation":"insert","username":data["username"],"password":data["password"]})
			return Response("{}",status=201)
		return 	Response("{}",status=400)
	except:
		return 	Response("{}",status=400)

@app.route('/api/v1/users/<username>', methods=["DELETE"])
def removeuser(username):
	r = requests.post(ip + "/api/v1/db/read",json={"table":"users","username":username})
	r = r.json()
	l = len(r["username"])
	if(l != 0):
		r = requests.post(ip + "/api/v1/db/write",json = {"table":"user","operation":"delete","username":username})
		return Response('{}',status = 200)
	return Response("{}",status=400)


@app.route('/api/v1/rides', methods=["POST"])
def createride():
	try:
		data = request.json
		#print(data)
		if not testdate(data['timestamp']):
			print("Bad timestamp!")
			return Response('{}',status=400)
		if int(data["source"]) not in locations.keys() and int(data["destination"]) not in locations.keys():
			#print("KEK")
			return Response('{}',status=400)
		#print("main params ok ")
		r = requests.post(ip + "/api/v1/db/read",json={"table":"users","username":data["created_by"]})
		r = r.json()
		l = len(r["username"])
		if(l != 0):
			r = requests.post(ip + "/api/v1/db/write",json={"table":"ride","operation":"insert","username":data["created_by"],"timestamp":data["timestamp"],"source":data["source"],"destination":data["destination"]})
			return Response('{}',status=201)
		return 	Response('{}',status=400)
	except:
		return 	Response("{}",status=400)


@app.route('/api/v1/rides', methods=["GET"])
def rideslist():
	try:
		rs = request.args.get("source")
		rd = request.args.get("destination")
		#print(rs, rd)
		r1 = requests.post(ip + "/api/v1/db/read",json={"table":"ride_sd","source":rs,"destination":rd})
		detail = r1.json()
		#print(detail)
		req_time = datetime.datetime.now()
		req_time = req_time.replace(microsecond=0)
		print("req_time:", req_time)
		if "rideid" not in detail or len(detail["rideid"])==0:
			return Response("{}", status=204)
		resp = []
		for i in range(len(detail["rideid"])):
			ride_time = makedt(detail["timestamp"][i])
			print("ride_time:", ride_time)
			if ride_time >= req_time:
				resp.append({"rideId":detail["rideid"][i],"username":detail["created_by"][i],"timestamp":detail["timestamp"][i]})
		return Response(json.dumps(resp), status=200)
	except:
		return 	Response("{}",status=400)


@app.route('/api/v1/rides/<rideId>', methods=["GET"])
def ridedetails(rideId):
	r1 = requests.post(ip + "/api/v1/db/read",json={"table":"ride","rideid":rideId})
	detail = r1.json()
	#print(detail)
	r2 = requests.post(ip + "/api/v1/db/read",json={"table":"user_ride","rideid":rideId})
	detail2 = r2.json()
	#print(detail2)
	resp = []
	if "rideid" not in detail:
		return Response("{}", status = 204)
	if(len(detail["rideid"])==0):
		return Response('{}',status=204)
	for i in range(len(detail["rideid"])):
		resp.append({"rideId":detail["rideid"][i],"created_by":detail["created_by"][i],"users":detail2["username"],"timestamp":detail["timestamp"][i],"source":locations[int(detail["source"][i])],"destination":locations[int(detail["destination"][i])]})
	return Response(json.dumps(resp[0]),status=200)



@app.route('/api/v1/rides/<rideId>', methods=["POST"])
def joinride(rideId):
	try:
		data = request.json
		r1 = requests.post(ip + "/api/v1/db/read",json={"table":"ride","rideid":rideId})
		detail = r1.json()
		creator = detail["created_by"][0]
		#print("Creator:",creator)
		rtest = requests.post(ip + "/api/v1/db/read",json={"table":"users","username":data["username"]})
		rt = rtest.json()
		l1 = len(rt["username"])
		#print("Joiner:", data["username"])
		r3 = requests.post(ip + "/api/v1/db/read",json={"table":"user_ride","rideid":rideId})
		r3js = r3.json()
		#print("R3's json:", r3js)
		existing_users = r3js["username"]
		#print("existing users:", existing_users)
		if (creator == data["username"]) or (data["username"] in existing_users):
			#print("You're already a part of the party!")
			return Response("{}", status=400) # creator is trying to add himself as a user, or user is already in. dont allow
		if(len(detail["rideid"])!=0 and l1!=0):
			r1 = requests.post(ip + "/api/v1/db/write",json={"table":"user_ride","operation":"insert","rideid":rideId,"username":data["username"]})
			return Response("{}",status=200)
		return  Response("{}",status=400)
	except:
		return 	Response("{}",status=400)

@app.route('/api/v1/rides/<rideId>', methods=["DELETE"])
def deleteride(rideId):
	try:
		r1 = requests.post(ip + "/api/v1/db/read",json={"table":"ride","rideid":rideId})
		detail = r1.json()
		if(len(detail["rideid"])!=0):
			r = requests.post(ip + "/api/v1/db/write",json={'table':"ride","operation":"delete","rideid":rideId})
			return Response('{}',status=200)
		return Response('{}',status=400)
	except:
		return 	Response("{}",status=400)

@app.route('/api/v1/db/write', methods=["POST"])
def writedb():
	data = request.json
	prepost = "NoConn"
	connection = psycopg2.connect(user = "postgres",password = "password",host = pg_ip ,port = "5432",database = "rideshare")
	prepost = "Conned"
	cursor = connection.cursor()
	if(data["operation"] == "insert"):
		if(data["table"] == "user"):
			query = "INSERT INTO users(userid,password) VALUES('" +data["username"]+ "','"+data["password"]+"');"
		if(data["table"] == "ride"):
			query = "INSERT INTO rides(created_by,timestamp,source,destination) VALUES('" +data["username"]+ "','" +data["timestamp"]+ "','" +data["source"]+ "','" +data["destination"]+ "');"
		if(data["table"] == "user_ride"):
			query = "INSERT INTO user_rides(ride_id, userid) VALUES(" + data["rideid"] + ",'" + data["username"]+ "');"
	if(data["operation"] == "delete"):
		if(data["table"] == "user"):
			query = "DELETE FROM users where userid = '" +data["username"]+ "';"
		if(data["table"] == "ride"):
			query = "DELETE FROM rides where rideid  = " +data["rideid"]+ ";"
	cursor.execute(query)
	connection.commit()
	return Response("{}",status=201)

@app.route('/api/v1/db/read', methods=["POST"])
def readdb():
	data = request.json
	connection = psycopg2.connect(user = "postgres",password ="password",host = pg_ip ,port = "5432",database = "rideshare")
	cursor = connection.cursor()
	output = {}
	if(data["table"] == "users"):
		query = "SELECT * FROM users WHERE userid = '" +data["username"]+ "';"
		output["username"] = []
		cursor.execute(query)
		result = cursor.fetchall()
		for i in range(len(result)):
			output["username"].append(result[i][0])
	if(data["table"] == "ride_sd"):
		query = "SELECT * FROM rides WHERE source = '" +data["source"]+ "' AND destination  = '" +data["destination"]+ "';"
		cursor.execute(query)
		result = cursor.fetchall()
		output["rideid"] = []
		output["created_by"] = []
		output["timestamp"] = []
		for i in range(len(result)):
			output["rideid"].append(result[i][0])
			output["created_by"].append(result[i][1])
			output["timestamp"].append(result[i][2])
	if(data["table"] == "ride"):
		query = "SELECT * FROM rides WHERE rideid = " +data["rideid"]+ ";"
		cursor.execute(query)
		result = cursor.fetchall()
		output["rideid"] = []
		output["created_by"] = []
		output["timestamp"] = []
		output["source"] = []
		output["destination"] = []
		for i in range(len(result)):
			output["rideid"].append(result[i][0])
			output["created_by"].append(result[i][1])
			output["timestamp"].append(result[i][2])
			output["source"].append(result[i][3])
			output["destination"].append(result[i][4])
	if(data["table"] == "user_ride"):
		query = "SELECT * FROM user_rides WHERE ride_id = " + data["rideid"] + ";"
		cursor.execute(query)
		result = cursor.fetchall()
		output["username"] = []
		for i in range(len(result)):
			output["username"].append(result[i][1])
	return jsonify(output)

if __name__ == '__main__':
	serve(app, host = "0.0.0.0", port = 80)
	#app.run('0.0.0.0',port=80) #it should be  just run() when you do it with gunicorn+nginx. Don't forget!
