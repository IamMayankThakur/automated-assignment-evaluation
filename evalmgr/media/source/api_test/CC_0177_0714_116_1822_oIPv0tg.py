from flask import *
import csv
import re
import string
import requests
from flask_api import status  
import sqlite3
import datetime
app = Flask(__name__)
def db(i):
	if i==0:
		con = sqlite3.connect("assign.db")
		con.execute("create table User (uid INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, password TEXT NOT NULL)")
		con.execute("create table Ride (ride_id INTEGER PRIMARY KEY AUTOINCREMENT, ride_s TEXT NOT NULL,ride_s_enum INTEGER , ride_d TEXT NOT NULL,ride_d_enum INTEGER,timestamp TEXT NOT NULL,user1 TEXT NOT NULL,user2 TEXT,user3 TEXT,user4 TEXT)")
		print("Table created successfully")
		con.close()

#1st api
@app.route("/api/v1/users",methods=["PUT"])
def inex():
	user=request.get_json()["username"]
	pas=request.get_json()["password"]
	pas=pas.lower()
	params1 = {
		"table":"User",
		"columns":"username",
		"where":""
	}
	if(user==""):
		return make_response("Usename cant be empty",400,{"Content-type":"application/json"})
	try:
		r = requests.post("http://localhost:80/api/v1/db/read",json=params1)  
	except:
		return make_response("Service not available",500,{"Content-type":"application/json"})		
	user_name_enter=(r.text).split("\n")
	for i in user_name_enter:
		if(i.strip(",")==str(user)):
			return make_response("Usename already exist",400,{"Content-type":"application/json"})
	params = {
		"insert":str(user)+","+str(pas),
		"column":"username,password",
		"table":"User"
	}
	if(len(pas)!=40):
		return make_response("Password not in correct format",400,{"Content-type":"application/json"})
	if(all(c in string.hexdigits for c in pas)==False):
		return make_response("Password not in correct format",400,{"Content-type":"application/json"})
	try:
		r = requests.post("http://localhost:80/api/v1/db/write",json=params)
	except:
		return make_response("Service not available",500,{"Content-type":"application/json"})
	return make_response("{}",201,{"Content-type":"application/json"})

#2nd api
@app.route("/api/v1/users/<usernam>",methods=["DELETE"])
def delete(usernam): 
	with sqlite3.connect("assign.db") as con:  
		cur = con.cursor()
		params1 = {
		"table":"User",
		"columns":"username",
		"where_part":"1",
		"where":"username=",
		"condition":usernam
	}
		r = requests.post("http://localhost:80/api/v1/db/read",json=params1)  
		user_name_enter=(r.text).split("\n")
		flag=0
		for i in user_name_enter:
			if(i.strip(",")==str(usernam)):
				flag=1
		if(flag==0):
			return make_response("Usename not exist",405,{"Content-type":"application/json"})
		parm = {
		"table":"Ride",
		"columns":"*",
		"where_part":"1",
		"condition":usernam,
		"where":"user1="
		}
		r = requests.post("http://localhost:80/api/v1/db/read",json=parm)
		if(r.text.strip()!=""):
			abort(400,"User exists in a ride cant be deleted")
		parm["where"]="user2="
		r = requests.post("http://localhost:80/api/v1/db/read",json=parm)
		if(r.text.strip()!=""):
			abort(400,"User exists in a ride cant be deleted")
		parm["where"]="user3="
		r = requests.post("http://localhost:80/api/v1/db/read",json=parm)
		if(r.text.strip()!=""):
			abort(400,"User exists in a ride cant be deleted")
		parm["where"]="user3="
		r = requests.post("http://localhost:80/api/v1/db/read",json=parm)
		if(r.text.strip()!=""):
			abort(400,"User exists in a ride cant be deleted") 
		param = {
		"table":"Ride",
		"columns":"*",
		"where":""
		}
		params = {
					"delete":"1",
					"where":usernam,
					"table":"User"
				}
		r = requests.post("http://localhost:80/api/v1/db/write",json=params)
		return make_response("{}",200,{"Content-type":"application/json"})

