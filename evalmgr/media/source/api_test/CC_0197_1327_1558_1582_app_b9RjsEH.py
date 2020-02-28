import requests, json
from flask import Flask, jsonify
from flask import request
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db = SQLAlchemy(app)


class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True, nullable=False)
	password = db.Column(db.String(40), nullable=False)

class Rides(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	created_by = db.Column(db.String(80), nullable=False)
	timestamp = db.Column(db.String(80),nullable=False)
	source = db.Column(db.Integer,nullable=False)
	destination = db.Column(db.Integer,nullable=False)

class ID_UNAME(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	rideid = db.Column(db.Integer,nullable=False)
	username = db.Column(db.String(80), nullable=False)


def check_passwd(passwd):
	if len(passwd) == 40:
		for i in passwd:
			if i not in "ABCDEF0123456789abcdef":
				return 0
		return 1
	return 0
	
#def check_date_time(timestamp):

	

@app.route('/api/v1/db/read',methods=['POST'])
def read_db():
	id=request.get_json()["id"]
	if(id==1):
		uname=request.get_json()["username"]
		if(User.query.filter_by(username=uname).first()):
			return jsonify({"value":"exist"})
		else:
			return jsonify({"value":"no"})

	if(id==2):
		uname=request.get_json()["username"]		
		if(User.query.filter_by(username=uname).first()):
			return jsonify({"value":"exist"})
		else:
			return jsonify({"value":"no"})

	if(id==3):
		src=request.get_json()["source"]
		dst=request.get_json()["destination"]
		ride_list=Rides.query.filter_by(source=src,destination=dst).all()
		f_l=[]
		for ride in ride_list:
			t1 = datetime.datetime.strptime(str(ride.timestamp), "%d-%m-%Y:%S-%M-%H")
			now = datetime.datetime.now().strftime("%d-%m-%Y:%S-%M-%H")
			now = datetime.datetime.strptime(str(now),"%d-%m-%Y:%S-%M-%H")
			if t1 > now:
				d={}
				d["rideID"]=ride.id
				d["created_by"]=ride.created_by
				d["timestamp"]=ride.timestamp
				f_l.append(d)
		return jsonify({"ridesList":f_l})

	if(id==4):
		rideid = request.get_json()["rideid"]
		ride = Rides.query.filter_by(id=rideid).first()
		if(ride):
			d={}
			d["rideID"]=ride.id			
			d["created_by"]=ride.created_by
			l=ID_UNAME.query.filter_by(rideid=rideid).all()
			user=[]
			for i in l:
				user.append(i.username)
			d["users"]=user
			d["timestamp"]=ride.timestamp
			d["source"]=ride.source
			d["destination"]=ride.destination
			return {"data":d},200
	
		else:
			return {},400
	if(id==5):
		uname=request.get_json()["username"]
		rideid=request.get_json()["rideid"]
		if(User.query.filter_by(username=uname).first()):
			if(Rides.query.filter_by(id=rideid).first()):
				return jsonify({"value":"exist"})
		else:
			return jsonify({"value":"no"})
	if(id==6):
		rideid=request.get_json()["rideid"]
		print(rideid)
		if(Rides.query.filter_by(id=rideid).first()):
			print("hello")
			return jsonify({"value":"exist"})
		else:
			return jsonify({"value":"no"})	

@app.route('/api/v1/db/write',methods=['POST'])
def write_db():
	id=request.get_json()["id"]
	if(id==1):
		uname=request.get_json()["username"]
		pswd=request.get_json()["password"]
		add_new_user=User(username=uname,password=pswd)
		db.session.add(add_new_user)
		#print(add_new_user)
		db.session.commit()
		#print(add_new_user)
	if(id==2):
		uname=request.get_json()["username"]
		rm_user= User.query.filter_by(username=uname).first()
		db.session.delete(rm_user)
		db.session.commit()
		return {},200
	if(id==3):
		uname=request.get_json()["created_by"]
		datetime=request.get_json()["timestamp"]
		src=request.get_json()["source"]
		dst=request.get_json()["destination"]
		add_new_ride=Rides(created_by=uname,timestamp=datetime,source=src,destination=dst)
		db.session.add(add_new_ride)
		db.session.commit()
		return {},200
	if(id==4):
		uname=request.get_json()["username"]
		rideid=request.get_json()["rideid"]
		join_ride=ID_UNAME(rideid=rideid,username=uname)
		db.session.add(join_ride)
		db.session.commit()
		return {},200
	if(id==5):
		rideid=request.get_json()["rideid"]
		ride1=ID_UNAME.query.filter_by(rideid=rideid).all()
		ride2=Rides.query.filter_by(id=rideid).first()
		for i in ride1:
			db.session.delete(i)
		db.session.delete(ride2)
		db.session.commit()
		return {},200
	return {}, 200


@app.route('/api/v1/users',methods=['PUT'])
def add_user():
	if request.method == 'PUT':
		uname=request.get_json()["username"]
		r=requests.post(url='http://127.0.0.1:5000/api/v1/db/read', json={"id":1,"username":uname})
		#print(r.text)
		r=json.loads(r.text)
		if(r["value"]=="no"):
			pswd=request.get_json()["password"]
			if(check_passwd(pswd)):
				#print("hello")
				new_data={"id":1,"username":uname,"password":pswd}
				r1=requests.post(url='http://127.0.0.1:5000/api/v1/db/write',json=new_data)
				if r1.status_code==200:
					return {},201
			else:
				return "invalid pwd",400
		return "user",400
	return "",405


@app.route('/api/v1/users/<username>',methods=['DELETE'])
def delete_user(username):
	if request.method == 'DELETE':
		r=requests.post(url='http://127.0.0.1:5000/api/v1/db/read', json={"id":2,"username":username})
		r=json.loads(r.text)
		if(r["value"]=="no"):
			return {},400
		else:
			r=requests.post(url='http://127.0.0.1:5000/api/v1/db/write', json={"id":2,"username":username})
			return {}, 200
	else:
		return {},405


@app.route('/api/v1/rides',methods=['POST'])
def new_ride():
	if request.method == 'POST':
		uname=request.get_json()["created_by"]
		r=requests.post(url='http://127.0.0.1:5000/api/v1/db/read', json={"id":1,"username":uname})
		r=json.loads(r.text)
		if(r["value"]=="exist"):
			#print("hello")
			datetime=request.get_json()["timestamp"]
			src=request.get_json()["source"]
			dst=request.get_json()["destination"]
			new_data={"id":3,"created_by":uname,"timestamp":datetime,"source":src,"destination":dst}
			r1=requests.post(url='http://127.0.0.1:5000/api/v1/db/write',json=new_data)
			if r1.status_code==200:
					return {},201
						

		else:
			return "user",400
	return {},405	

@app.route('/api/v1/rides',methods=['GET'])
def upcumming_rides():
	if request.method == 'GET':
		src=0
		dst=0
		src = request.args.get('source')
		dst = request.args.get('destination')
		if(src==0 or dst==0 or int(src)>199 or int(dst)>199):
			return {},400
		else:
			data={"id":3,"source":src,"destination":dst}
			r=requests.post(url='http://127.0.0.1:5000/api/v1/db/read', json=data)
			list = r.json()["ridesList"]
			if(len(list)==0):
				return {},204
			return jsonify(list),200
	else:
		return {},405
		
@app.route('/api/v1/rides/<id>',methods=['GET'])
def ride_details(id):
	if request.method == 'GET':
		r=requests.post(url='http://127.0.0.1:5000/api/v1/db/read', json={"id":4,"rideid":id})
		if(r.status_code!=400):
			return jsonify(r.json()["data"])
		else:
			return {},400
	else:
		return {},405

@app.route('/api/v1/rides/<id>',methods=['POST'])
def join_ride(id):
	if request.method == 'POST':
		uname=request.get_json()["username"]
		r=requests.post(url='http://127.0.0.1:5000/api/v1/db/read',json={"id":5,"username":uname,"rideid":id})
		r=json.loads(r.text)
		if(r["value"]=="exist"):
			new_data={"id":4,"rideid":id,"username":uname}
			r1=requests.post(url='http://127.0.0.1:5000/api/v1/db/write',json=new_data)
			if r1.status_code==200:
				return {},201
		else:
			return "user",400
	else:
		return {},405

@app.route('/api/v1/rides/<id>',methods=['DELETE'])
def delete_ride(id):
	if request.method == 'DELETE':
		r=requests.post(url='http://127.0.0.1:5000/api/v1/db/read', json={"id":6,"rideid":id})	
		r=json.loads(r.text)
		if(r["value"]=="no"):
			return {},400
		else:
			r=requests.post(url='http://127.0.0.1:5000/api/v1/db/write', json={"id":5,"rideid":id})	
		return {}, 200
	else:
		return {},405
@app.route('/')
def hello_world():
	return 'Hello, World!'

if __name__=="__main__":
	db.create_all()
	app.run(debug=True)
