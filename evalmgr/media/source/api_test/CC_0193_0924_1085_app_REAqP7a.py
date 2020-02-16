from flask import Flask,render_template,jsonify,request,abort
import requests
import sqlite3
import re
import csv
from datetime import datetime


app=Flask(__name__)


@app.route('/')
def hello_world():
	return "RideShare API"


@app.route('/api/v1/users',methods=["PUT"])
def add_user():
	data = request.get_json()
	if("username" in data and "password" in data):
		new_username = request.get_json()["username"]
		new_passw = (request.get_json()["password"]).lower()
		url = 'http://127.0.0.1:5000/api/v1/db/read'
		myobj = {"command": "select","table":"users","where":"username="+"'"+new_username+"'"}
		response = requests.post(url, json = myobj)
		y = response.json()
		n = len(y)
		if(n==0 and re.match(r"[0-9a-f]{40}", new_passw) and len(new_username)>0 and len(new_passw)==40):
			url = 'http://127.0.0.1:5000/api/v1/db/write'
			myobj = {"command": "insert","table":"users","column_list":{"username":"'"+new_username+"'","password":"'"+new_passw+"'"}}
			response = requests.post(url, json = myobj)
			return jsonify ({}),201
		else:
			return jsonify ({}),400
	else:
		return jsonify ({}),400


@app.route('/api/v1/users/<username>',methods=["DELETE"])
def remove_user(username):
	if(username):
		url = 'http://127.0.0.1:5000/api/v1/db/read'
		myobj = {"command": "select","table":"users","where":"username="+"'"+username+"'"}
		response = requests.post(url, json = myobj)
		y = response.json()
		n = len(y)
		myobj = {"command": "select","table":"rides","where":"created_by="+"'"+username+"'"}
		response = requests.post(url, json = myobj)
		n1 = len(response.json())
		if(n==1 and n1==0):
			url = 'http://127.0.0.1:5000/api/v1/db/write'
			myobj = {"command": "delete","table":"users","where":"username="+"'"+username+"'"}
			response = requests.post(url, json = myobj)
			myobj = {"command": "delete","table":"ridepool","where":"username="+"'"+username+"'"}
			response = requests.post(url, json = myobj)
			return jsonify ({}),200
		elif(n1>0):
			return "This user cannot be deleted as he is associated with a ride.",400
		else:
			return jsonify({}),400
	else:
		return jsonify ({}),400


@app.route('/api/v1/rides',methods=["POST"])
def new_ride():
	data = request.get_json()
	if("created_by" in data and "timestamp" in data and "source" in data and "destination" in data):
		created_by=data["created_by"]
		tstamp=data["timestamp"]
		intsource=data["source"]
		intdest=data["destination"]
		isvalidDate = True
		try:
			date_object = datetime.strptime(tstamp, "%d-%m-%Y:%S-%M-%H")
			date_object = str(date_object)
		except ValueError:
			isvalidDate = False
		src=int(intsource)
		dst=int(intdest)
		source=0
		dest=0
		with open('AreaNameEnum.csv', 'r') as file:
			reader = csv.reader(file)
			for row in reader:
				if row[0]==intsource:
					source=int(row[0])
				if row[0]==intdest:
					dest=int(row[0])
		url = 'http://127.0.0.1:5000/api/v1/db/read'
		myobj = {"command": "select","table":"users","where":"username="+"'"+created_by+"'"}
		response = requests.post(url, json = myobj)
		y = response.json()
		n = len(y)
		if(source==0 or dest==0 or (source>0 and dest>0 and source==dest) or not(isvalidDate) or n==0):
			return jsonify ({}),400
		elif(n==1 and isvalidDate):
			url = 'http://127.0.0.1:5000/api/v1/db/write'
			myobj = {"command": "insert","table":"rides","column_list":{"created_by":"'"+created_by+"'","time_stamp":"'"+data["timestamp"]+"'","source":"'"+intsource+"'","destination":"'"+intdest+"'"}}
			response = requests.post(url, json = myobj)
			return jsonify ({}),201
	else:
		return jsonify ({}),400


@app.route('/api/v1/rides',methods=["GET"])
def upcoming_rides():
	source = request.args.get('source')
	destination = request.args.get('destination')
	current_time = datetime.now()
	src = 0
	dest = 0
	with open('AreaNameEnum.csv', 'r') as file:
		reader = csv.reader(file)
		for row in reader:
			if row[0]==source:
				src=int(row[0])
			if row[0]==destination:
				dest=int(row[0])
	if(src==0 or dest==0 or (src>0 and dest>0 and src==dest)):
		return jsonify({}),400
	else:
		url = 'http://127.0.0.1:5000/api/v1/db/read'
		myobj = {"command": "select","table":"rides","where":"source="+str(src)+" and destination="+str(dest)}
		response = requests.post(url, json = myobj)
		x =  response.json()
		l=[]
		for i in x:
			temp = i[2].split(':')[0]
			temp1 = i[2].split(':')[1]
			f = temp.split('-')
			d = int(f[0])
			m = int(f[1])
			yy = int(f[2])
			f1 = temp1.split('-')
			ss = int(f1[0])
			mm = int(f1[1])
			h = int(f1[2])
			if(datetime(yy, m, d, h,mm,ss)>current_time):
				p={"username":i[1],"rideid":str(i[0]),"timestamp":i[2]}
				l.append(p)
		if(len(l)>0):
			return jsonify(l),200
		else:
			return jsonify({}),204


