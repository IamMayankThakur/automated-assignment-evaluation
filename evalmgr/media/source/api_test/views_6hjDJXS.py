from flask import Flask, render_template,\
jsonify, request, abort,Response
import requests
import json
import datetime
import re
import datetime 


from flask_mysqldb import MySQL

app = Flask(__name__)


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'admin4321'
app.config['MYSQL_DB'] = 'ride'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

"""
API 1 add  user PUT
http://localhost:80/api/v1/users

{

 "username":"nishi",
 "password":"hi"
}

API 2
remove user 

http://localhost:80/api/v1/users/<nishi>


API 3
add ride post

http://localhost:80/api/v1/rides

{
	"created_by":"nishi",
	"timestamp":"23-12-1999:10-14-10",
	"source":"{10}",
	"destination":"{11}"
}



{

 "created_by":"nishi",
 "timestamp":"11-11-2020:11-11-11",
 "source":"{1}",
 "destination":"{2}"
}

API  4 GET
 http://localhost:80/api/v1/rides?source=10&destination=11

API 5 GET  given rideID


http://localhost:80/api/v1/rides/1


API 6 JOIN RIDE POST
http://localhost:80/api/v1/rides/<ride_query_ID>


{
"username":"nishi"
}

API 7  delete

http://localhost:80/api/v1/rides/<ride_query_ID>

"""
mysql = MySQL(app)
ride_id_global=1


@app.route('/test', methods = ["GET"])
def ababab():
	return "shit"

def is_sha1(maybe_sha):
    if len(maybe_sha) != 40:
        return False
    try:
        sha_int = int(maybe_sha, 16)
    except ValueError:
        return False
    return True

# API 1 add user
@app.route('/api/v1/users', methods = ["PUT"])

def add_user():
	user = request.get_json()
	username = user["username"]
	pwd = user["password"]
	data={}	
	if(is_sha1(pwd)==False):
		response = Response(response=json.dumps(dict(error='Password not in format')),status=400, mimetype='application/json')
		return response
	data["flag"]="1"
	data["username"]=username
	data["pwd"]=pwd
	data["columns"]=["username","pwd"]
	data["values"]=[username,pwd]
	r = requests.put('http://localhost:80/api/v1/db/write', json=data)
	if(r.text=="0"):
		response = Response(response=json.dumps(dict(error='User already exists')),status=400, mimetype='application/json')
		return response

	response = Response(response=json.dumps(dict({})),status=201, mimetype='application/json')
	return response

# API 2 delete user
@app.route('/api/v1/users/<username>', methods = ["DELETE"])
def delete_user(username):
	data={}
	#return username
	data["flag"]="2"
	data["username"]=username
	r = requests.delete('http://localhost:80/api/v1/db/write', json=data)
	if(r.text=="0"):
		response = Response(response=json.dumps(dict(error='User doesnot exist')),status=404, mimetype='application/json')
		return response

	if(r.text=="1"):
		response = Response(response=json.dumps(dict(error='User cannot be deleted,he is associated with rides')),status=404, mimetype='application/json')
		return response

	response = Response(response=json.dumps(dict({})),status=200, mimetype='application/json')
	return response

# API 3 create new ride
@app.route('/api/v1/rides',methods=["POST"])

def create_new_ride():
	ride = request.get_json()
	ride["flag"]="3"
	r = requests.post('http://localhost:80/api/v1/db/write', json=ride)
	#return r.text
	if(r.text=="0"):
		response = Response(response=json.dumps(dict(error='Not valid source or destination')),status=400, mimetype='application/json')
		return response
	

	if(r.text=="1"):
		response = Response(response=json.dumps(dict(error='User does not exist')),status=400, mimetype='application/json')
		return response
	if(r.text=="2"):
		response = Response(response=json.dumps(dict({})),status=201, mimetype='application/json')
		return response
	
	if(r.text=="3"):
		response = Response(response=json.dumps(dict(error='Ride already exists')),status=400, mimetype='application/json')
		return response
					
	

#API 4  GET
@app.route('/api/v1/rides', methods = ["GET"])
def rides():
	
	args = request.args
	args = dict(args)
	query = {}
	cur_time=str(datetime.datetime.now())
	a=cur_time.split(" ")
	b=a[1].split(":")
	c=b[2].split(".")
	act_time=a[0]+" "+b[0]+":"+b[1]+":"+c[0]
	act_time=str(act_time)
	query["flag"]="4"
	query["source"]=args["source"]
	query["destination"]=args["destination"]
	query["time"]=act_time	
	r = requests.post('http://localhost:80/api/v1/db/read',json=query)
	#return "hjj"	
	if(r.text=="0"):
		response = Response(response=json.dumps(dict(error='Ride doesnt exist')),status=400, mimetype='application/json')
		return response
	return r.text