#3rd api
@app.route("/api/v1/rides",methods=["POST"])
def ride():  
	created_by=request.get_json()["created_by"]
	timestamp=request.get_json()["timestamp"]
	source_enum=request.get_json()["source"]
	destination_enum=request.get_json()["destination"]
	source="NULL";
	destination="NULL";
	if(created_by=="" or timestamp=="" or source_enum=="" or destination_enum==""):
		return make_response("Parameters cant be empty",400,{"Content-type":"application/json"})	
	if(source_enum==destination_enum):
		return make_response("Source and destination cannot be same",405,{"Content-type":"application/json"})
	p = re.findall(r'^([1-9]|([012][0-9])|(3[01]))-([0]{0,1}[1-9]|1[012])-\d\d\d\d:[0-5][0-9]-[0-5][0-9]-[012]{0,1}[0-9]$',timestamp)
	if(len(p)==0):
		return make_response("Timestamp format error",400,{"Content-type":"application/json"})
	f = open('AreaNameEnum.csv')
	csv_f = csv.reader(f)
	for row in csv_f:
		if(row[0]==source_enum):
			source=row[1]
		elif(row[0]==destination_enum):
			destination=row[1]
	params = {
		"table":"User",
		"columns":"*",
		"where_part":"1",
		"where":"username=",
		"condition":created_by
	}



	r = requests.post("http://localhost:80/api/v1/db/read",json=params)
	row = r.text.split("\n")
	if(len(row)>1):
		params = {
			"insert":str(source)+","+str(source_enum)+","+str(destination)+","+str(destination_enum)+","+timestamp+","+created_by+","+"NULL,NULL,NULL",
			"column":"ride_s, ride_s_enum,ride_d,ride_d_enum,timestamp,user1,user2,user3,user4",
			"table":"Ride"
		}
		if(source=="NULL"or destination=="NULL"):
			return make_response("ENUM NOT EXISTS",400,{"Content-type":"application/json"})
		r = requests.post("http://localhost:80/api/v1/db/write",json=params)
		return make_response("{}",200,{"Content-type":"application/json"})
	else:
		return make_response("User does not exists",400,{"Content-type":"application/json"})


#4th api to list all the rides given source and destination enum
@app.route("/api/v1/rides",methods=["GET"])
def listrides():
	source = request.args.get('source')
	destination = request.args.get('destination')
	if(source=="" or destination==""):
		return make_response("Parameters cant be empty",400,{"Content-type":"application/json"})
	params = {
		"table":"Ride",
		"columns":"*",
		"where":"where ride_s_enum="+source+" AND ride_d_enum="+destination
	}
	r = requests.post("http://localhost:80/api/v1/db/read",json=params)
	l = []
	for row in r.text.split("\n"):
		ro = row.split(",")
		print(len(ro))
		d = {}
		if(len(ro)>5):
			d["rideId"]=ro[0]
			d["username"]=ro[6]
			d["timestamp"]=ro[5]
			timestamp = ro[5]
			time = timestamp.split(":")[1]
			date = timestamp.split(":")[0]
			tim_arr = time.split("-")
			tim = ""
			print(ro[0])
			tim = tim+tim_arr[2]+":"+tim_arr[1]+":"+tim_arr[0]
			dat_arr = date.split("-")
			dat = dat_arr[2]+"-"+dat_arr[1]+"-"+dat_arr[0]
			datetim = dat+" "+tim
			date_time =datetime.datetime.strptime(datetim,"%Y-%m-%d %H:%M:%S")
			present = datetime.datetime.now()
			dif = present - date_time
			print(present)
			print(date_time)
			if(present>date_time):
				pass
			else:
				l.append(d)
	if(len(l)==0):
		return make_response("Rides not exists",204,{"Content-type":"application/json"})
	return jsonify(l)

