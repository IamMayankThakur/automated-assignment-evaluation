from flask import * 
from flask import request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *
from sqlalchemy import exc
from datetime import datetime
import requests

app = Flask(__name__) 
app.config['JSON_SORT_KEYS'] = False

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
 
db = SQLAlchemy(app)

class User(db.Model):
	__tablename__ = 'User'
	name = db.Column(db.String(50), primary_key = True)
	password = db.Column(db.String(40))

class Area(db.Model):
	__tablename__ = 'Area'
	areano = db.Column(db.Integer, primary_key = True)
	areaname = db.Column(db.String(50))

#db.create_all()

class Rides(db.Model):
	__tablename__ = 'Rides'
	rideid = db.Column(db.Integer, primary_key = True)
	created_by = db.Column(db.String(50), db.ForeignKey('User.name'))
	timestamp = db.Column(db.DateTime)
	source = db.Column(db.Integer, db.ForeignKey('Area.areano'))
	dest = db.Column(db.Integer, db.ForeignKey('Area.areano'))

class UserRides(db.Model):
	__tablename__ = 'UserRides'
	rideid = db.Column(db.Integer, db.ForeignKey('Rides.rideid'), primary_key = True)
	username = db.Column(db.String(50), db.ForeignKey('User.name'), primary_key = True)

db.create_all()

# f = open("AreaNameEnum.csv",'r')
# for i in f:
# 	x = i.split(',')
# 	a = int(x[0])
# 	b = x[1].strip()
# 	row = Area(areano=a,areaname=b)
# 	db.session.add(row)
# 	db.session.commit()
def is_hex(val):
	try:
		a = int(val,16)
		return 1
	except:
		return 0

def checkloc(source,dest):
	query1 = "SELECT COUNT(*) from Area where areano = '"+source+"'"
	mydata1 = {"query":query1}
	r1 = requests.post("http://127.0.0.1:5051/api/v1/db/read",json=mydata1)
	res1 = json.loads(r1.text)
	count1 = res1[0]["COUNT(*)"]
	query2 = "SELECT COUNT(*) from Area where areano = '"+dest+"'"
	mydata2 = {"query":query2}
	r2 = requests.post("http://127.0.0.1:5051/api/v1/db/read",json=mydata2)
	res2 = json.loads(r2.text)
	count2 = res2[0]["COUNT(*)"]
	if (count1 == 0 or count2 == 0):
		return 0
	else:
		return 1
### API 1 ###
@app.route("/api/v1/users",methods=["PUT"])
def add_user():
    usr = request.get_json()["username"]
    pas = request.get_json()["password"]
    if(len(pas)!=40 or (is_hex(pas) != 1)):
    	return Response("Password must be SHA1 hash hex only",status = 400,mimetype='application/text')
    else:
        mydata = {"table":"User","insert":[usr,pas]}
        r = requests.post("http://127.0.0.1:5051/api/v1/db/write",json=mydata)
        res = r.text
        if res=='201':
        	return Response("Added user successfully",status = 201,mimetype='application/text')
        elif res=='400':
        	return Response("Username taken already",status = 400,mimetype='application/text')
        elif res=='500':
        	return Response("Internal server errror",status = 500,mimetype='application/text')

### API 2 ###
@app.route("/api/v1/users/<username>",methods=["DELETE"])
def del_user(username):
	query = "SELECT COUNT(*) from User where name = '"+username+"'"
	mydata = {"query":query}
	r = requests.post("http://127.0.0.1:5051/api/v1/db/read",json=mydata)
	res = json.loads(r.text)
	count = res[0]["COUNT(*)"]
	if count==0:
		return Response("User does not exist",status = 400,mimetype='application/text')
	else:
		query2 = "SELECT COUNT(*) from Rides where created_by = '"+username+"'"
		mydata2 = {"query":query2}
		r2 = requests.post("http://127.0.0.1:5051/api/v1/db/read",json=mydata2)
		res2 = json.loads(r2.text)
		count = res2[0]["COUNT(*)"]
		if count!=0:
			return Response("This user cannot be deleted because he/she has created a ride",status = 400,mimetype='application/text')
		else:
			query = "DELETE from User where name = '"+username+"'"
			mydata = {"query":query}
			r = requests.post("http://127.0.0.1:5051/api/v1/db/read",json=mydata)
			res = r.text
			query3 = "DELETE from UserRides where username = '"+username+"'"
			mydata3 = {"query":query3}
			r3 = requests.post("http://127.0.0.1:5051/api/v1/db/read",json=mydata3)
			res3 = r3.text
			if res=="200" and res3=="200":
				return Response("User deleted successfully",status = 200,mimetype='application/text')
			else:
				return Response("Internal server error",status = 500,mimetype='application/text')

