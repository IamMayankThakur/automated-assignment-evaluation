from flask import Flask, render_template,\
jsonify,request,abort
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String,ForeignKey ,DateTime
from sqlalchemy.orm import sessionmaker,scoped_session
import requests
from flask import Response
import json
import re
from datetime import datetime
 
app=Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SQLALCHEMY_DATAdb.Model_URI'] = 'sqlite:///:c:' 
db = SQLAlchemy(app)
Session = scoped_session(sessionmaker(bind=db))
enum = {1: 'Kempegowda Ward', 2: 'Chowdeswari Ward', 3: 'Atturu', 4: 'Yelahanka Satellite Town', 5: 'Jakkuru', 
        6: 'Thanisandra', 7: 'Byatarayanapura', 8: 'Kodigehalli', 9: 'Vidyaranyapura', 10: 'Dodda Bommasandra', 
       11: 'Kuvempu Nagar', 12: 'Shettihalli', 13: 'Mallasandra', 14: 'Bagalakunte', 15: 'T Dasarahalli',
       16: 'Jalahalli', 17: 'J P Park', 18: 'Radhakrishna Temple Ward', 19: 'SanJayanagar', 20: 'Ganga Nagar',
       21: 'Hebbala', 22: 'Vishwanath Nagenahalli', 23: 'Nagavara', 24: 'HBR Layout', 25: 'Horamavu', 
       26: 'Ramamurthy Nagar', 27: 'Banasavadi', 28: 'Kammanahalli', 29: 'Kacharkanahalli', 30: 'Kadugondanahalli', 
       31: 'Kushal Nagar', 32: 'Kaval Bairasandra', 33: 'Manorayana Palya', 34: 'Gangenahalli', 35: 'Aramane Nagara', 
       36: 'Mattikere', 37: 'Yeshwanthpura', 38: 'HMT Ward', 39: 'Chokkasandra', 40: 'Dodda Bidarakallu',
       41: 'Peenya Industrial Area', 42: 'Lakshmi Devi Nagar', 43: 'Nandini Layout', 44: 'Marappana Palya', 45: 'Malleshwaram', 
       46: 'Jayachamarajendra Nagar', 47: 'Devara Jeevanahalli', 48: 'Muneshwara Nagar', 49: 'Lingarajapura', 50: 'Benniganahalli',
       51: 'Vijnanapura', 52: 'KR Puram', 53: 'Basavanapura', 54: 'Hudi', 55: 'Devasandra', 
       56: 'A Narayanapura', 57: 'C.V. Raman Nagar', 58: 'New Tippa Sandra', 59: 'Maruthi Seva Nagar', 60: 'Sagayara Puram', 
       61: 'SK Garden', 62: 'Ramaswamy Palya', 63: 'Jaya Mahal', 64: 'Raj Mahal Guttahalli', 65: 'Kadu Malleshwar Ward', 
       66: 'Subramanya Nagar', 67: 'Nagapura', 68: 'Mahalakshmipuram', 69: 'Laggere', 70: 'Rajagopal Nagar', 
       71: 'Hegganahalli', 72: 'Herohalli', 73: 'Kottegepalya', 74: 'Shakthi Ganapathi Nagar', 75: 'Shankar Matt', 
       76: 'Gayithri Nagar', 77: 'Dattatreya Temple Ward', 78: 'Pulakeshi Nagar', 79: 'Sarvagna Nagar', 80: 'Hoysala Nagar', 
       81: 'Vijnana Nagar', 82: 'Garudachar palya', 83: 'Kadugodi', 84: 'Hagadur', 85: 'Dodda Nekkundi', 
       86: 'Marathahalli', 87: 'HAL Airport', 88: 'Jeevanbhima Nagar', 89: 'Jogupalya', 90: 'Halsoor', 
       91: 'Bharathi Nagar', 92: 'Shivaji Nagar', 93: 'Vasanth Nagar', 94: 'Gandhi Nagar', 95: 'Subhash Nagar', 
       96: 'Okalipuram', 97: 'Dayananda Nagar', 98: 'Prakash Nagar', 99: 'Rajaji Nagar', 100: 'Basaveshwara Nagar', 
       101: 'Kamakshipalya', 102: 'Vrisahbhavathi Nagar', 103: 'Kaveripura', 104: 'Govindaraja Nagar', 105: 'Agrahara Dasarahalli', 
       106: 'Dr.Raj Kumar Ward', 107: 'Shiva Nagar', 108: 'Sri Rama Mandir Ward', 109: 'Chickpete', 110: 'Sampangiram Nagar', 
       111: 'Shantala Nagar', 112: 'Domlur', 113: 'Konena Agrahara', 114: 'Agaram', 115: 'Vannar Pet', 
       116: 'Nilasandra', 117: 'Shanthi Nagar', 118: 'Sudham Nagar', 119: 'Dharmaraya Swamy Temple', 120: 'Cottonpete', 
       121: 'Binni Pete', 122: 'Kempapura Agrahara', 123: 'ViJayanagar', 124: 'Hosahalli', 125: 'Marenahalli', 
       126: 'Maruthi Mandir Ward', 127: 'Mudalapalya', 128: 'Nagarabhavi', 129: 'Jnana Bharathi Ward', 130: 'Ullalu', 
       131: 'Nayandahalli', 132: 'Attiguppe', 133: 'Hampi Nagar', 134: 'Bapuji Nagar', 135: 'Padarayanapura', 
       136: 'Jagajivanaram Nagar', 137: 'Rayapuram', 138: 'Chelavadi Palya', 139: 'KR Market', 140: 'Chamraja Pet', 
       141: 'Azad Nagar', 142: 'Sunkenahalli', 143: 'Vishveshwara Puram', 144: 'Siddapura', 145: 'Hombegowda Nagar', 
       146: 'Lakkasandra', 147: 'Adugodi', 148: 'Ejipura', 149: 'Varthur', 150: 'Bellanduru', 
       151: 'Koramangala', 152: 'Suddagunte Palya', 153: 'Jayanagar', 154: 'Basavanagudi', 155: 'Hanumanth Nagar', 
       156: 'Sri Nagar', 157: 'Gali Anjenaya Temple Ward', 158: 'Deepanjali Nagar', 159: 'Kengeri', 160: 'Raja Rajeshawari Nagar', 
       161: 'Hosakerehalli', 162: 'Giri Nagar', 163: 'Katriguppe', 164: 'Vidya Peeta Ward', 165: 'Ganesh Mandir Ward', 
       166: 'Kari Sandra', 167: 'Yediyur', 168: 'Pattabhi Ram Nagar', 169: 'Byra Sandra', 170: 'Jayanagar East', 
       171: 'Gurappana Palya', 172: 'Madivala', 173: 'Jakka Sandra', 174: 'HSR Layout', 175: 'Bommanahalli', 
       176: 'BTM Layout', 177: 'JP Nagar', 178: 'Sarakki', 179: 'Shakambari Narar', 180: 'Banashankari Temple Ward', 
       181: 'Kumara Swamy Layout', 182: 'Padmanabha Nagar', 183: 'Chikkala Sandra', 184: 'Uttarahalli', 185: 'Yelchenahalli', 
       186: 'Jaraganahalli', 187: 'Puttenahalli', 188: 'Bilekhalli', 189: 'Honga Sandra', 190: 'Mangammana Palya', 
       191: 'Singa Sandra', 192: 'Begur', 193: 'Arakere', 194: 'Gottigere', 195: 'Konankunte', 
       196: 'Anjanapura', 197: 'Vasanthpura', 198: 'Hemmigepura'}