#5 and 6 api
@app.route("/api/v1/rides/<rideId>",methods=["POST","GET"])
def join(rideId):
	if(request.method=="POST"):#Join to a ride complete
		user = request.get_json()["username"]
		with sqlite3.connect("assign.db") as con:
			cur = con.cursor()
			sql = "SELECT * from User WHERE username=?"
			cur.execute(sql,(user,))
			rows = cur.fetchall()
			if(len(rows)>0):
				sql = "SELECT user1,user2,user3,user4 FROM Ride WHERE ride_id=?"
				cur.execute(sql,(rideId,))
				row = cur.fetchone()
				print(row)
				user1=row[0]
				user2=row[1]
				user3=row[2]
				user4=row[3]
				if(user==user1 or user==user2 or user==user3 or user4==user):
					return make_response("User already in the ride",400,{"Content-type":"application/json"})
				else:
					if(user2=="NULL"):
						params ={
							"update":"1",
							"set":"user2=",

							"user":user,
							"where":"ride_id="+rideId,
							"table":"Ride"
						}
						r = requests.post("http://localhost:80/api/v1/db/write",json=params)
						return make_response("{}",200,{"Content-type":"application/json"})
					elif(user3=="NULL"):
						params ={
							"update":"1",
							"set":"user3=",
							"user":user,
							"where":"ride_id="+rideId,
							"table":"Ride"
						}
						r = requests.post("http://localhost:80/api/v1/db/write",json=params)
						return make_response("{}",200,{"Content-type":"application/json"})
					elif(user4=="NULL"):
						params ={
							"update":"1",
							"set":"user4=",
							"user":user,
							"where":"ride_id="+rideId,
							"table":"Ride"
						}
						r = requests.post("http://localhost:80/api/v1/db/write",json=params)
						#print("successfully joined the ride")
						return make_response("{}",200,{"Content-type":"application/json"})
					else:
						params ={
							"update":"1",
							"set":"user4=",
							"user":user4+","+user,
							"where":"ride_id="+rideId,
							"table":"Ride"
						}
						r = requests.post("http://localhost:80/api/v1/db/write",json=params)
						print("successfully joined the ride")
						return make_response("{}",200,{"Content-type":"application/json"})
						#return make_response("CAPACITY LIMIT REACHED",401,{"Content-type":"application/json"})

			else:
				header = {"Content-type":"application/json"}
				return make_response('User not registered',400,	header)
	if(request.method=="GET"):#details of a ride
		params = {
			"table":"Ride",
			"columns":"*",
			"where":"where ride_id="+rideId
		}
		r = requests.post("http://localhost:80/api/v1/db/read",json=params)
		row = r.text.split(",")
		if(len(row)==1):
			abort(400,"RIDE NOT FOUND")
		f= {}
		f["ride_id"]=row[0]
		f["created_by"]=row[6]
		user2 = row[7]
		user3 = row[8]
		user4 = row[9]
		f["users"]=list()
		for i in range(6,len(row)-1):
			ss=row[i].strip("\n")
			if(ss!="NULL"):
				f["users"].append(ss)
		f["timestamp"] = row[5]
		f["source"] = row [1]
		print(jsonify(f["users"]))
		f["destination"] = row[3]
		return jsonify(f)



#7th api
@app.route("/api/v1/rides/<rideId>",methods=["DELETE"])
def delete_ride(rideId):
	if(rideId==""):
		abort(400,"Ride id not found")
	params1 = {
	"table":"Ride",
	"columns":"ride_id",
	"where":""
		}
	r = requests.post("http://localhost:80/api/v1/db/read",json=params1)  
	if(r.text==""):
		abort(400,"Error in reading")
	user_name_enter=(r.text).split("\n")
	flag=0
	for i in user_name_enter:
		if(i.strip(",")==str(rideId)):
			flag=1
	if(flag==0):
		return make_response("Ride not exist",405,{"Content-type":"application/json"})
	params = {
		"delete":"1",
		"table":"Ride",
		"where":rideId
	} 
	r = requests.post("http://localhost:80/api/v1/db/write",json=params)
	return make_response("{}",200,{"Content-type":"application/json"})

