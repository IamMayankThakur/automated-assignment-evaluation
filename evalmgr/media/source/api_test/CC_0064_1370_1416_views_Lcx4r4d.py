from flask import Flask,render_template,request,jsonify,Response,make_response
import requests
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.sqlite import TIMESTAMP
import csv
import uuid
import sqlite3
import random,re
import datetime,time
#from data import Constants
from enum import Enum
class Constants(Enum):
	KempegowdaWard=1
	ChowdeshwariWard=2
	Atturu=3
	YelahankaSatelliteTown=4
	Jakkuru=5
	Thanisandra=6
	Byatarayanapura=7
	Kodigehalli=8
	Vidyaranyapura=9
	DoddaBommasandra=10
	KuvempuNagar=11
	Shettihalli=12
	Mallasandra=13
	Bagalakunte=14
	TDasarahalli=15
	Jalahalli=16
	JPPark=17
	RadhakrishnaTempleWard=18
	SanJayanagar=19
	GangaNagar=20
	Hebbala=21
	VishwanathNagenhalli=22
	Nagavara=23
	HBRLayout=24
	Horamavu=25
	RamamurthyNagar=26
	Banasavadi=27
	Kammanahalli=28
	Kacharkanahalli=29
	Kadugondanahalli=30
	KushalNagar=31
	KavalBairasandra=32
	ManorayanaPalya=33
	Gangenahalli=34
	AramaneNagara=35
	Mattikere=36
	Yeshwanthpura=37
	HMTWard=38
	Chokkasandra=39
	DoddaBidarakallu=40
	PeenyaIndustrialArea=41
	LakshmiDeviNagar=42
	NandiniLayout=43
	MarappanaPalya=44
	Malleshwaram=45
	JayachamarajendraNagar=46
	DevaraJeevanahalli=47
	MuneshwaraNagar=48
	Lingarajapura=49
	Benniganahalli=50
	Vijnanapura=51
	KRPuram=52
	Basavanapura=53
	Hudi=54
	Devasandra=55
	ANarayanapura=56
	CVRamanNagar=57
	NewTippaSandra=58
	MaruthiSevaNagar=59
	SagayaraPuram=60
	SKGarden=61
	RamaswamyPalya=62
	JayaMahal=63
	RajMahalGuttahalli=64
	KaduMalleshwarWard=65
	SubramanyaNagar=66
	Nagapura=67
	Mahalakshmipuram=68
	Laggere=69
	RajagopalNagar=70
	Hegganahalli=71
	Herohalli=72
	Kottegepalya=73
	ShakthiGanapathiNagar=74
	ShankarMatt=75
	GayithriNagar=76
	DattatreyaTempleWard=77
	PulakeshiNagar=78
	SarvagnaNagar=79
	HoysalaNagar=80
	VijnanaNagar=81
	GarudacharPalya=82
	Kadugodi=83
	Hagadur=84
	DoddaNekkundi=85
	Marathahalli=86
	HALAirport=87
	JeevanbhimaNagar=88
	Jogupalya=89
	Halsoor=90
	BharathiNagar=91
	ShivajiNagar=92
	VasanthNagar=93
	GandhiNagar=94
	SubhashNagar=95
	Okalipuram=96
	DayanandaNagar=97
	PrakashNagar=98
	RajajiNagar=99
	BasaveshwaraNagar=100
	Kamakshipalya=101
	VrisahbhavathiNagar=102
	Kaveripura=103
	GovindarajaNagar=104
	AgraharaDasarahalli=105
	DrRajKumarWard=106
	ShivaNagar=107
	SriRamaMandirWard=108
	Chickpete=109
	SampangiramNagar=110
	ShantalaNagar=111
	Domlur=112
	KonenaAgrahara=113
	Agaram=114
	VannarPet=115
	Nilasandra=116
	ShanthiNagar=117
	SudhamNagar=118
	DharmarayaSwamyTemple=119
	Cottonpete=120
	BinniPete=121
	KempapuraAgrahara=122
	ViJayanagar=123
	Hosahalli=124
	Marenahalli=125
	MaruthiMandirWard=126
	Mudalapalya=127
	Nagarabhavi=128
	JnanaBharathiWard=129
	Ullalu=130
	Nayandahalli=131
	Attiguppe=132
	HampiNagar=133
	BapujiNagar=134
	Padarayanapura=135
	JagajivanaramNagar=136
	Rayapuram=137
	ChelavadiPalya=138
	KRMarket=139
	ChamrajaPet=140
	AzadNagar=141
	Sunkenahalli=142
	VishveshwaraPuram=143
	Siddapura=144
	HombegowdaNagar=145
	Lakkasandra=146
	Adugodi=147
	Ejipura=148
	Varthur=149
	Bellanduru=150
	Koramangala=151
	SuddaguntePalya=152
	Jayanagar=153
	Basavanagudi=154
	HanumanthNagar=155
	SriNagar=156
	GaliAnjenayaTempleWard=157
	DeepanjaliNagar=158
	Kengeri=159
	RajaRajeshwariNagar=160
	Hosakerehalli=161
	GiriNagar=162
	Katriguppe=163
	VidyaPeetaWard=164
	GaneshMandirWard=165
	KariSandra=166
	Yediyur=167
	PattabhiRamNagar=168
	ByraSandra=169
	JayanagarEast=170
	GurappanaPalya=171
	Madivala=172
	JakkaSandra=173
	HSRLayout=174
	Bommanahalli=175
	BTMLayout=176
	JPNagar=177
	Sarakki=178
	ShakambariNarar=179
	BanashankariTempleWard=180
	KumaraSwamyLayout=181
	PadmanabhaNagar=182
	ChikkalaSandra=183
	Uttarahalli=184
	Yelchenahalli=185
	Jaraganahalli=186
	Puttenahalli=187
	Bilekhalli=188
	HongaSandra=189
	MangammanaPalya=190
	SingaSandra=191
	Begur=192
	Arakere=193
	Gottigere=194
	Konankunte=195
	Anjanapura=196
	Vasanthpura=197
	Hemmigepura=198
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/CC/test2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
'''import csv
with open('./AreaNameEnum.csv', mode='r') as infile:
    reader = csv.reader(infile)
    mydict = {rows[0]:rows[1] for rows in reader}
#print(mydict.keys())
# return Response("{'a':'b'}", status=201, mimetype='application/json')'''