### API 3 ###
@app.route("/api/v1/rides",methods=["POST"])
def create_ride():
	create = request.get_json()["created_by"]
	time = request.get_json()["timestamp"]
	src = request.get_json()["source"]
	dst = request.get_json()["destination"]
	query2 = "SELECT COUNT(*) from User where name = '"+create+"'"
	mydata2 = {"query":query2}
	r2 = requests.post("http://127.0.0.1:5051/api/v1/db/read",json=mydata2)
	res2 = json.loads(r2.text) #[{}]
	count = res2[0]["COUNT(*)"]
	if count==0:
		return Response("Given username does not exist",status = 400,mimetype='application/text')
	else:
		if(checkloc(src,dst)):
			mydata = {"table":"Rides","insert":[create,time,src,dst]}
			r = requests.post("http://127.0.0.1:5051/api/v1/db/write",json=mydata)
			res = r.text
			query = "SELECT rideid FROM Rides where created_by = '"+create+"'"
			qdata = {"query":query}
			q = requests.post("http://127.0.0.1:5051/api/v1/db/read",json=qdata)
			qt = q.text
	        #rideid = int(qt)
			json_data = json.loads(qt)
			for item in json_data:
				ride = item["rideid"]
			mydata1 = {"table":"UserRides","insert":[ride,create]}
			r1 = requests.post("http://127.0.0.1:5051/api/v1/db/write",json=mydata1)
			if r1.text == "201":
				return Response("Created ride successfully",status = 201,mimetype='application/text')
			else:
				return Response("Internal server error",status = 500,mimetype='application/text')
		else:
			return Response("Wrong source or destination code",status = 400,mimetype='application/text')

	

### API 4 ###
@app.route("/api/v1/rides",methods=["GET"])
def up_rides():
	d1 = datetime.now()
	s_d1 = str(d1)
	source = request.args.get("source")
	destination = request.args.get("destination")
	if(checkloc(source,destination)):
		query = "SELECT rideid,created_by,timestamp FROM Rides WHERE timestamp >= '"+s_d1+"' and source = '"+source+"' and dest = '"+destination+"'"
		mydata = {"query":query}
		r = requests.post("http://127.0.0.1:5051/api/v1/db/read",json=mydata)
		ch = r.text.replace("created_by","username")
		res = json.loads(ch)
		if len(res)==0:
			return Response("No rides found",status = 204,mimetype='application/text')
		else:
			for i in res:
				tm = i["timestamp"]
				newt = datetime.strptime(tm,"%Y-%m-%d %H:%M:%S.%f")
				convnewt = newt.strftime("%d-%m-%Y:%S-%M-%H")
				i["timestamp"] = convnewt
			return jsonify(res),200
	else:
		return Response("Wrong source or destination code",status = 400,mimetype='application/text')

### API 5 ###
@app.route("/api/v1/rides/<rideid>",methods=["GET"])
def ride_details(rideid):
	query = "SELECT created_by,source,dest,timestamp from Rides where rideid = '"+rideid+"'"
	mydata = {"query":query}
	r = requests.post("http://127.0.0.1:5051/api/v1/db/read",json=mydata)
	res = json.loads(r.text)
	if len(res)==0:
		return Response("Invalid Ride ID",status = 400,mimetype='application/text')
	else:
		query2 = "SELECT username from UserRides where rideid = '"+rideid+"'"
		mydata2 = {"query":query2}
		r2 = requests.post("http://127.0.0.1:5051/api/v1/db/read",json=mydata2)
		res2 = json.loads(r2.text)
		usrs = []
		for i in res2:
			name = i["username"]
			usrs.append(name)
		tm = res[0]["timestamp"]
		newt = datetime.strptime(tm,"%Y-%m-%d %H:%M:%S.%f")
		convnewt = newt.strftime("%d-%m-%Y:%S-%M-%H")
		returnjson = {"rideId":rideid,"created_by":res[0]["created_by"],"users":usrs,"timestamp":convnewt,"source":res[0]["source"],"destination":res[0]["dest"]}
		return jsonify(returnjson),200