class Username(db.Model):
    __tablename__ = 'users'

    name = Column(String, primary_key=True)
    password = Column(String(40))

    def __init__(self,name,password):
    	self.password = password
    	self.name = name
class Ride(db.Model):
    __tablename__ = 'ride'

    id = Column(Integer, primary_key =  True)
    created_by = Column(String)
    timestamp = Column(String)
    source = Column(Integer)
    destination = Column(Integer)
    

    def __init__(self,created_by,timestamp,source,destination):
    	
    	self.created_by = created_by
    	self.timestamp = timestamp
    	self.source = source
    	self.destination = destination

class Riders(db.Model):
    __tablename__ = 'riders'
    id = Column(Integer, primary_key =  True)
    rideid = Column(Integer)
    name =Column(String)
    def __init__(self,rideid,name):
    	self.rideid = rideid
    	self.name =name

    

@app.route("/api/v1/users",methods=["PUT"])
def adduser():
	
	name=request.get_json()["username"]
	password=request.get_json()["password"]
	read_request = { "flag" : "1",
					"name" : name
					}
	
	pattern = re.compile(r'\b[0-9a-f]{40}\b')
	if(re.match(pattern,password) == None):
		return Response("password not in sha1", status=400, mimetype='application/json')
	r = requests.post(url = "http://127.0.0.1:80/api/v1/db/read",json = read_request )
	if(r.text == "None"):
		write_request = { "flag" : "1",
					"name" : name,
					"password": password
					}
		r = requests.post(url = "http://127.0.0.1:80/api/v1/db/write",json = write_request )
		if r.text == "success":
			return jsonify("Username added successfully"),201
		else:
			return jsonify("{400:failed}"),400
	else:
		return jsonify("Username already exist"),400
	
	