class Pool(db.Model):
	__tablename__ = "Pool_details"
	i = db.Column(db.Integer,primary_key=True,nullable=False)#,autoincrement=True)
	ride_id = db.Column(db.Integer,nullable=False)
	username = db.Column(db.String(80))#,primary_key=True)
	def __init__(self,ride_id,username):
		#self.i = waste
		self.ride_id = ride_id
		self.username = username
class Ride(db.Model):
	__tablename__ = "Ride_details"
	ride_id = db.Column(db.Integer,primary_key=True,nullable=False)
	created_by = db.Column(db.String(80),nullable=False)
	timestamp = db.Column(db.String(80),nullable=False)
	source = db.Column(db.Integer,nullable=False)
	destination =db.Column(db.Integer,nullable=False)
	def __init__(self,created_by,timestamp,source,destination):
		#self.ride_id = ride_id_g
		#self.ride_id=random.random()
		self.created_by = created_by
		#self.timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%d-%m-%y:%S-%M-%H')
		self.timestamp = datetime.datetime.strptime(timestamp, '%d-%m-%Y:%S-%M-%H')
		self.source = source
		self.destination = destination

class User(db.Model):
	__tablename__ = "RideShare"
	username = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)
	password = db.Column(db.String(40), nullable=False)
	def __init__(self,username,password):
		self.username = username
		self.password = password
#API3
@app.route("/api/v1/rides/",methods=["POST"])
def create_ride():
	if not (request.method=="POST"):
		return Response("{}", status=405, mimetype='application/json')
	content = request.get_json()
	pattern=re.compile(r'^(?:(?:31(-)(?:0?[13578]|1[02]))\1|(?:(?:29|30)(-)(?:0?[13-9]|1[0-2])\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29(-)0?2\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])(-)(?:(?:0?[1-9])|(?:1[0-2]))\4(?:(?:1[6-9]|[2-9]\d)?\d{2})(:)[0-5][0-9](-)[0-5][0-9](-)[0-2][0-3]$')
	match = re.match(pattern,content["timestamp"])
	#if not any(x for x in Constants if x.value == content["source"]):
	#if match==None or content["source"]==content["destination"] or str(content["source"]) not in mydict.keys() or str(content["destination"]) not in mydict.keys() :
	if match==None or content["source"]==content["destination"] or not any(x for x in Constants if x.value == content["source"]) or not any(x for x in Constants if x.value == content["destination"]):
		return Response("{}", status=400, mimetype='application/json')
	if requests.post("http://0.0.0.0:80/api/v1/db/read",json={"table_name":"RideShare","username":content["created_by"]}).text=="1":
		requests.post("http://0.0.0.0:80/api/v1/db/write",json={"table_name":"Ride_details","created_by":content["created_by"],"timestamp":content["timestamp"],"source":content["source"],"destination":content["destination"],"opt":"2"})
		#return "201"
		return Response("{}", status=200, mimetype='application/json')
	else:
		#return "400"
		return Response("{}", status=400, mimetype='application/json')
	