@app.route('/api/v1/rides/<rideid>',methods=["GET"])
def ride_details(rideid):
	url = 'http://127.0.0.1:5000/api/v1/db/read'
	myobj = {"command": "select","table":"rides","where":"rideid="+rideid}
	response = requests.post(url, json = myobj)
	n = len(response.json())
	if(n==1):
		myobj = {"command": "select","table":"ridepool","column_list":["username"],"where":"rideid="+rideid}
		resp1 = requests.post(url, json = myobj)
		ride = response.json()[0]
		q=[]
		for i in resp1.json():
			for j in i:
				q.append(j)
		p={"rideid":str(ride[0]),"created_by":ride[1],"users":q,"timestamp":ride[2],"source":str(ride[3]),"destination":str(ride[4])}
		return jsonify(p),200
	else:
		return '',204


@app.route('/api/v1/rides/<rideid>',methods=["POST"])
def join_ride(rideid):
	n1=0
	n2=0
	data = request.get_json()
	print(data)
	if("username" in data):
		url = 'http://127.0.0.1:5000/api/v1/db/read'
		obj1 = {"command":"select","table":"users","where":"username='"+data["username"]+"'"}
		resp1 = requests.post(url, json = obj1)
		n1 = len(resp1.json())
		obj2 = {"command":"select","table":"rides","where":"rideid="+rideid}
		resp2 = requests.post(url, json = obj2)
		n2 = len(resp2.json())
		obj3 = {"command":"select","table":"rides","where":"created_by='"+data["username"]+"' and rideid="+rideid}
		resp3 = requests.post(url, json = obj3)
		n3 = len(resp3.json())
		if(n1==1 and n2==1):
			url1 = 'http://127.0.0.1:5000/api/v1/db/write'
			obj = {"command":"select","table":"ridepool","where":"rideid="+rideid+" and "+"username='"+data["username"]+"'"}
			resp = requests.post(url, json=obj)
			if(len(resp.json())==0 and n3==0):
				obj = {"command":"insert","table":"ridepool","column_list":{"rideid":rideid,"username":"'"+data["username"]+"'"}}
				resp = requests.post(url1, json=obj)
				return jsonify({}),200
			else:
				return "Already part of ride.",400
		else:
			return "Creator of ride cannot join the same ride.",400
	else:
		return jsonify({}),400


@app.route('/api/v1/rides/<rideid>',methods=["DELETE"])
def delete_ride(rideid):
	url = 'http://127.0.0.1:5000/api/v1/db/read'
	myobj = {"command": "select","table":"rides","where":"rideid="+rideid}
	response = requests.post(url, json = myobj)
	n = len(response.json())
	if(n>0):
		url1 = 'http://127.0.0.1:5000/api/v1/db/write'
		obj1 = {"command": "delete","table":"rides","where":"rideid="+rideid}
		resp1 = requests.post(url1, json = obj1)
		obj2 = {"command": "delete","table":"ridepool","where":"rideid="+rideid}
		resp2 = requests.post(url1, json = obj2)
		return jsonify({}),200
	else:
		return jsonify({}),400


@app.route('/api/v1/db/write',methods=["POST"])
def write_db():
	data = request.get_json()
	if("table" not in data or "command" not in data):
		return "Incorrect command/data.",400
	else:
		table=data["table"]
	if(data["command"]=="insert"):
		cols = data["column_list"]
		s=""
		for i in cols:
			s=s+i+","
		s=s[:len(s)-1]
		t=""
		for i in cols:
			t=t+cols[i]+","
		t=t[:len(t)-1]
		sql = "insert into "+table+"("+s+") VALUES ("+t+")"
	elif(data["command"]=="delete"):
		s = ""
		sql = "delete from "+table 
		if("where" in data):
			sql = sql + " where "+ data["where"]
	else:
		return "Incorrect command/data.",400
	try:
		with sqlite3.connect("rideshare.db") as con:
			cur = con.cursor()
			cur.execute(sql)
			con.commit()
		return "Ok",200
	except:
		return "Incorrect command/data.",400

@app.route('/api/v1/db/read',methods=["POST"])
def read_db():
	data = request.get_json()
	if("table" not in data):
		return "Incorrect command/data.",400
	else:
		table=data["table"]
	sql = "select "
	if(data["command"]=="select"):
		if("column_list" in data):
			for i in data["column_list"]:
				sql = sql + i + ","
			sql = sql[:len(sql)-1] + " from " + table
		else:
			sql = sql+"* from "+table
		if("where" in data):
			sql = sql + " where "+ data["where"]
		if("group by" in data):
			sql = sql + " group by "
			for i in data["group by"]:
				sql = sql + i + ","
			sql = sql[:len(sql)-1]
		try:
			with sqlite3.connect("rideshare.db") as con:
				cur = con.cursor()
				cur.execute(sql)
				rows = cur.fetchall()
				con.commit()
			return jsonify(rows),200
		except:
			return "Incorrect command/data.",400
	else:
		return "Incorrect command/data.",400


if __name__ == '__main__':	
	app.debug=True
	app.run()