### API 6 ###
@app.route("/api/v1/rides/<rideid>",methods=["POST"])
def addusrride(rideid):
	usn = request.get_json()["username"]
	query = "SELECT COUNT(*) from Rides where rideid = '"+rideid+"'"
	mydata = {"query":query}
	r = requests.post("http://127.0.0.1:5051/api/v1/db/read",json=mydata)
	res = json.loads(r.text)
	count = res[0]["COUNT(*)"]
	if count==0:
		return Response("Invalid rideId",status = 400,mimetype='application/text')
	else:
		query2 = "SELECT COUNT(*) from User where name = '"+usn+"'"
		mydata2 = {"query":query2}
		r2 = requests.post("http://127.0.0.1:5051/api/v1/db/read",json=mydata2)
		res2 = json.loads(r2.text)
		count = res2[0]["COUNT(*)"]
		if count==0:
			return Response("Username does not exist",status = 400,mimetype='application/text')
		else:
			mydata3 = {"table":"UserRides","insert":[rideid,usn]}
			r3 = requests.post("http://127.0.0.1:5051/api/v1/db/write",json=mydata3)
			res3 = r3.text
			if res3 == "201":
				return Response("Added user to ride",status = 200,mimetype='application/text')
			elif res3 == "400":
				return Response("User already added to the ride",status = 400,mimetype='application/text')
			elif res3 == "500":
				return Response("Internal server error",status = 500,mimetype='application/text')

##API 7 ##
@app.route("/api/v1/rides/<rideid>",methods=["DELETE"])
def del_ride(rideid):
	query3= "SELECT COUNT(*) from Rides where rideid = '"+rideid+"'"
	mydata3 = {"query":query3}
	r3= requests.post("http://127.0.0.1:5051/api/v1/db/read",json=mydata3)
	res3 = json.loads(r3.text)
	count = res3[0]["COUNT(*)"]
	if count==0:
		return Response("Ride dosen't exist",status = 400,mimetype='application/text')
	else:
		query = "DELETE from UserRides where rideid = '"+rideid+"'"
		mydata = {"query":query}
		r = requests.post("http://127.0.0.1:5051/api/v1/db/read",json=mydata)
		res = r.text
		query2 = "DELETE FROM Rides where rideid = '"+rideid+"'"
		mydata2 = {"query":query2}
		r2 = requests.post("http://127.0.0.1:5051/api/v1/db/read",json=mydata2)
		res2 = r2.text
		if res=="200" and res2=="200":
			return Response("Ride deleted successfully",status = 200,mimetype='application/text')
		else:
			return Response("Internal server error",status = 500,mimetype='application/text')


	
### API 8 ###
@app.route("/api/v1/db/write",methods=["POST"])
def write_db():
	tbl = request.get_json()["table"]
	data = request.get_json()["insert"]
	if (tbl == "User"):
		try:
			user = User(name=data[0], password=data[1])
			db.session.add(user)
			db.session.commit()
			return '201'
		except exc.IntegrityError as e:
			db.session().rollback()
			return '400'
		except:
			return '500'
	elif (tbl == "Rides"):
		frmt = "%d-%m-%Y:%S-%M-%H"
		date = datetime.strptime(data[1],frmt)	
		row = Rides(created_by=data[0],timestamp=date,source=int(data[2]),dest=int(data[3]))
		db.session.add(row)
		db.session.commit()
		return 'Added New Ride'
	elif (tbl == "UserRides"):
		try:
			row = UserRides(rideid=int(data[0]),username=data[1])
			db.session.add(row)
			db.session.commit()
			return '201'
		except exc.IntegrityError as e:
			db.session().rollback()
			return '400'
		except:
			return '500'

### API 9 ###
@app.route("/api/v1/db/read",methods=["POST"])
def read_db():
	query = request.get_json()["query"]
	res = {}
	engine = create_engine('sqlite:///test.db')
	connection = engine.connect()
	if "DELETE" in query:
		connection.execute(query)
		return "200"
	else:
		result = connection.execute(query)
		res = [dict(x) for x in result]
		return jsonify(res)



if __name__ == "__main__":
	app.run(port=5051)