#API 1
@app.route("/api/v1/users/",methods=["PUT"])
def new_user():
	if not (request.method=="PUT"):
		return Response("{}", status=405, mimetype='application/json')
	content = request.get_json()
	pattern = re.compile(r'\b[0-9a-fA-F]{40}\b')
	match = re.match(pattern,content["password"])
	if match == None:
		#return "400"
		return Response("{}", status=400, mimetype='application/json')
	if requests.post("http://0.0.0.0:80/api/v1/db/read",json={"table_name":"RideShare","username":content["username"]}).text=="1":
		#return "405"
		return Response("{}", status=405, mimetype='application/json')
	else:
		requests.post("http://0.0.0.0:80/api/v1/db/write",json={"table_name":"RideShare","username":content["username"],"password":content["password"],"opt":"1"})
		#return "201"
		return Response("{}", status=201, mimetype='application/json')

#API2
@app.route("/api/v1/users/<username>",methods=["DELETE"])
def remove_user(username):	
	if not (request.method=="DELETE"):
		return Response("{}", status=405, mimetype='application/json')
	#requests.post("http://127.0.0.1:5000/api/v1/db/read",json={"table_name":"RideShare","username":username})
	if(requests.post("http://0.0.0.0:80/api/v1/db/read",json={"table_name":"RideShare","username":username}).text=="1"):
		'''a = User.query.filter_by(username=username).first()
		b = Ride.query.filter_by(created_by=username).all()
		c = Pool.query.filter_by(username=username).all()
		db.session.delete(a)
		db.session.commit()
		for b1 in b:
			db.session.delete(b1)
			db.session.commit()
		for c1 in c:
			db.session.delete(c)
			db.session.commit()'''
		#return "200"	
		a = requests.post("http://0.0.0.0:80/api/v1/db/write",json={"table_name":"RideShare","username":username,"opt":"2"})
		b = requests.post("http://0.0.0.0:80/api/v1/db/write",json={"table_name":"Ride_details","username":username,"opt":"3"})
		c = requests.post("http://0.0.0.0:80/api/v1/db/write",json={"table_name":"Pool_details","username":username,"opt":"3"})
		return Response("{}", status=200, mimetype='application/json')
	else:
		return Response("{}", status=400, mimetype='application/json')
		#return "400"
	#return "%s"%b

#API4
@app.route("/api/v1/rides/",methods=["GET"])
def list_ride():
	if not (request.method=="GET"):
		return Response("{}", status=405, mimetype='application/json')
	source = request.args.get("source")
	destination = request.args.get("destination")
	#if str(source) not in mydict.keys() or str("destination") not in mydict.keys():
	if not any(x for x in Constants if x.value == int(source)) or not any(x for x in Constants if x.value == int(destination)):
		return Response("{}", status=400, mimetype='application/json')
	#a = requests.post("http://127.0.0.1:5000/api/v1/db/read",json={"table_name":"RideShare","username":content["username"]}).text=="1"
	b = requests.post("http://0.0.0.0:80/api/v1/db/read",json={"table_name":"Ride_details","source":source,"destination":destination,"opt":"2"}).text=="1"
	#return str(b)
	if b:
		#return "hey"
		#compare here for timestamp,, only if the timestamp is > system time return details.
		c = requests.post("http://0.0.0.0:80/api/v1/db/read",json={"table_name":"Ride_details","source":source,"destination":destination,"opt":"1"})
		return c.text
		#return Response(jsonify(c.text), status=400, mimetype='application/json')
		#make_response(jsonify(c.text), 200)
	else:
		#return "400"
		return Response("{}", status=400, mimetype='application/json')
	
