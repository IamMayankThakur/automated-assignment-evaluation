from flask import Flask, render_template,jsonify,request,abort
import sqlite3,requests,json,re,csv

from datetime import datetime

conn = sqlite3.connect('database.db',check_same_thread=False)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS users(username text primary key, password text not null);")
conn.commit()

cursor.execute("CREATE TABLE IF NOT EXISTS rides(rideid integer primary key, username text, time_stamp text, source integer, dest integer, users text);")
conn.commit()


csv_file = r"C:\Users\VINU PC\Downloads\AreaNameEnum.csv"

#cursor.execute("ALTER TABLE rides autoincrement=1001;")
#conn.commit()

app=Flask(__name__)

#str = '30-01-2020:13-55-00'

	

def validDateTime(date):
	datetime_object = datetime.strptime(date, '%d-%m-%Y:%S-%M-%H')
	now = datetime.now()
	return(datetime_object > now)  

def validSrcDest(source, destination):
	rows = []
	with open(csv_file, 'r') as csvfile:
	    csvreader = csv.reader(csvfile)
	    for row in csvreader:
	        rows.append(row)
	src = False
	dest = False
	for i in rows:
	    if(i[0] == str(source)):
	        src = True
	    if(i[0] == str(destination)):
	    	dest = True
	if(src == False or dest == False):
		return False
	return True

@app.route('/api/v1/db/read',methods=["POST"])
def read_database():	
	#table=request.get_json()["table"]
	#column=request.get_json()["column"]
	data=request.get_json()["data"]
	operation=request.get_json()["operation"]
	if(operation == "check_users"):
		cursor.execute("select * from users where username = ?",(data,))
		rows = cursor.fetchall()
		if(rows):
			status=400
		else:
			status=201
		response = {}
	elif(operation == "check_user_exists"):
		cursor.execute("select * from users where username = ?",(data,))
		rows = cursor.fetchall()
		if(rows):
			status=201
		else:
			status=400
		response = {}
	elif(operation == "list_rides"):
		cursor.execute("select * from rides where source = ? and dest = ?",(data[0], data[1]))
		rows = cursor.fetchall()
		response = []
		for row in rows:
			if(validDateTime(row[2])):
				d = dict()
				d["rideId"] = row[0]
				d["username"] = row[1]
				d["timestamp"] = row[2]
				response.append(d)
		if(response == []):
			status = 204
		else:
			status=200

	elif(operation == "list_ride_details"):
		data = int(data)
		cursor.execute("select * from rides where rideid = ?",(data,))
		rows = cursor.fetchall()
		users_list = []
		if(rows):
			for row in rows:
				username = row[1]
				timestamp = row[2]
				source = row[3]
				dest = row[4]
				users = row[5]
				if(users):
					users_list = users.split(',')	
			status=200
			response = {"rideId" : data , "timestamp" : timestamp, "created_by" : username, "source" : source,  "destination" : dest , "users" : users_list}
		else:
			status=204
			response={}

	elif(operation == "check_rideid"):
		data = int(data)
		cursor.execute("select * from rides where rideid = ?",(data,))
		rows = cursor.fetchall()
		if(rows):
			status=201
		else:
			status=400
		response={}	
	return jsonify(response),status


@app.route('/api/v1/db/write',methods=["POST"])
def write_database():	
	table=request.get_json()["table"]
	#column=request.get_json()["column"]
	data=request.get_json()["data"]
	#operation=request.get_json()["operation"]
	try:
		if(table == "users"):
			cursor.execute("insert into users values (?,?);", (data[0], data[1]))
			conn.commit()
			status=201
		elif(table == "rides"):
			cursor.execute("insert into rides(rideid, username, time_stamp, source, dest) values (NULL,?,?,?,?);", (data[0], data[1], data[2], data[3]))
			conn.commit()
			status=201
		elif(table == "rides_update"):
			cursor.execute("select * from rides where rideid = ?",(data[0],))
			rows = cursor.fetchall()
			row = rows[0]
			if(row[5]):
				users = row[5] + "," + data[1]
			else:
				users = data[1]
			cursor.execute("update rides set users = ? where rideid = ?;", (users,data[0]))
			conn.commit()
			status=200	
	except:
		status=400
	return jsonify(""),status