#api number 8 complete ....works only for our database ....
@app.route("/api/v1/db/write",methods=["POST"])
def write_to_db():
	#cur.execute("INSERT into User (username, password) values (?,?)",(user,pas)) 
	delete = "NULL"
	data = "NULL"
	column1 = "NULL"
	table = "NULL"
	WHERE = "NULL"
	update = "NULL"
	SET = "NULL"
	user = "NULL"
	try:#if the instruction is an update 
		update = request.get_json()["update"]
		table = request.get_json()["table"]
		SET = request.get_json()["set"]
		user = request.get_json()["user"]
		WHERE = request.get_json()["where"]
	except:
		pass
	try:#if the instruction is a delete
		delete = request.get_json()["delete"]
		WHERE = request.get_json()["where"]
		table = request.get_json()["table"]
	except:
		pass
	try:#if the instruction is a insert
		data = request.get_json()["insert"]
		column1 = request.get_json()["column"]
		table = request.get_json()["table"]
	except:
		pass
	if(update!="NULL"):
		sql = "UPDATE "+table+" SET "+SET+" ? WHERE "+WHERE
		with sqlite3.connect("assign.db") as con:
				cur = con.cursor()
				cur.execute(sql,(user,))
				con.commit()
				return "update over"
	if(delete!="NULL"):
		if(table=="User"):
			sql = "DELETE from User WHERE username=?"
			with sqlite3.connect("assign.db") as con:
				cur = con.cursor()
				cur.execute(sql,(WHERE,))
				con.commit()
				return "{}"
		if(table=="Ride"):
			sql = "DELETE from Ride WHERE ride_id=?"
			with sqlite3.connect("assign.db") as con:
				cur = con.cursor()
				cur.execute(sql,(WHERE,))
				con.commit()
				return "{}"
	else:
		with sqlite3.connect("assign.db") as con:
			data1 = data.split(",")
			if(table=="Ride"):
				sql = "INSERT into "+str(table)+" ("+str(column1)+") values (?,?,?,?,?,?,?,?,?)"
			if(table=="User"):
				sql = "INSERT into "+str(table)+" ("+str(column1)+") values (?,?)"
			cur = con.cursor()
			cur.execute(sql,([d for d in data1]))
			con.commit()
			return "{}"
#api number 9 complete
@app.route("/api/v1/db/read",methods=["POST"])
def read_db():
	where_part = "NULL"
	condition = "NULL"
	try:
		where_part = request.get_json()["where_part"]
		condition = request.get_json()["condition"]
		table = request.get_json()["table"]
		columns =request.get_json()["columns"]
		where = request.get_json()["where"]
	except:
		pass
	if(where_part!="NULL"):
		sql_query = "SELECT "+columns+" from "+table+" WHERE "+where+" ?"
		with sqlite3.connect("assign.db") as con:
			con.row_factory = sqlite3.Row
			cur = con.cursor()
			cur.execute(sql_query,(condition,))
			rows = cur.fetchall()
			s= ""
			for row in rows:
				for r in row:
					s = s+str(r)+","
				s = s+"\n"
			return s
	else:
		table = request.get_json()["table"]
		columns =request.get_json()["columns"]
		where = request.get_json()["where"]
		sql_query = "SELECT "+columns+" from "+table+" "+where
		with sqlite3.connect("assign.db") as con:
			con.row_factory = sqlite3.Row
			cur = con.cursor()
			cur.execute(sql_query)
			rows = cur.fetchall()
			s= ""
			for row in rows:
				for r in row:
					s = s+str(r)+","
				s = s+"\n"
			return s

#extra api for User table view
@app.route("/view")  
def view():  
    params = {
    	"table":"User",
    	"columns":"*",
    	"where":""
    }
    r = requests.post("http://localhost:80/api/v1/db/read",json=params)  
    return r.text

#extra api for Ride table view
@app.route("/view1")  
def view1():
	params = {
		"table":"Ride",
		"columns":"*",
		"where":""
	}
	r = requests.post("http://localhost:80/api/v1/db/read",json=params)  
	return r.text


i=0
if __name__ == "__main__":
	try:
		db(i)
	except Exception as e:
		pass
	app.run(host='0.0.0.0',port='80')
#	app.run()