@app.route("/api/v1/users/<username>",methods=["DELETE"])
def delete_user(username):
	read_request = { "flag" : "1",
					"name" : username
					}
	r = requests.post(url = "http://127.0.0.1:80/api/v1/db/read",json = read_request )
	if(r.text != "None"):
		write_request =  {
					"flag" : "4",
		             "name": username
		}
		r = requests.delete(url = "http://127.0.0.1:80/api/v1/db/write",json = write_request )
		if r.text == "success":
			return jsonify("deleted"),200
		else:
			return jsonify(""),400
	else:
			return jsonify("Username doesn't exist"),400
	
@app.route("/api/v1/rides",methods=["POST"])
def create_ride():
	created_by = request.get_json()["created_by"]
	timestamp = request.get_json()["timestamp"]
	source = int(request.get_json()["source"])
	destination =int(request.get_json()["destination"])
	if source == destination:
		return jsonify("Source and Destination are same"),400
	if source not in enum.keys():
		return jsonify("Source doesn't exist"),400
	if destination not in enum.keys():
		return jsonify("Destination doesn't exist"),400
	pattern = re.compile(r'\d\d-\d\d-\d\d\d\d:\d\d-\d\d-\d\d')
	if(re.match(pattern,timestamp) == None):
		return Response("Timestamp format not correct", status=400, mimetype='application/json')
	read_request = { "flag" : "1",
					"name" : created_by
					}

	r = requests.post(url = "http://127.0.0.1:80/api/v1/db/read",json = read_request )
	if(r.text != "None"):
		write_request = {	
				"flag" : "2",	
				"created_by" : created_by,
				"timestamp": timestamp,
				"source": source,
				"destination": destination
				}
		r = requests.post(url = "http://127.0.0.1:80/api/v1/db/write",json = write_request )
		if r.text == "success":
			return jsonify("Ride Created"),201
		else:
			return jsonify("{400:failed}"),400
		
	else:
		return Response("Username doesn't exist", status=400, mimetype='application/json')

@app.route("/api/v1/rides",methods = ["GET"])
def get_ride_id1():
	source = int(request.args.get("source"))
	destination = int(request.args.get("destination"))
	read_request = { "flag" : "2",
					"source" : source,
					"destination" : destination
					}

	r = requests.post(url = "http://127.0.0.1:80/api/v1/db/read",json = read_request )
	if r.text == "204":
		return jsonify(""),204
	else:
		res = json.loads(r.text)
		return jsonify(res),200
	 

	
@app.route("/api/v1/rides/<rideId>",methods=["GET"])
def get_rideDetails(rideId):
	read_request = { "flag" : "3",
					"rideid": rideId
	}
	r = requests.post(url = "http://127.0.0.1:80/api/v1/db/read",json = read_request )
	if r.text == "204":
		return jsonify(""),204
	else:
		res = json.loads(r.text)
		return jsonify(res),200

@app.route("/api/v1/rides/<rideId>",methods=["POST"])
def join_ride(rideId):
	username = request.get_json()["username"]
	read_request = { "flag" : "4",
					"name" : username,
					"rideid": rideId
	}
	r = requests.post(url = "http://127.0.0.1:80/api/v1/db/read",json = read_request )

	
	if(int(r.text) ==0 ):
		return jsonify("User Created the ride"),400
	elif(int(r.text) ==1 ):
		return jsonify("User has already joined the ride"),400
	elif(int(r.text) ==2 ):
		return jsonify("Username doesn't exist"),400
	elif(int(r.text) ==3 ):
		return jsonify("RideId doesn't exist"),400
	if(int(r.text) ==5 ):
		write_request = { "flag" : "3",
					"name" : username,
					"rideid": rideId
						}
		r = requests.post(url = "http://127.0.0.1:80/api/v1/db/write",json = write_request )
		
		if r.text== "success":
			return jsonify("Joined successfully"),201
		else:
			return jsonify("{2:fail}"),400	

	
		
@app.route("/api/v1/rides/<rideId>",methods=["DELETE"])
def delete_ride(rideId):
	read_request = { "flag" : "5",
					"rideid": rideId
	}
	r = requests.post(url = "http://127.0.0.1:80/api/v1/db/read",json = read_request )
	if r.text == "None":
		return Response("RideId doesn't exist", status=400, mimetype='application/json')
	else:
		write_request = { "flag" : "5",
					"rideid": rideId
					}
		r = requests.post(url = "http://127.0.0.1:80/api/v1/db/write",json = write_request )
		if r.text == "success":
			return Response("RideId Deleted", status=200, mimetype='application/json')
		
		



