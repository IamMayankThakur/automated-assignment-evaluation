from flask import Flask, render_template,\
jsonify,request,abort
import string, logging
import psycopg2
import pandas
from datetime import datetime 
def make_connection():
	try:
	    connection = psycopg2.connect(user = "postgres",
	                                  password = "postgres",
	                                  host = "127.0.0.1",
	                                  port = "5432",
	                                  database = "cc_a1")
	    cursor = connection.cursor()

	except (Exception, psycopg2.Error) as error :
	    print ("Error while connecting to PostgreSQL", error)
	    abort(405)
	finally:
		return connection

app=Flask(__name__)


def checkSHA(pwd):
	if(len(pwd)!=40 or not(all(c in string.hexdigits for c in pwd))):
		#print(pwd)
		return False
	else:
		return True
def locExists(num):
	colnames = ['AreaNo', 'AreaName']
	data = pandas.read_csv('AreaNameEnum.csv', names=colnames)
	areas = data.AreaNo.tolist()
	if(num not in areas):
		return 0
	else:
		return 1

@app.route("/api/v1/users", methods=["PUT"])
def add_user():
	created = 201
	username = request.get_json()["username"]
	pwd = request.get_json()["password"]

	if(username==''):
		abort(400)

	elif(not(checkSHA(pwd))):
		abort(405)

	else:
		#Create new request to insert
		insert_request = {"insert": [username,pwd], "table": "users"}
		read_req = {"table": "users", "where" :"username='"+username+"'"}

		#Checking if user exists or not
		if(read(read_req)!=0):
			print("User already exists")
			abort(400)

		#inserting new user
		insert(insert_request)
		print(request.get_json())
		return "",created


@app.route("/api/v1/users/<name>", methods=["DELETE"])
def del_user(name):
	username = str(name)

	#terminate operation if username doesn't exist
	if(username==''):
		abort(400)

	else:
		#First check if specified user exists or not
		read_req = {"table": "users", "where" :"username='"+username+"'"}
		if(read(read_req)==0):
			print("Can't delete user because he doesnt exist")
			abort(400)
		else:
			try:
				del_user = "DELETE FROM users WHERE username = %s"
				connection = make_connection()
				cursor2 = connection.cursor()
				cursor2.execute(del_user, (username,))
				connection.commit()
				cursor2.close()
				connection.close()
				return '',200
			except (Exception, psycopg2.Error) as error:
				print("Error in Delete operation", error)
				abort(405) #not sure about this



@app.route("/api/v1/rides", methods=["POST"])
def create_ride():
	username = request.get_json()["created_by"]
	timestamp = request.get_json()["timestamp"]


	#checking if timestamp is valid or not
	try:
		ts = datetime.strptime(timestamp,  "%d-%m-%Y:%S-%M-%H")
	except Exception as e:
		print("Incorrect format: ",e)
		abort(400)

	src = request.get_json()["source"]
	dst = request.get_json()["destination"]
	src = str(src).strip()
	dst = str(dst).strip()

	#check if user exists in table
	read_req = {"table": "users", "where" :"username='"+username+"'"}
	
	#non-existing user can't create a ride
	if(read(read_req)==0):
		print("User doesn't exist")
		abort(400)

	#if source or dst is invalid, raise error
	elif(not(locExists(src)) or not(locExists(dst))):
		print("Area doesn't exist")
		abort(400)

	else:
		#persistent storage of ride_id
		#reading from DB each time and updating is too cumbersome
		f = open("ride_id.txt", "r")
		ride_id= f.read()
		ride_id = int(ride_id.strip())
		ride_id+=1
		f.close()
		w = open("ride_id.txt", "w")
		w.write(str(ride_id))
		w.close()

		#Creating request to insert into user_ride table
		insert_user_ride = {"insert": [username,ride_id], "table": "user_ride"}
		insert(insert_user_ride)

		#Creating request to insert into rides table
		insert_ride = {"insert": [ride_id, username, timestamp, src, dst, username], "table": "rides"}
		insert(insert_ride)
		return '',200


@app.route("/api/v1/rides",methods=["GET"])
def ride_listing():
	src = request.args.get('source')
	dst = request.args.get('destination')

	#if source or dst is invalid, raise error
	if(not(locExists(src)) or not(locExists(dst))):
		print("Area doesn't exist")
		abort(400)
	where_clause = "rides.source = "+src +"AND rides.dest = "+dst
	ride_listing_q = {"table": "rides", "where" :where_clause}
	#print(src,dst)
	listing = read(ride_listing_q)
	print(listing)
	if listing==0:
		abort(400)
	else:
		master =[]
		#print(listing)
		for rec in listing:
			slave ={}
			ts = datetime.strptime(rec[2],  "%d-%m-%Y:%S-%M-%H")
			today = datetime.today()
			if(ts > today):
				slave["rideId"] = rec[0]
				slave["username"] = rec[1]
				slave["timestamp"] = rec[2]
				master.append(slave)
			else:
				continue

		return jsonify(master), 200


@app.route('/api/v1/rides/<rideId>',methods=["GET"])
def ride_deets(rideId):
	#Creating request with rideId
	ride_Id = int(rideId)
	print(ride_Id)
	ride_deets_q = {"table": "rides", "where":"rides.ride_id="+str(ride_Id)}
	deets = read(ride_deets_q)

	if(deets ==0):
		print("Ride Id doesnt exist")
		abort(400)

	users = deets[0][5]
	user_list = users.split(",")
	for i in range (0,len(user_list)):
		if(user_list[i]== ''):
			del user_list[i]
	print(user_list)
	master = {"rideId" : deets[0][0],"Created_by" : deets[0][1], "users": user_list, "timestamp: ": deets[0][2], 
	"source": int(deets[0][3]), "destination": int(deets[0][4])}
	return jsonify(master)