#API6
@app.route("/api/v1/rides/<ride_id>",methods=["POST"])
def join_ride(ride_id):
	if not (request.method=="POST"):
		return Response("{}", status=405, mimetype='application/json')
	content = request.get_json()
	#to check if user exists
	a = requests.post("http://0.0.0.0:80/api/v1/db/read",json={"table_name":"RideShare","username":content["username"]}).text=="1"
	b = requests.post("http://0.0.0.0:80/api/v1/db/read",json={"table_name":"Ride_details","ride_id":ride_id,"opt":"3"}).text=="1"
	#q  = Ride.query.filter_by(ride_id=ride_id).first()
	q = requests.post("http://0.0.0.0:80/api/v1/db/read",json={"table_name":"Ride_details","ride_id":ride_id,"opt":"4"})
	#return q.text
	#if a and b and not(content["username"]==q.created_by):
	if a and b and not(content["username"]==q.text):
		d = requests.post("http://0.0.0.0:80/api/v1/db/read",json={"table_name":"Pool_details","ride_id":ride_id,"username":content["username"],"opt":"2"}).text=="1"
		if d:
			#return "hey"
			requests.post("http://0.0.0.0:80/api/v1/db/write",json={"table_name":"Pool_details","ride_id":ride_id,"username":content["username"],"opt":"2"})
			#return "200"
			return Response("{}", status=200, mimetype='application/json')
		else:
			return Response("{}", status=400, mimetype='application/json')
	else:
		#return "405"
		return Response("{}", status=400, mimetype='application/json')

#API7
@app.route("/api/v1/rides/<ride_id>",methods=["DELETE"])
def del_ride(ride_id):
	if not (request.method=="DELETE"):
		return Response("{}", status=405, mimetype='application/json')
	b = requests.post("http://0.0.0.0:80/api/v1/db/read",json={"table_name":"Ride_details","ride_id":ride_id,"opt":"3"}).text=="1"
	if b:

		'''a = Ride.query.filter_by(ride_id=ride_id).all()
		for r in a:
			db.session.delete(r)
			db.session.commit()'''
		a = requests.post("http://0.0.0.0:80/api/v1/db/write",json={"table_name":"Ride_details","ride_id":ride_id,"opt":"1"})
		c = requests.post("http://0.0.0.0:80/api/v1/db/read",json={"table_name":"Pool_details","ride_id":ride_id,"opt":"1"}).text=="1"
		if c:
			d = requests.post("http://0.0.0.0:80/api/v1/db/write",json={"table_name":"Pool_details","ride_id":ride_id,"opt":"1"})
			'''d = Pool.query.filter_by(ride_id=ride_id).all()
			for r in d:
				db.session.delete(r)
				db.session.commit()'''
		#return "200"
		return Response("{}", status=200, mimetype='application/json')
	else:
		#return "405"
		return Response("{}", status=405, mimetype='application/json')

#API5
@app.route("/api/v1/rides/<ride_id>",methods=["GET"])
def get_ride(ride_id):
	if not (request.method=="GET"):
		return Response("{}", status=405, mimetype='application/json')
	b = requests.post("http://0.0.0.0:80/api/v1/db/read",json={"table_name":"Ride_details","ride_id":ride_id,"opt":"3"}).text=="1"
	if b:
		u = []
		#rows  = Pool.query.filter_by(ride_id=ride_id).all()
		rows = requests.post("http://0.0.0.0:80/api/v1/db/read",json={"table_name":"Pool_details","ride_id":ride_id,"opt":"3"})
		#rows.text is a list of users.
		#return rows.json()
		'''for r in rows:
			u.append(r.username)'''
		#entry = Ride.query.filter_by(ride_id=ride_id).first()
		entry = requests.post("http://0.0.0.0:80/api/v1/db/read",json={"table_name":"Ride_details","ride_id":ride_id,"opt":"5"})
		l=[]
		#return entry.text
		l=entry.json()
		result ={}
		result["rideId"] = ride_id
		result["username"] = l[3]
		result["users"] = rows.json()
		result["timestamp"] = l[0]
		result["source"] = l[1]
		result["destination"] = l[2]
		return result
		#make_response(jsonify(result), 200)
	else:
		#return "405"
		return Response("{}", status=400, mimetype='application/json')