def compare_time(t1,t2):
	l1 = t1.split(" ")
	l2 = t2.split(":")
	date1 = l1[0].split("-")
	date2 = l2[0].split("-")
	time1 = l1[1].split(":")
	time2 = l2[1].split("-")
	d1,m1,y1 = int(date1[2]) ,int(date1[1]) ,int(date1[0])
	d2,m2,y2 = int(date2[0]) ,int(date2[1]) ,int(date2[2])
	s1,min1,h1 = int(time1[2][:2]) ,int(time1[1]) ,int(time1[0])
	s2,min2,h2 = int(time2[0]) ,int(time2[1]) ,int(time2[2])
	#print("1 ",y1,m1,d1,h1,min1,s1)
	#print("2 ",y2,m2,d2,h2,min2,s2)
	if(y1>y2):
		return 0
	elif y2>y1:
		return 1
	if(m1>m2):
		return 0
	elif m2>m1:
		return 1
	if(d1>d2):
		return 0
	elif d2>d1:
		return 1
	if(h1>h2):
		return 0
	elif h2>h1:
		return 1
	if(min1>min2):
		return 0
	elif min2>min1:
		return 1
	if(s1>s2):
		return 0

	return 1
		

@app.route("/api/v1/db/read",methods=["POST"])
def readdb():
	flag = request.get_json()["flag"]
	if int(flag) == 1:
		name = request.get_json()["name"]
		res = Username.query.filter_by(name  = name ).first()
		if res == None:
			return "None"
		else:
			return name
	if int(flag) == 2:
		source = int(request.get_json()["source"])
		destination = int(request.get_json()["destination"])
		f = 0
		res = Ride.query.filter_by(source = source).filter_by(destination = destination)
		if(res == None):
			return jsonify("{}"),204
		for i in res:

			c = compare_time(str(datetime.now()),i.timestamp)
			
			if(c == 1):
				
				f = 1
				r1 = {}
				r1["rideId"] = i.id
				r1["username"] = i.created_by
				r1["timestamp"] = i.timestamp
				return jsonify(r1),201
			else:
				
				continue

		if f == 0:
			return "204"
	if int(flag) == 3:
		rideId = request.get_json()["rideid"]
		res = Ride.query.filter_by(id = int(rideId)).first()
		if res == None:
			return "204"
		res1 = Riders.query.filter_by(rideid = int(rideId)).all()
		r1 = {}
		r1["rideId"] = rideId
		r1["users"] = []
		for i in res1:
			r1["users"].append(i.name)
		r1["Created_by"] = res.created_by
		r1["Timestamp"] = res.timestamp
		r1["source"] = res.source
		r1["destination"] = res.destination
		return Response(json.dumps(r1), status=201, mimetype='application/json')
		
		
	if int(flag) == 4:
		username = request.get_json()["name"]
		rideId = request.get_json()["rideid"]
		if(Username.query.filter_by(name = username).first() == None):
			return "2" 
		if Ride.query.filter_by(id = int(rideId)).first() == None:
			return "3"
		if(bool(Riders.query.filter_by(name = username).filter_by(rideid = rideId).first()) ): 
				return "1"

		if(bool(Ride.query.filter_by(id = rideId).filter_by(created_by = username).first())):
				return "0"
		else:
			return "5"
			
	if(int(flag) == 5):
		rideId = request.get_json()["rideid"]
		res = Ride.query.filter_by(id = int(rideId)).first()
		if res == None:
			return "None"
		else:
			return str(rideId)




@app.route("/api/v1/db/write",methods=["POST","DELETE"])
def writedb():
	flag = request.get_json()["flag"]
	if int(flag) == 1:
		name = request.get_json()["name"]
		password=request.get_json()["password"]
		u = Username(name,password)
		db.session.add(u)
		db.session.commit()
		return "success"
	if int(flag) == 2:
		created_by = request.get_json()["created_by"]
		timestamp = request.get_json()["timestamp"]
		source = int(request.get_json()["source"])
		destination =int(request.get_json()["destination"])
		r =Ride(created_by,timestamp,source,destination)
		db.session.add(r)
		db.session.commit()
		return "success"
	if int(flag) == 3:
		name = request.get_json()["name"]
		rideid = request.get_json()["rideid"]
		u = Riders(int(rideid),name)
		db.session.add(u)
		db.session.commit()
		res= Riders.query.filter_by(name = name).first()

		return "success"
	if int(flag) == 4:
		username = request.get_json()["name"]
		Username.query.filter_by(name = username).delete()
		Riders.query.filter_by(name = username).delete()
		db.session.commit()
		return "success"
	if int(flag) == 5:
		rideId = request.get_json()["rideid"]
		Ride.query.filter_by(id = int(rideId)).delete()
		Riders.query.filter_by(rideid = int(rideId)).delete()
		db.session.commit()
		return "success"

db.create_all()
app.debug=True