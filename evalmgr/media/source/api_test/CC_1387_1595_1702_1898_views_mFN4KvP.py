from flask import Flask,jsonify,request,Response,make_response
import pandas as pd
import re
import datetime
from requests import post,get
from enum import Enum
from sqlalchemy import and_,Column,Integer,String,DateTime
from  flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:''@localhost/app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
class User(db.Model):
	__tablename__ = 'user'
	username = db.Column(db.String(50), primary_key=True)
	password = db.Column(db.String(50))
	userride = db.relationship("Userride",cascade="delete")
class Rideshare(db.Model):
    __tablename__ = 'rideshare'
    rideid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    created_by = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime)
    source = db.Column(db.String(50))
    dest = db.Column(db.String(50))
    userride = db.relationship("Userride",cascade="delete")
class Userride(db.Model):
	__tablename__ = "user_ride"
	rid = db.Column(db.Integer,db.ForeignKey('rideshare.rideid'), primary_key=True)
	users = db.Column(db.String(50),db.ForeignKey('user.username'), primary_key=True)
db.session.commit()
df = pd.read_csv('/var/www/FlaskApp/FlaskApp/AreaNameEnum.csv')
locs = list(df.iloc[:,1])
for i in range(len(locs)):
    locs[i] = "".join(locs[i].split())
Areas = Enum("Areas",locs)

@app.route('/api/v1/users',methods=["PUT"])
def add_user():
	if request.method == "PUT":
		data = request.get_json()
		if re.match(r'[a-fA-F0-9]{40}$',data["password"]):
			r = post('http://0.0.0.0:80/api/v1/db/read',json={"api":"add","usn":data["username"]})
			if r.status_code == 201:
				data["api"] = "add"
				post('http://0.0.0.0:80/api/v1/db/write',json = data)
				return jsonify({}),201
			else:
				return jsonify({}),400
		else:
			return jsonify({}),400
	else:
		return jsonify({}),405

@app.route('/api/v1/rides',methods = ["GET"])
def list_all_upcoming_rides():
	if request.method == "GET":
		src = int(request.args.get('source'))
		dest = int(request.args.get('destination'))
		s = False
		d = False
		for a in Areas:
			if a.value == src:
				s = True
			if a.value == dest:
				d = True
		if src == dest:
			return jsonify({}),400
		if not(s and d):
			return jsonify({}),400
		r = post('http://0.0.0.0:80/api/v1/db/read',json = {"api":"upcoming","src":src,"dest":dest})
		if r.status_code == 204:
			return Response(status=204)
		else:
			return jsonify(r.json()),200
	else:
		return jsonify({}),405


@app.route('/api/v1/rides/<rideId>',methods = ["DELETE"])
def delete_ride(rideId):
	if request.method == "DELETE":
		r = post('http://0.0.0.0:80/api/v1/db/read',json = {"api":"delete","column":rideId})
		if r.status_code == 200:
			post('http://0.0.0.0:80/api/v1/db/write',json = {"api":"delete","column":rideId})
			return jsonify({}),200
		else:
			return jsonify({}),400
	else:
		return jsonify({}),405

@app.route('/api/v1/db/read',methods = ["POST"])
def read():
	if request.get_json()["api"] == "add":
		try:
			u = User.query.filter_by(username = request.get_json()["usn"]).one()
		except:
			return jsonify({}),201
		return jsonify({}),400
	elif request.get_json()["api"] == "addride":
		try:
			u = User.query.filter_by(username = request.get_json()["created_by"]).one()
		except:
			return jsonify({}),400
		return jsonify({}),201
	elif request.get_json()["api"] == "delete":
	    try:
	    	u = Rideshare.query.filter_by(rideid = request.get_json()["column"]).one()
	    except:
	    	return jsonify({}),400
	    return jsonify({}),200
	elif request.get_json()["api"] == "upcoming":
		l = []
		try:
			u = Rideshare.query.filter(and_(Rideshare.source == request.get_json()["src"],Rideshare.dest == request.get_json()["dest"])).all()
			for i in u:
				try:
					b = User.query.filter_by(username=i.created_by).one()
					if i.timestamp > datetime.datetime.now():
						d = {}                                                                                                                                                                  d["rideId"] = i.rideid
						d["username"] = i.created_by
						d["timestamp"] = i.timestamp.strftime('%d-%m-%Y:%S-%M-%H')
						a = Userride.query.filter_by(rid = i.rideid).all()
						l1 = []
						for i in a:
							l1.append(i.users)
						d["users"] = l1
						l.append(d)
				except:
					return Response(status=400)
				if l:
					return jsonify(l),200
				return Response(status=204)
		except:
			return Response(status=204)
	elif request.get_json()["api"] == "remove":
		usn = request.get_json()["column"]
		try:
			u = User.query.filter_by(username = usn).all()
		except:
			return jsonify({}),400
		return jsonify({}),200
	elif request.get_json()["api"] == "list":
		rid = request.get_json()["rideid"]
		try:
			a = Rideshare.query.filter_by(rideid = rid).one()
			dic={}
			dic["rideId"]=a.rideid
			dic["created_by"]=a.created_by
			v = Userride.query.filter_by(rid = rid).all()
			l = []
			for i in v:
				l.append(i.users)
			dic["users"] = l
			dic["timestamp"] = a.timestamp.strftime('%d-%m-%Y:%S-%M-%H')
			dic["source"] = a.source
			dic["destination"] = a.dest
			return jsonify(dic),200
		except:
			return jsonify({}),204
	elif request.get_json()["api"] == "join":
		try:	
			c1 = Rideshare.query.filter_by(rideid = request.get_json()["column1"]).one()
			c2 = User.query.filter_by(username = request.get_json()["column2"]).one()
		except:
			return jsonify({}),400
		return jsonify({}),200