@app.route('/api/v1/rides/<rideId>',methods=["POST"])
def join_ride(rideId):
	username = request.get_json()["username"]
	ride_Id = int(rideId)
	ride_deets_q = {"table": "rides", "where":"rides.ride_id="+str(ride_Id)}
	deets = read(ride_deets_q)

	#rideId doesn't exist
	if(deets ==0):
		print("Ride Id doesnt exist")
		abort(400) #double check

	#First check if specified user exists or not
	read_req = {"table": "users", "where" :"username='"+username+"'"}
	if(read(read_req)==0):
		print("Can't add user because he doesnt exist")
		abort(400)

	users = deets[0][5]
	created_by = deets[0][1]
	timestamp = deets[0][2]
	src = deets[0][3]
	dst = deets[0][4]
	if(username in users.split(',')):
		print("Same user can't join ride twice")
		abort(400)


	#finally do the honours
	users = users + username
	try:
		#first delete ride
		del_ride = "DELETE FROM rides WHERE ride_id = %s"
		connection = make_connection()
		cursor = connection.cursor()
		cursor.execute(del_ride, (ride_Id,))
		connection.commit()
		cursor.close()
		connection.close()
		#insert row again with new appended user
		insert_ride = {"insert": [ride_Id, created_by, timestamp, src, dst, users], "table": "rides"}
		insert(insert_ride)
		return '',204
	except (Exception, psycopg2.Error) as error:
		print("Error in Delete operation", error)
		abort(405) #not sure about this

@app.route('/api/v1/rides/<rideId>',methods=["DELETE"])
def delete_ride(rideId):
	ride_Id = int(rideId)
	ride_deets_q = {"table": "rides", "where":"rides.ride_id="+str(ride_Id)}
	deets = read(ride_deets_q)

	#rideId doesn't exist
	if(deets ==0):
		print("Ride Id doesnt exist")
		abort(400) #double check

	try:
		#first delete ride
		del_ride1 = "DELETE FROM rides WHERE ride_id = %s"
		del_ride2 = "DELETE FROM user_ride WHERE ride_id = %s"
		connection = make_connection()
		cursor = connection.cursor()
		cursor.execute(del_ride1, (ride_Id,))
		cursor.execute(del_ride2, (ride_Id,))
		connection.commit()

		cursor.close()
		connection.close()
		return '',200
		
	except (Exception, psycopg2.Error) as error:
		print("Error in Delete operation", error)
		abort(405) #not sure about this

@app.route("/api/v1/db/write", methods=["POST"])
def insert(req):
	table= req["table"]
	connection = make_connection()
	cursor = connection.cursor()
	try:
		if(table == "users"):
			username = req["insert"][0]
			pwd = req["insert"][1]
			print(username,pwd)
			insert_user = "INSERT INTO users (username, password) VALUES (%s,%s)"
			record = (username, pwd)
			cursor.execute(insert_user, record)
			connection.commit()

			#Logging message
			count = cursor.rowcount
			print (count, "Record inserted successfully into users table")

		elif(table == "user_ride"):
			print("HERE")
			username = req["insert"][0]
			ride_id = int(req["insert"][1])
			insert_user_ride = "INSERT INTO user_ride (created_by, ride_id) VALUES (%s,%s)"
			record = (username, ride_id)
			cursor.execute(insert_user_ride, record)
			connection.commit()

			#Logging message
			count = cursor.rowcount
			print (count, "Record inserted successfully into user_ride table")

		elif(table == "rides"):
			#for table rides
			ride_id = req["insert"][0]
			created_by = req["insert"][1]
			ts = req["insert"][2]
			src = int(req["insert"][3])
			dst = int(req["insert"][4])
			other_user = req["insert"][5]

			print(ride_id,created_by, ts, src, dst, other_user)
			check_ride_req= {"table": "rides", "where" :"ride_id='"+str(ride_id)+"'"}
			resp = read(check_ride_req)
			print("Resp: ", resp)
			if(resp == 0):
				insert_ride = "INSERT INTO rides (ride_id, created_by, timestamp, source, dest, other_users) VALUES (%s,%s,%s,%s,%s,%s)"
				record = (ride_id, created_by, ts, src, dst, other_user+',')
				cursor.execute(insert_ride, record)
				connection.commit()
			else:
				others = resp[0][5]
				others = others + other_user +','
				insert_ride = "INSERT INTO rides (ride_id, created_by, timestamp, source, dest, other_users) VALUES (%s,%s,%s,%s,%s,%s)"
				record = (ride_id, created_by, ts, src, dst, others)
		else:
			abort(405)

	except(Exception, psycopg2.Error) as error:
		if(connection):
			print("Failed to insert record", error)
			abort(405)
	finally:
		if(connection and cursor):
			cursor.close()
			connection.close()	



@app.route("/api/v1/db/read", methods=["POST"])
def read(req):
	connection = make_connection()
	print(type(connection))
	cursor = connection.cursor()
	try:
		table= req["table"]
		ret = -1

		
		where = req["where"]
		q = "SELECT * FROM "+ table+" WHERE " + where
		cursor.execute(q)
		rec = cursor.fetchall()
		cursor.close()
		connection.close()
		print("table = ", table,"Rec: ",rec)
		if(len(rec)==0):
			print("Record Doesn't exist")
			return 0
		else:
			return rec

	except(Exception, psycopg2.Error) as error:
		if(connection):
			print("Failed to read record", error)
			abort(405)
	finally:
		if(connection and cursor):
			cursor.close()
			connection.close()

if __name__ == '__main__':
	app.debug=True
	app.run()