#API 5 GET

@app.route('/api/v1/rides/<ride_id>', methods = ["GET"])
def ride_details(ride_id):
	query = {}
	query["flag"] = "5"
	query["ride"]= ride_id.strip("<").strip(">")
	r=requests.post("http://localhost:80/api/v1/db/read",json=query)
	if(r.text=="0"):
		response = Response(response=json.dumps(dict(error='Ride doesnt exist')),status=400, mimetype='application/json')
		return response
	return r.text





# API 6 join a ride
@app.route('/api/v1/rides/<ride_query_ID>',methods=["POST"])
def join_ride(ride_query_ID):
	data=request.get_json()
	data["flag"]="6"
	data["ride_query"]=ride_query_ID.strip("<").strip(">")
	r = requests.post('http://localhost:80/api/v1/db/write', json=data)
	#return r.text
	if(r.text=="0"):
		response = Response(response=json.dumps(dict(error='Ride Not found')),status=400, mimetype='application/json')
		return response
	if(r.text=="1"):
		response = Response(response=json.dumps(dict(error='User not found')),status=400, mimetype='application/json')
		return response
	if(r.text=="2"):
		response = Response(response=json.dumps(dict(error='User already in given ride')),status=400, mimetype='application/json')
		return response

	response = Response(response=json.dumps(dict({})),status=201, mimetype='application/json')
	return response

#API 7 delete
@app.route('/api/v1/rides/<ride_ID>', methods = ["Delete"])
def delete_ride(ride_ID):
	data={}
	data["flag"]="7"
	data["id"]=ride_ID.strip(">").strip("<")
	r = requests.delete('http://localhost:80/api/v1/db/write', json=data)
	if(r.text=="0"):
		response = Response(response=json.dumps(dict(error='Ride not found')),status=400, mimetype='application/json')
		return response
	response = Response(response=json.dumps(dict({})),status=200, mimetype='application/json')
	return response	
	

# API 8 write db
@app.route('/api/v1/db/write',methods=["PUT","DELETE","POST"])
def write_db():
	catch=request.get_json()
	#return catch["flag"]#"something"
	if(catch["flag"]=="1"):
		cur = mysql.connection.cursor()
		rows_count=cur.execute("select * from User_table where username =%s",(catch["username"],))
		#return jsonify(rows_count)
		if(rows_count==1):
			return "0"	
		cur.execute("insert into User_table values(%s, %s)", (catch["username"], catch["pwd"]))
		mysql.connection.commit()
		cur.close()
		
		return "1"


	if(catch["flag"]=="2"):
		cur = mysql.connection.cursor()
		user=catch["username"].strip("<")                                     
		user=user.strip(">")
		rows_count=cur.execute("select * from User_table where username =(%s)",(user,))
		#return jsonify(rows_count)
		if(rows_count<1):
			return "0"
		rows_count1=cur.execute("select * from Ride_table where creator =(%s)",(user,))	
		#return jsonify(rows_count1)		
		if(rows_count1>=1):
			return "1"

		cur.execute("delete from User_table where username = %s", (user,))
		mysql.connection.commit()
		cur.close()
		return "2"


	if(catch["flag"]=="3"):


		cur = mysql.connection.cursor()
		creator=catch["created_by"]
		timestamp=catch["timestamp"]
		destination=int(catch["destination"].strip("{").strip("}"))	
		source=int(catch["source"].strip("{").strip("}"))
		#return jsonify(destination)
		if(int(source) < 1 or int(destination) > 198 or int(source) > 198 or int(destination) < 1):
			return "0"
		
			
		
		
		rows_count=cur.execute("select * from User_table where username =(%s)",(creator,))
				
		if(rows_count<1):
			return "1"
			#abort(400,'{"message":"USER DOES NOT EXIST"}')
		
		
		#timestamp coversion
		b=timestamp.split(":")
		c=b[0].split("-")
		d=b[1].split("-")
		time=c[2]+"-"+c[1]+"-"+c[0]+" "+d[2]+":"+d[1]+":"+d[0]
		
		
		global ride_id_global
		
		rows_count=cur.execute("select * from Ride_table where source =%s AND destination=%s AND creator=%s AND create_time=%s ",(str(source),str(destination),creator,time))
		
		#return jsonify(rows_count)
		if(rows_count>0):
			return "3"
			#abort(400,'{"message":"RIDE already exists"}')
		
		ride_id_global=ride_id_global+1
		

		hell=cur.execute("insert into Ride_table values(%s,%s,%s,%s,%s)",(ride_id_global,source,destination,creator,time))

		mysql.connection.commit()

		cur.close()

				
		return "2" 



	if(catch["flag"]=="6"):
		cur = mysql.connection.cursor()
		username = catch["username"]
		ride=catch["ride_query"]
		ride=ride.strip("<")
		ride=ride.strip(">")
		#return jsonify(str(ride))		
		row_c=row_c=cur.execute("select * from Ride_table where ride_id =%s",(str(ride),))
		
		
		if(row_c<1):
			return "here"	
			return "0"
			#abort(400,'{"message :Ride Not found"}')
				
		no_rows=cur.execute("select * from User_table where username =%s",(str(username),))
		if(no_rows<1):
			return "1"#abort(400,'{"message :User not found found"}')
		
		no_count=cur.execute("select * from Riders_table where ride_id =%s AND rider =%s",(ride,str(username)))
		#return "asdad"
		#return jsonify(no_count)
		if(no_count>0):
			return "2"#abort(400,'{"message":"RIDER ALREADY IN GIVEN RIDE"}')
		
		hell=cur.execute("insert into Riders_table values(%s,%s)",(ride,str(username)))
		mysql.connection.commit()
		return "3" #200 OK success"

	if(catch["flag"]=="7"):
		cur = mysql.connection.cursor()
		rideid=catch["id"].strip("<")
		rideid=rideid.strip(">")
		rows_count=cur.execute("select * from Ride_table where ride_id =(%s)",(rideid,))
		if(rows_count<1):
			return "0"
			#abort(400,'{"message":"Ride DOES NOT EXIST"}')	
		cur.execute("delete from Ride_table where ride_id = %s", (rideid,))
		mysql.connection.commit()
		cur1 = mysql.connection.cursor()
		cur1.execute("delete from Riders_table where ride_id = %s", (rideid,))
		mysql.connection.commit()
		return "1"#"200 OK success"
		
		
		