@app.route('/api/v1/db/write',methods = ["POST"])
def write():
	if request.get_json()["api"] == "delete":
		db.session.delete(Rideshare.query.filter_by(rideid = request.get_json()["column"]).one())
		db.session.commit()
		return jsonify({}),200
	if request.get_json()["api"] == "remove":
		db.session.delete(User.query.filter_by(username = request.get_json()["column"]).one())
		db.session.commit()
		return jsonify({}),200
	if request.get_json()["api"] == "addride":
		usn = request.get_json()["created_by"]
		tmp = datetime.datetime.strptime(request.get_json()["timestamp"],'%d-%m-%Y:%S-%M-%H')
		try:
			x = datetime.datetime(tmp.year,tmp.month,tmp.day,tmp.hour,tmp.minute,tmp.second)
		except:
			return jsonify({}),400
		src = request.get_json()["source"]
		dest = request.get_json()["destination"]
		db.session.add(Rideshare(created_by=usn,timestamp=tmp,source=src,dest=dest))
		db.session.commit()
		return jsonify({}),201
	if request.get_json()["api"] == "join":
		try:
			rid=request.get_json()["column1"]
			us=request.get_json()["column2"]
			db.session.add(Userride(rid = rid,users= us))
			db.session.commit()
		except:
			return jsonify({}),400
		return jsonify({}),200
	if request.get_json()["api"] == "add":
		db.session.add(User(username=request.get_json()["username"],password=request.get_json()["password"]))
		db.session.commit()
		return jsonify({}),200

@app.route('/api/v1/users/<username>',methods = ["DELETE"])
def remove_user(username):
	if request.method == "DELETE":
		r = post('http://0.0.0.0:80/api/v1/db/read',json = {"api":"remove","column":username})
		if r.status_code == 400:
			return jsonify({}),400
		elif r.status_code == 200:
			post('http://0.0.0.0:80/api/v1/db/write',json = {"api":"remove","column":username})
			return jsonify({}),200
	else:
		return jsonify({}),405

@app.route('/api/v1/rides',methods=["POST"])
def add_ride():
	if request.method == "POST":
		data=request.get_json()
		data["api"]="addride"
		s = False
		d = False
		for a in Areas:
			if a.value == int(data["source"]):
				s = True
			if a.value == int(data["destination"]):
				d = True
		if int(data["source"]) == int(data["destination"]):
			return jsonify({}),400
		if not(s and d) :
			return jsonify({}),400
		r = post('http://0.0.0.0:80/api/v1/db/read',json = data)
		if r.status_code == 201:
			s = post('http://0.0.0.0:80/api/v1/db/write',json = data)
			if s.status_code == 201:
				return jsonify({}),201
			else:
				return jsonify({}),400
		else:
			return jsonify({}),400
	else:
		return jsonify({}),405

@app.route('/api/v1/rides/<rideId>',methods = ["GET"])
def list_all_the_details(rideId):
	if request.method == "GET":
		r = post('http://0.0.0.0:80/api/v1/db/read',json ={"api":"list","rideid":rideId})
		if r.status_code == 200:
			return jsonify(r.json()),200
		else:
			return jsonify({}),204
	else:
		return jsonify({}),405

@app.route('/api/v1/rides/<rideId>', methods=['POST'])
def joinride(rideId):
	if request.method == "POST":
		username = request.get_json()["username"]
		r=post('http://0.0.0.0:80/api/v1/db/read',json = {"api":"join","column1":rideId,"column2":username})
		if r.status_code == 200:
			r1 = post('http://0.0.0.0:80/api/v1/db/write',json = {"api":"join","column1":rideId,"column2":username})
			if r1.status_code == 200:
				return jsonify({}),200
			return jsonify({}),400
		else:
			return jsonify({}),400
	else:
		return jsonify({}),405

if __name__ == '__main__':
	app.run(debug=True,host="0.0.0.0",port="80")