#API9
@app.route("/api/v1/db/read",methods=["POST"])
def read_db():
	content = request.get_json()
	if content["table_name"]=="RideShare":
		#return "2"
		#a = db.session.query(db.exists().where(User.username==content["username"])).scalar()
		a = User.query.filter_by(username=content["username"]).all()
		if len(a)==0:
			return "0"
		else:
			return "1" 
	if content["table_name"]=="Ride_details":
		if content["opt"]=="1":
			#return "hi"
			l={}
			v={}
			i=0
			t=datetime.datetime.fromtimestamp(time.time()).strftime('%d-%m-%y:%S-%M-%H')
			x=datetime.datetime.strptime(t, '%d-%m-%y:%S-%M-%H')
			rides = Ride.query.filter(Ride.timestamp>=x,Ride.source==content["source"],Ride.destination==content["destination"]).all()
			#rides = Ride.query.filter_by(source=content["source"],destination=content["destination"]).all()
			for r in rides:
				if requests.post("http://0.0.0.0:80/api/v1/db/read",json={"table_name":"RideShare","username":r.created_by}).text=="1":
					l[i]={"ride_id":r.ride_id,"username":r.created_by,"timestamp":r.timestamp}
					i+=1
			return jsonify(list(l.values()))

		elif content["opt"]=="2":
			#t=datetime.datetime.fromtimestamp(time.time()).strftime('%d-%m-%y:%S-%M-%H')
			#x=datetime.datetime.strptime(t, '%d-%m-%y:%S-%M-%H')
			a = Ride.query.filter_by(source=content["source"],destination=content["destination"]).all()
			#datetime_object = datetime.strptime('Jun 1 2005  1:33PM', '%b %d %Y %I:%M%p')
			#a = Ride.query.filter(Ride.timestamp>=x,Ride.source==content["source"],Ride.destination==content["destination"]).all()
			#return type(t)
			#a = session.query(Ride).filter(Ride.timestamp>=t,Ride.source==content["source"],Ride.destination==content["destination"])
			if len(a)==0:
				return "0"
			else:
				return "1"
			#return "3"
			#return db.session.query(db.exists().where(Ride.source==content["source"])).scalar() and db.session.query(db.exists().where(Ride.destination==content["destination"])).scalar()
		elif content["opt"]=="3":
			#return "4"
			a = Ride.query.filter_by(ride_id=content["ride_id"]).all()
			if len(a)!=0:
				return "1"
			else:
				return "0"
		elif content["opt"]=="4":
			#return "hell"
			q  = Ride.query.filter_by(ride_id=content["ride_id"]).first()
			return str(q.created_by)
		elif content["opt"]=="5":
			l=[None]*4
			entry = Ride.query.filter_by(ride_id=content["ride_id"]).first()
			l[0]  =entry.timestamp
			l[1] = entry.source
			l[2] = entry.destination
			l[3] = entry.created_by
			return jsonify(l)
	if content["table_name"]=="Pool_details":
		if content["opt"]=="2": #user shouldnt already be in POOL for THAT ride
			a=Pool.query.filter_by(ride_id=content["ride_id"],username=content["username"]).all()
			if len(a)!=0:
				return "0"
			else:
				return "1"
		if content["opt"]=="3":
			rows  = Pool.query.filter_by(ride_id=content["ride_id"]).all()
			l = []
			for i in rows:
				l.append(i.username)
			return jsonify(l)
		elif content["opt"]=="1":
			a = Pool.query.filter_by(ride_id=content["ride_id"]).all()
			if len(a)!=0:
				return "1"
			else:
				return "0"

#API8
@app.route("/api/v1/db/write",methods=["POST"])
def write_db():
	content = request.get_json()
	if(content["table_name"]=="RideShare"):
		if content["opt"]=="1":
			u = User(content["username"],content["password"])
			db.create_all()
			db.session.add(u)
			db.session.commit()
		elif content["opt"]=="2":
			a = User.query.filter_by(username=content["username"]).first()
			db.session.delete(a)
			db.session.commit()

	elif(content["table_name"]=="Ride_details"):
		if content["opt"]=="1": #delete ride
			a = Ride.query.filter_by(ride_id=content["ride_id"]).all()
			for r in a:
				db.session.delete(r)
				db.session.commit()
			return "200"
		elif content["opt"]=="2":
			u = Ride(content["created_by"],content["timestamp"],content["source"],content["destination"])
			db.create_all()
			db.session.add(u)
			db.session.commit()
		elif content["opt"]=="3":
			b = Ride.query.filter_by(created_by=content["username"]).all()
			for b1 in b:
				db.session.delete(b1)
				db.session.commit()
	elif(content["table_name"]=="Pool_details"):
		if content["opt"]=="1": #delete ride
			d = Pool.query.filter_by(ride_id=content["ride_id"]).all()
			for r in d:
				db.session.delete(r)
				db.session.commit()
			return "200"
		elif content["opt"]=="2":
			u = Pool(content["ride_id"],content["username"])
			db.create_all()
			db.session.add(u)
			db.session.commit()
		elif content["opt"]=="3":
			c = Pool.query.filter_by(username=content["username"]).all()
			for c1 in c:
				db.session.delete(c1)
				db.session.commit()
	
	return "200"

if __name__ == "__main__":
	#app.debug=True
	#app.run(debug=True,host="0.0.0.0",port="80")
	app.run(host="0.0.0.0",port="80")