from flask import Flask,make_response,request,jsonify,session,Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.attributes import flag_modified
from datetime import datetime
from time import strftime
import pickle 
import requests
import re
import json
import os

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:////home/ubuntu/myproject/rideshare.db'
db=SQLAlchemy(app)


class Rides(db.Model):
	__tablename__="Rides"
	id=db.Column(db.Integer,primary_key=True)
	username = db.Column(db.String,db.ForeignKey('Users.username'),nullable=False)
	timestamp = db.Column(db.String,nullable=False)
	source = db.Column(db.Integer,nullable=False)
	destination = db.Column(db.Integer,nullable=False,unique=False)
	users = db.Column(db.PickleType,nullable=True)
	
	user = db.relationship('Users',backref=db.backref('ride',lazy=True))
	
	def __init__(self,username,source,destination,timestamp=None,users=None):
		self.username=username
		self.timestamp=timestamp
		self.source=source
		self.destination=destination
		self.users=users
		
	#def __repr__(self):
		#return 'rideid : %r , username : %r , timestamp : %r , source : %r , destination : %r , Users : %r' %(self.id,self.username,self.timestamp,self.source,self.destination,self.users)

		
class Users(db.Model):
	__tablename__="Users"
	username = db.Column(db.String,primary_key=True)
	password = db.Column(db.String,nullable=False)
	
	def __init__(self,username,password):
		self.username=username
		self.password=password
		
	def __repr__(self):
		return 'Username : %s , password : %s' %(self.username,self.password)
		
db.create_all()
	
#9.Write to db	
@app.route("/api/v1/db/write",methods=["DELETE","POST"])
def writedb():
	data = request.get_json()
	if data['table']=="Users" and data['op']=="adding":
		new_user=Users(username=data['username'],password=data['password'])
		db.session.add(new_user)
		db.session.commit()
		return "created"
	elif data['table']=="Users" and data['op']=="deleting":
		usernm = data['username']
		delete_user = Users.query.get(usernm)
		db.session.delete(delete_user)
		db.session.commit()
		return "deleted"
	elif data['table']=="Rides" and data['op']=="creating":
		create_ride=Rides(username=data['created_by'],timestamp=data['timestamp'],source=data['source'],destination=data['destination'])
		db.session.add(create_ride)
		db.session.commit()
		return "created"
	elif data['table']=="Rides" and data['op']=="deleting":
		rideid=data['rideid']
		delete_ride=Rides.query.get(rideid)
		db.session.delete(delete_ride)
		db.session.commit()
		return "deleted"
	elif data['op']=="joining":
		juser=data['username']
		jid=data['rideid']
		result=Rides.query.filter(Rides.id==jid).first()
		s=result.users
		if juser not in s:
			s.append(juser)
			result.users=s
			flag_modified(result,"users")
			db.session.merge(result)
			db.session.flush()
			db.session.commit()
			return "joined"
		else:
			return "failed"
			
	
#8.Read from db		
@app.route("/api/v1/db/read",methods=["POST","DELETE","GET"])
def readdb():
	data=request.json
	tablename=data["table"]  
	Operations=data['op']
	if tablename=="Users" and (Operations=="adding" or Operations=="deleting"):
		user=data['username']
		c= Users.query.filter(Users.username==user).all()
		if c:
			return "exist"
		else:
			return "does_not_exist"
	elif tablename=="Rides" and Operations=="creating":
		ride_user=data['created_by']
		d=Users.query.filter(Users.username==ride_user).all()
		if d:
			return "exist"
		else:
			return "does_not_exist"
	elif tablename=="Rides" and Operations=="deleting":
		ride_rec=data['rideid']
		e=Rides.query.filter(Rides.id==ride_rec).all()
		if e:
			return "exist"
		else:
			return "does_not_exist"
	elif tablename=="Rides" and Operations=="listing":
		ride_list=data['rideid']
		f=Rides.query.filter(Rides.id==ride_list).first()
		if f:
			#return "exist"
			#return str(f.id)
			y={}
			y["rideId"]=str(f.id)
			y["Created_by"]=str(f.username)
			if str(f.users)=="None":
				u=[]
				y["users"]=u
			else:
				y["users"]=str(f.users)
			y["Timestamp"]=str(f.timestamp)
			y["source"]=str(f.source)
			y["destination"]=str(f.destination)
			return y
		else:
			return "not_found"
	elif tablename=="Rides" and Operations=="joining":
		ride_join=data['rideid']
		g=Rides.query.filter(Rides.id==ride_join).first()
		if g:
			user_join=data['username']
			h=Users.query.filter(Users.username==user_join).first()
			if h:
				return "exist"
			else:
				return "does_not_exist"
		else:
			return "does_not_exist"
	elif tablename=="Rides" and Operations=="upcoming":
		src=data['source']
		dest=data['destination']
		rideup=Rides.query.filter(Rides.source==int(src),Rides.destination==int(dest)).all()
		if not rideup:
			return "not_found"
		else:
			r=str(rideup)
			upcoming=[]
			x=map(int,re.findall(r'\d+',r))
			z=list(x)
			if(len(z)==0):
				return "no"
			else:
				for i in z:
					y=Rides.query.get(i)
					#return y.timestamp
					stamp=y.timestamp
					#return stamp
					dt_value=datetime.strptime(stamp,'%d-%m-%Y:%S-%M-%H')
					#return dt_value
					pres_dt_value=datetime.utcnow()
					user1=y.username
					#return user1
					ucheck=Users.query.filter(Users.username==user1).first()
					#return str(ucheck)
					if(str(ucheck)=="None"):
						pass
					elif (dt_value>pres_dt_value):
						d={}
						d["rideId"]=y.id
						d["username"]=y.username
						d["timestamp"]=y.timestamp
						upcoming.append(d)
				if(len(upcoming)==0):
					return "not_found"
				else:
					return jsonify(upcoming)
			
			