def isSHA(str):
	if(len(str) != 40):
		return False
	try:
		hex_str = int(str,16)
	except ValueError:	
		return False
	return True

@app.route('/api/v1/users',methods=["PUT"])
def add_users():
	username=request.get_json()["username"]
	password=request.get_json()["password"]

	if(isSHA(password) == False):
		return jsonify(""),400

	data = {"data":[username, password],"table":"users"}
	r = requests.post('http://localhost:5000/api/v1/db/write', json=data)
	return jsonify(""),r.status_code


@app.route('/api/v1/rides',methods=["POST"])
def create_ride():
	username=request.get_json()["created_by"]
	source=request.get_json()["source"]
	destination=request.get_json()["destination"]
	timestamp=request.get_json()["timestamp"]
	
	pattern = re.compile("^(3[01]|[12][0-9]|0[1-9])-(1[0-2]|0[1-9])-[0-9]{4}:([0-5]?[0-9])-([0-5]?[0-9])-(2[0-3]|[01][0-9])$")
	if(bool(pattern.match(timestamp)) == False):
		return jsonify(""),400
	
	if(validSrcDest(source, destination) == False):
		return jsonify(""),400
	
	data={"data":username, "operation":"check_user_exists"}
	r = requests.post('http://localhost:5000/api/v1/db/read', json=data)
	if(r.status_code == 400):
		return jsonify(""),400
	data = {"data":[username, timestamp, source, destination],"table":"rides"}
	r = requests.post('http://localhost:5000/api/v1/db/write', json=data)
	return jsonify(""),r.status_code
	
@app.route('/api/v1/rides')
def list_rides():	
	source = request.args.get('source')
	dest = request.args.get('destination')
	if(source is None or dest is None):
		return jsonify(""),400

	
	if(validSrcDest(source, dest) == False):
		return jsonify(""),400
		
	data={"data":[source, dest], "operation":"list_rides"}
	r = requests.post('http://localhost:5000/api/v1/db/read', json=data)
	return (r.text, r.status_code,r.headers.items())


@app.route('/api/v1/rides/<rideId>')
def list_ride_details(rideId):	
	data={"data":rideId, "operation":"list_ride_details"}
	r = requests.post('http://localhost:5000/api/v1/db/read', json=data)
	return (r.text, r.status_code,r.headers.items())

@app.route('/api/v1/rides/<rideId>',methods=["POST"])
def join_ride(rideId):	
	username=request.get_json()["username"]
	
	data={"data":username, "operation":"check_user_exists"}
	r = requests.post('http://localhost:5000/api/v1/db/read', json=data)
	if(r.status_code == 400):
		return jsonify(""),400

	data={"data":rideId, "operation":"check_rideid"}
	r = requests.post('http://localhost:5000/api/v1/db/read', json=data)
	if(r.status_code == 400):
		return jsonify(""),400
	
	data = {"data":[rideId, username],"table":"rides_update"}
	r = requests.post('http://localhost:5000/api/v1/db/write', json=data)
	return jsonify(""),r.status_code
	

@app.route('/api/v1/users/<username>',methods=["DELETE"])
def delete_user(username):	
	data={"data":username, "operation":"check_user_exists"}
	r = requests.post('http://localhost:5000/api/v1/db/read', json=data)
	if(r.status_code == 400):
		return jsonify(""),400
	cursor.execute("delete from users where username = ?",(username,))
	conn.commit()
	return jsonify(""),200


@app.route('/api/v1/rides/<rideId>',methods=["DELETE"])
def delete_rides(rideId):	
	data={"data":rideId, "operation":"check_rideid"}
	r = requests.post('http://localhost:5000/api/v1/db/read', json=data)
	if(r.status_code == 400):
		return jsonify(""),400
	cursor.execute("delete from rides where rideid = ?",(rideId,))
	conn.commit()
	return jsonify(""),200



if __name__ == '__main__':	
	app.debug=True
	app.run()