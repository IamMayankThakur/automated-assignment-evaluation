import sqlite3
from flask import Flask, render_template,jsonify,request,abort,Response
import requests
import json
import csv

from datetime import datetime
app=Flask(__name__)
cursor = sqlite3.connect("rideshare.db")


cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
          name varchar(20) primary key,
  		  pass varchar(20)
        );
    """)

cursor.execute("""
        CREATE TABLE IF NOT EXISTS rideusers(
         id int not null,
  		 name varchar(20),
		foreign key (name) references users(name) on delete cascade,
		foreign key (id) references rides(rideid) on delete cascade,
		primary key(id,name)
        );
    """)

cursor.execute("""
    CREATE TABLE IF NOT EXISTS place(
      id int primary key,
	  name varchar(20)
    );
""")
with open('AreaNameEnum.csv') as File:  
	reader = csv.reader(File)

	i=0
	for row in reader:
		if(i):
			try:
				d=[row[0],row[1]]
				sql="insert into place values (?,?)"
				
				cursor.execute(sql,d)
			except:
				continue	
		i=1		
	cursor.commit()

cursor.execute("""
        CREATE TABLE IF NOT EXISTS rides(
          rideid integer  primary key AUTOINCREMENT,
          name varchar(20) not null ,
  		  timest DATETIME not null,
  		  source varchar(30) not null,
  		  desti varchar(30) not null,
  		  foreign key (name) references users(name) on delete cascade, 
  		  foreign key (source) references place(id) on delete cascade,
  		  foreign key (desti) references place(id) on delete cascade
        );
    """)

cursor.commit()

def fun(passw):
	if(len(passw)!=40):
		return 0
	for i in passw:
		if(not i.isdigit() and not (i.isalpha() and ord('a')<=ord(i) and ord('f')>=ord(i)) ):
			return 0
	return 1
@app.route("/")
def hello():
    return "<h1>hello world</h1>"
@app.route("/api/v1/db/read",methods=["POST"])
def read_database():
	cursor = sqlite3.connect("rideshare.db")
	resp_dict={}
	val=request.get_json()["insert"]
	table=request.get_json()["table"]
	column=request.get_json()["column"]
	where_check_cond=request.get_json()["where"]
	check_string=""
	for i in range(len(where_check_cond)-1):
		check_string+=where_check_cond[i]+" = "+"'"+val[i]+"'"+" AND "
	check_string+=where_check_cond[len(where_check_cond)-1]+" = "+"'"+val[len(where_check_cond)-1]+"'"
	##print(check_string,"aaaaaaaaaaaaa")
		

	r=""
	s=""
	e=len(column)-1
	for i in range(e):
		r+=column[i]+","
		s+="?,"
	r+=column[e]
	s+="?"
	for i in range(len(val)):
		val[i]=val[i].encode("utf8")

	
	sql="select "+r+" from "+table+" where "+check_string+";"
	##print(sql)
	resp=cursor.execute(sql)
	#print(resp)
	resp_check=resp.fetchall()
	#print(len(resp_check),"length of resp_check")
	if(len(resp_check) == 0):
		resp_dict["response"]=0
		return json.dumps(resp_dict)
	else:
		
		#print(resp_check)
		#print(list(resp_check[0]))
		#print(len(resp_check),"count of all rows")
		resp_dict["count"]=len(resp_check)
		for i in range(len(resp_check)):
			for j in range(len(column)):
				resp_dict.setdefault(column[j],[]).append(list(resp_check[i])[j])
		#print(resp_dict,"hii i am dict")
		#print("user does exists from read_Db")
		resp_dict["response"]=1
		return json.dumps(resp_dict)

@app.route("/api/v1/db/write",methods=["POST"])
def to_database():
	
	indicate=request.get_json().get("indicate")
	#print("indicate:", indicate)
	try :
		cursor = sqlite3.connect("rideshare.db")
		cursor.execute("PRAGMA FOREIGN_KEYS=on")
		cursor.commit()
	except Exception as e:
		#print("Database connect error:",e)
		pass
	if(indicate=="0"):
		val=request.get_json().get("insert")
		table=request.get_json().get("table")
		column=request.get_json().get("column")
		#print("val:",val)
		#print("table",table)
		#print("column:", column)
		r=""
		s=""
		e=len(column)-1
		for i in range(e):	
			r+=column[i]+","
			s+="?,"
		r+=column[e]
		s+="?"
		for i in range(len(val)):
			val[i]=val[i]

		try:

			sql="insert into "+table+" ("+r+")"+" values ("+s+")"
			#print("query:",sql)
			cursor.execute(sql,val)

			cursor.commit()
			sql="select * from "+table
			et=cursor.execute(sql)
			rows = et.fetchall()

			sql="select * from users"
			et=cursor.execute(sql)
			rows = et.fetchall()
			return jsonify(1)
		except Exception as e:
			#print(e)
			sql="select * from "+table
			et=cursor.execute(sql)
			rows = et.fetchall()
			#for row in rows:
				#print(row,"we")
			return jsonify(0)
		return jsonify(1)
	elif(indicate=='1'):
		table=request.get_json()["table"]
		delete=request.get_json()["delete"]
		column=request.get_json()["column"]
		#print("table",table)
		#print("delete:",delete)
		try:
			#print("asdf")
			sql="select * from "+table+" WHERE "+column+"=(?)"
			#print("query",sql)
			et=cursor.execute(sql,(delete,))
			if(not et.fetchone()):
				#print("fs")
				return jsonify(0)
			
			sql = "DELETE from "+table+" WHERE "+column+"=(?)"
			#print(table,column,delete)
			#print(sql)
			et=cursor.execute(sql,(delete,))
			#print(et.fetchall())
			cursor.commit()
		except Exception as e:
			#print(e)
			#print("rt")
			return jsonify(0)
		return jsonify(1)
	else:
		return jsonify(0)


@app.route("/api/v1/users",methods=["PUT"])
def add():
	if(request.method!="PUT"):
		abort(405,"method not allowed")

	name=request.get_json()["username"]
	passw=request.get_json()["password"]
	#print("name:", name)
	#print("pass:", passw)

	d=[name,passw]
	if(fun(passw)==0):
		abort(400,"password is not correct")
	res=requests.post("http://34.201.201.196/api/v1/db/write",json={"insert":d,"column":["name","pass"],"table":"users","indicate":"0"})	

	
	if(res.json()==0):
			abort(400,"user already exists")	
	

	return Response("success",status=201,mimetype='application/json')

rides=[]
rides_id=0
sour={}
des={}

	

@app.route("/api/v1/rides",methods=["POST"])
def insert_rider():
	if(request.method!="POST"):
		abort(405,"method not allowed")
	global rides_id
	name=request.get_json()["created_by"]
	timestamp=request.get_json()["timestamp"]
	source=request.get_json()["source"]
	destination=request.get_json()["destination"]
    
	d=[name,timestamp,source,destination]
	#print(type(timestamp.encode("utf8")))
	#print(timestamp.encode("utf8"))
	try:
		time_object=datetime.strptime(timestamp,'%d-%m-%Y:%S-%M-%H')
	except:
		#print("hii")
		abort(400,"invalid input")

	read_res=requests.post("http://34.201.201.196/api/v1/db/read",json={"insert":d,"column":["name","pass"],"table":"users","where":["name"]})
	if(read_res.json().get("response")==0):
		abort(400,"user name doesn't exists")

	res=requests.post("http://34.201.201.196/api/v1/db/write",json={"insert":d,"column":["name","timest","source","desti"],"table":"rides","indicate":"0"})	
	if(res.json()==0):
		abort(400,"user already exists")

	return Response("success",status=201,mimetype='application/json')

@app.route("/api/v1/users/<name>",methods=["DELETE"])
def remove(name):
	if(request.method!="DELETE"):
		abort(405,"method not allowed")
	res=requests.post("http://34.201.201.196/api/v1/db/write",json={"table":"users","delete":name,"column":"name","indicate":"1"})
	#print(res.json())
	if(res.json()==0):
		abort(400,"user does not  exists")
	elif(res.json()==1):
		return json.dumps({'success':"user has been deleted successfully"}), 200, {'ContentType':'application/json'}

@app.route("/api/v1/rides/<rideId>",methods=["DELETE"])
def delete_rideId(rideId):
	if(request.method!="DELETE"):
		abort(405,"method not allowed")
	res=requests.post("http://34.201.201.196/api/v1/db/write",json={"table":"rides","delete":rideId,"column":"rideid","indicate":"1"})
	if(res.json()==0):
		abort(400,"rideId does not  exists")
	elif(res.json()==1):
		return json.dumps({'success':"deleted successfully"}), 200, {'ContentType':'application/json'}

@app.route("/api/v1/rides/<rideId>",methods=["POST"])
def join_ride(rideId):
	if(request.method!="POST"):
		abort(405,"method not allowed")
	name=request.get_json()["username"]
	d=[name,rideId]
	read_res=requests.post("http://34.201.201.196/api/v1/db/read",json={"insert":d,"column":["name","pass"],"table":"users","where":["name"]})
	if(read_res.json().get("response")==0):
		abort(400,"user doesn't exists")
	d=[rideId,name]
	rideid_check=requests.post("http://34.201.201.196/api/v1/db/read",json={"insert":d,"column":["rideid","name","source","desti"],"table":"rides","where":["rideid"]})
	if(rideid_check.json().get("response")==0):
		abort(400,"ride id doesn't exists")
	
	res=requests.post("http://34.201.201.196/api/v1/db/write",json={"insert":d,"column":["id","name"],"table":"rideusers","indicate":"0"})
	if(res.json()==0):
		abort(400,"rideId does not  exists")
	elif(res.json()==1):
		return json.dumps({'success':"joined successfully"}), 200, {'ContentType':'application/json'}

@app.route("/api/v1/rides/<rideId>",methods=["GET"])
def ride_details(rideId):
	if(request.method!="GET"):
		abort(405,"method not allowed")
	users=""
	d=[rideId]
	user_list=[]
	rideid_check=requests.post("http://34.201.201.196/api/v1/db/read",json={"insert":d,"column":["rideid","name","source","desti","timest"],"table":"rides","where":["rideid"]})
	if(rideid_check.json().get("response")==0):
		abort(400,"rideId does not  exists")
	elif(rideid_check.json().get("response")==1):
		
		joined_users_check=requests.post("http://34.201.201.196/api/v1/db/read",json={"insert":d,"column":["id","name"],"table":"rideusers","where":["id"]})


		return json.dumps({"rideId":rideid_check.json().get("rideid"),
							"created_by":rideid_check.json().get("name")[0],
							"users":joined_users_check.json().get("name"),
							"timestamp":rideid_check.json().get("timest"), 
							"source":rideid_check.json().get("source"),
							"destination":rideid_check.json().get("desti")}),200, {'ContentType':'application/json'}
							
@app.route("/api/v1/rides",methods=["GET"])
def upcoming_rides():
	if(request.method!="GET"):
		abort(405,"method not allowed")
	array_of_rides=[]
	dateTimeObj = datetime.now()
	string=""
	string+=str(dateTimeObj.day)+"-"+str(dateTimeObj.month)+"-"+str(dateTimeObj.year)+":"+str(dateTimeObj.second)+"-"+str(dateTimeObj.minute)+"-"+str(dateTimeObj.hour)
	source=request.args.get('source')
	destination=request.args.get('destination')
	d=[source,destination]				
	src_dest_check=requests.post("http://34.201.201.196/api/v1/db/read",json={"insert":d,"column":["rideid","name","source","desti","timest"],"table":"rides","where":['source','desti']})			
	if(src_dest_check.json().get("response")==0):
		return "no content to send",204,{"ContentType":"application/json"}
	
	str_timestmp=src_dest_check.json().get("timest")
	timestamp1=src_dest_check.json().get("timest")
	for i in range(len(timestamp1)):
		t1 = datetime.strptime(timestamp1[i], "%d-%m-%Y:%S-%M-%H")
		t2 = datetime.strptime(string, "%d-%m-%Y:%S-%M-%H")
		#print(t2)
		#print(t1)
		if(t1>t2):
			array_of_rides.append({"rideId":src_dest_check.json().get("rideid")[i],
								"username":src_dest_check.json().get("name")[i],
								"timestamp":src_dest_check.json().get("timest")[i]})

	return json.dumps(array_of_rides),200,{"ContentType":"application/json"}
							
if __name__ == '__main__':
	app.debug=True
	app.run(host='0.0.0.0')