#1.Add User
@app.route("/api/v1/users",methods=["PUT"])
def AddUser():
	if request.method=="PUT":
		data = request.json
		data.update({"table":"Users"})
		data.update({"op":"adding"})
		response_r = requests.post("http://0.0.0.0:80/api/v1/db/read",json=data)
		ans = response_r.text
		#return ans
		if ans=="does_not_exist":
			passwd = data['password']
			usernm = data['username']
			if re.match('[a-f0-9]{40}',passwd) and usernm!="":
				response_w=requests.post("http://0.0.0.0:80/api/v1/db/write",json=data)
				ans1=response_w.text
				if ans1=="created":
					return make_response(" ",201)
			else:
				return make_response(" ",400)
		elif ans=="exist":
			return make_response(" ",400)
	else:
		return make_response(" ",405)
	
#2.Remove User
@app.route("/api/v1/users/<username>",methods=["DELETE"])
def RemoveUser(username):
	if request.method=="DELETE": 
		x = {"table":"Users","username":username,"op":"deleting"}
		x=json.dumps(x)
		data=json.loads(x)
		response_r=requests.post("http://0.0.0.0:80/api/v1/db/read",json=data)
		ans = response_r.text
		if ans=="exist":
			response_w = requests.post("http://0.0.0.0:80/api/v1/db/write",json=data)
			ans1 = response_w.text
			if ans1=="deleted":
				return make_response(" ",200)
			else:
				return make_response(" ",400)
	else:
		return make_response(" ",405)
		
#3.Create Ride
@app.route("/api/v1/rides",methods=["POST"])
def CreateRide():
	if request.method=="POST":
		data = request.json
		data.update({"table":"Rides"})
		data.update({"op":"creating"})
		response_r = requests.post("http://0.0.0.0:80/api/v1/db/read",json=data)
		ans = response_r.text
		if ans=="exist":
			response_w=requests.post("http://0.0.0.0:80/api/v1/db/write",json=data)
			ans1=response_w.text
			if ans1=="created":
				return make_response(" ",201)
		elif ans=="does_not_exist":
			return make_response(" ",400)
	else:
		return make_response(" ",405)
		
#7.Delete Ride
@app.route("/api/v1/rides/<rideid>",methods=["DELETE"])
def DeleteRide(rideid): 
	if request.method=="DELETE":
		x = {"table":"Rides","rideid":rideid,"op":"deleting"}
		x=json.dumps(x)
		data = json.loads(x)
		response_r=requests.post("http://0.0.0.0:80/api/v1/db/read",json=data)
		ans = response_r.text
		if ans=="exist":
			response_w = requests.post("http://0.0.0.0:80/api/v1/db/write",json=data)
			ans1 = response_w.text
			if ans1=="deleted":
				return make_response(" ",200)
		else:
			return make_response(" ",400)
	else:
		return make_response("",405)
		
#5.Listing all details of a given ride
@app.route("/api/v1/rides/<rideid>",methods=["GET"])
def ListRideDet(rideid):
	if request.method=="GET":
		x={"rideid":rideid,"op":"listing","table":"Rides"}
		x=json.dumps(x)
		data=json.loads(x)
		response_r=requests.post("http://0.0.0.0:80/api/v1/db/read",json=data)
		ans = response_r.text
		if ans=="not_found":
			return make_response("",204)
		else:
			return ans,200
	else:
		return make_response("",405)

#6.Join an existing ride
@app.route("/api/v1/rides/<rideid>",methods=["POST"])
def JoinRide(rideid):
	if request.method=="POST":
		data=request.json
		data.update({"rideid":rideid})
		data.update({"op":"joining"})
		data.update({"table":"Rides"})
		response_r=requests.post("http://0.0.0.0:80/api/v1/db/read",json=data)
		ans=response_r.text
		if ans=="exist":
			response_w=requests.post("http://0.0.0.0:80/api/v1/db/write",json=data)
			ans1=response_w.text
			if ans1=="joined":
				return make_response("",200)
		elif ans=="does_not_exist":
			return make_response("",204)
	else:
		return make_response("",405)
		
#4.List all upcoming rides
@app.route("/api/v1/rides",methods=["GET"])
def Uprides():
	if request.method=="GET":
		source=request.args.get('source')
		destination=request.args.get('destination')
		if(int(source)==int(destination)):
			return make_response("",400)
		x={"source":source,"destination":destination,"table":"Rides","op":"upcoming"}
		x=json.dumps(x)
		data=json.loads(x)
		if int(source) in range(199) and int(destination) in range(199):
			response_r=requests.post("http://0.0.0.0:80/api/v1/db/read",json=data)
			ans=response_r.text
			if ans=="not_found":
				return make_response("",204)
			else:
				return ans,200
		else:
			return make_response("",400)
	else:
		return make_response("",405)
		
if __name__=='__main__':
	app.run(debug=True)
	