#API 9  Read from DB
@app.route('/api/v1/db/read', methods = ["POST"])
def db_read():
	
	query = request.get_json()
	if(query["flag"]=="4"):

		cur = mysql.connection.cursor()
		cur_time = datetime.datetime.strptime(str(query["time"]),"%Y-%m-%d %H:%M:%S")
		
		hell=cur.execute("select ride_id as rideId,creator as username,create_time as timestamp from Ride_table where source=%s AND destination=%s AND create_time>%s",(query["source"],query["destination"],cur_time))# AND create_time>%s ,query["time"]
		if(hell==0):
			return "0"		
		data = cur.fetchall()
		
		for i in range(hell):
			a = str(data[i]["timestamp"])
			date, time = a.split(' ')
			date = date.split('-')[::-1]
			date = date[0] + '-' + date[1] + '-' + date[2]
			time = time.split(':')[::-1]
			time = time[0] + '-' + time[1] + '-' + time[2]
			timestamp = date + ':' + time
			data[i]["timestamp"] = timestamp
			data[i]["rideId"] = int(data[i]["rideId"])
		
		cur.close()
		return jsonify(data)
		
		
		
	if(query["flag"]=="5"):
		cur = mysql.connection.cursor()
		ride=query["ride"]
		
		ride1=cur.execute("select ride_id as rideId,creator as username,create_time as timestamp from Ride_table where ride_id=%s ",(ride,))
		data1=cur.fetchall()
		cur.close()
		cur1 = mysql.connection.cursor()
		ride2=cur1.execute("select ride_id as rideId, rider as username from Riders_table where ride_id =%s", (ride, ))
		data2 = cur1.fetchall()
		
		dicts = data1 + data2
		super_dict = {}
		for k in set(k for d in dicts for k in d):
			super_dict[k] = list(set([d[k] for d in dicts if k in d]))
		if(super_dict=={}):
			return "0"
		if(len(super_dict["rideId"]) == 1):
			super_dict["rideId"]  = int(super_dict["rideId"][0])
			
		if(len(super_dict["timestamp"]) == 1):
			super_dict["timestamp"] = super_dict["timestamp"][0]
			a = str(super_dict["timestamp"])
			date, time = a.split(' ')
			date = date.split('-')[::-1]
			date = date[0] + '-' + date[1] + '-' + date[2]
			time = time.split(':')[::-1]
			time = time[0] + '-' + time[1] + '-' + time[2]
			timestamp = date + ':' + time
			super_dict["timestamp"] = timestamp
			super_dict["rideId"]  = int(super_dict["rideId"])

		return jsonify(super_dict)
		

def convert_date(date):
	date = str(date)
	return date
	date_dic = {'Jan':'1', 'Feb':'2', 'Mar':'3', 'Apr':'4', 'May':'5', 'Jun':'6', 'Jul':'7', 'Aug':'8', 'Sept':'9', 'Oct':'10', 'Nov':'11', 'Dec':'12'}
	components = date.split(' ')
	changed_date = components[1] + '-' + date_dic[components[2]] + '-' + components[3] + ' ' + components[4]
	return changed_date



if __name__ == '__main__':
	app.run()

