from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import Flask,jsonify,request,Response
import requests
from sqlalchemy import func
from sqlalchemy.sql import select,text
from sqlalchemy import create_engine
from numpy import genfromtxt
import datetime
import re

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///assignment1.sqlite'
db = SQLAlchemy(app)

#User table
class User(db.Model):
    username = db.Column(db.String(), primary_key=True, nullable=False)
    password = db.Column(db.String(), nullable=False)

    def __init__(self,username,password):
        self.username=username
        self.password=password
 
#Rides table        
class Rides(db.Model):
	rideId = db.Column(db.Integer, primary_key=True,nullable=False)
	created_by = db.Column(db.String(), db.ForeignKey('user.username'),nullable=False)
	users=db.Column(db.String())
	timestamp = db.Column(db.String(19), nullable=False)
	source = db.Column(db.String(),nullable=False)
	destination = db.Column(db.String(),nullable=False)
	
	def __init__(self,rideId,created_by,users,timestamp,source,destination):
	    self.rideId=rideId
	    self.created_by=created_by
	    self.users=users
	    self.timestamp=timestamp
	    self.source=source
	    self.destination=destination

#AreaNum table
class area(db.Model):
	num = db.Column(db.String(),primary_key=True,nullable=False)
	area = db.Column(db.String())
	
	def __init__(self,num,area):
	    self.num=num
	    self.area=area
	    
db.create_all()

def Load_Data(file_name):
    data = genfromtxt(file_name, delimiter=',', skip_header=1,converters={1: lambda s: str(s,'utf-8')})
    return data.tolist()
    
file_name = "AreaNameEnum.csv" 
data = Load_Data(file_name) 
try:
	for i in data:
	    record = area(i[0],i[1])
	    db.session.add(record)
	db.session.commit()
except:
    db.session.rollback()

#add user
@app.route("/api/v1/users",methods=["PUT"])
def add_user():
	try:
		un=request.get_json()["username"]
		pa=request.get_json()["password"]
	except:
		return {},500 	
	re=requests.post("http://127.0.0.1:5051/api/v1/db/read",json={"table":"User","columns":["username"],"where":"username="+"'"+un+"'"})
	if(re.json()):
		return {},405
	try:
		sha=int(pa,16)
	except ValueError:
		return Response("Password should be 40 characters", status=400,mimetype='application/text')
	if(len(pa)!=40):
		return Response("Password should be 40 characters", status=400,mimetype='application/text')		
	else:
		j={"flag":"add","insert":{"username":un,"password":pa},"table":"User"}
		requests.post("http://127.0.0.1:5051/api/v1/db/write",json=j)
		return {},201

#remove user	
@app.route('/api/v1/users/<username>',methods=["DELETE"])
def remove_user(username):
	re=requests.post("http://127.0.0.1:5051/api/v1/db/read",json={"table":"User","columns":["username"],"where":"username="+"'"+username+"'"})
	if(not re.json()):
		return {},405
	else:
		j={"flag":"delete","username":username,"table":"User"}
		requests.post("http://127.0.0.1:5051/api/v1/db/write",json=j)
		j={"flag":"delete","username":username,"table":"Rides"}
		requests.post("http://127.0.0.1:5051/api/v1/db/write",json=j)
		return {},200

#add ride
@app.route("/api/v1/rides",methods=["POST"])
def add_ride():
	try:
		cr=request.get_json()["created_by"]
		ti=request.get_json()["timestamp"]
		s=request.get_json()["source"]
		d=request.get_json()["destination"]		        			
	except:
		return {},500 
	try:
	        d1=datetime.datetime.strptime(ti,'%d-%m-%Y:%S-%M-%H')
	except:
		return Response("Timestamp should be in the format dd-mm-yyyy:ss-mm-hh", status=400,mimetype='application/text')
	if(s==d):
		return Response("Source and destination cannot be the same",status=400,mimetype='application/text')
	re=requests.post("http://127.0.0.1:5051/api/v1/db/read",json={"table":"User","columns":["username"],"where":"username="+"'"+cr+"'"})
	if(not re.json()):
		return {},405
	else:
		j={"flag":"add","insert":{"created_by":cr,"timestamp":ti,"source":s,"destination":d},"table":"Rides"}
		requests.post("http://127.0.0.1:5051/api/v1/db/write",json=j)
		return {},201

#remove ride	
@app.route("/api/v1/rides/<rideId>",methods=["DELETE"])
def remove_ride(rideId):
	re=requests.post("http://127.0.0.1:5051/api/v1/db/read",json={"table":"Rides","columns":["rideId"],"where":"rideId="+"'"+rideId+"'"})
	if(not re.json()):
		return {},405
	else:
		j={"flag":"delete","rideId":rideId,"table":"Rides"}
		requests.post("http://127.0.0.1:5051/api/v1/db/write",json=j)
		return {},200
		
#list details of ride
@app.route("/api/v1/rides/<rideId>")
def ride_details(rideId):
	re=requests.post("http://127.0.0.1:5051/api/v1/db/read",json={"table":"Rides","columns":["rideId"],"where":"rideId="+"'"+rideId+"'"})
	if(not re.json()):
		return {},405
	else:
		a=requests.post("http://127.0.0.1:5051/api/v1/db/read",json={"table":"Rides","columns":["rideId","created_by","users","timestamp","source","destination"],"where":"rideId="+"'"+rideId+"'"})
		if(not a.json()):
			return {},204
		return jsonify(a.json()),200

#{"username":"abcde","password":"1111111111111111111111111111111111111111"}
#list upcoming rides between source and destination
@app.route('/api/v1/rides')
def upcoming():
	source=request.args.get('source')
	destination=request.args.get('destination')
	if((source.isdigit()==False) or (destination.isdigit()==False)):
		return Response("Source and destination must be an integer",status=400,mimetype='application/text')
	ar=db.session.query(area).count()
	if(int(source)<1 or int(source)>ar or int(destination)<0 or int(destination)>ar):
		return {},405
	re=requests.post("http://127.0.0.1:5051/api/v1/db/read",json={"table":"Rides","columns":["rideId","created_by","timestamp"],"where":"source="+"'"+str(source)+"' "+"and destination="+"'"+str(destination)+"'"})
	t1 = datetime.datetime.today().strftime("%d-%m-%Y:%S-%M-%H")
	t4 = datetime.datetime.strptime(t1,'%d-%m-%Y:%S-%M-%H')
	d,a={},[]
	for i in re.json():
		t2 = i["timestamp"]
		t3 = datetime.datetime.strptime(t2,'%d-%m-%Y:%S-%M-%H')		
		if(t3>t4):
			for col,val in i.items():
				d={**d,**{col:val}}
			a.append(d)
	if(len(a)):
		return jsonify(a),200
	else:
		return {},204
	

#join a ride
@app.route('/api/v1/rides/<rideId>',methods=["POST"])
def join_ride(rideId):
	un=request.get_json()["username"]
	re=requests.post("http://127.0.0.1:5051/api/v1/db/read",json={"table":"User","columns":["username"],"where":"username="+"'"+un+"'"})
	if(not re.json()):
		return {},405
	re1=requests.post("http://127.0.0.1:5051/api/v1/db/read",json={"table":"Rides","columns":["rideId"],"where":"rideId="+"'"+rideId+"'"})
	if(not re1.json()):
		return {},405
	else:
		j={"flag":"update","columns":{"username":un,"rideId":rideId},"table":"Rides"}
		a=requests.post("http://127.0.0.1:5051/api/v1/db/write",json=j)
		if(a.text=='405'):
			return {},405
	return {},200
	

#database read
@app.route("/api/v1/db/read",methods=["POST"])
def read():
	k=request.get_json()["table"]
	j=request.get_json()["columns"]
	t=request.get_json()["where"]
	if(k=="Rides"):
		new=[]
		for i in j:
			new.append(text(i))
		stmt = select(new).where(text(t)).select_from(text("Rides"))
		rs=db.engine.execute(stmt)
		d,a={},[]
		for row in rs:
			for col,val in row.items():
				d={**d,**{col:val}}
			a.append(d)
		return jsonify(a)
	elif(k=="User"):		
		new=[]
		for i in j:
			new.append(text(i))
		stmt = select(new).where(text(t)).select_from(text("User"))
		rs=db.engine.execute(stmt)
		d,a={},[]
		for row in rs:
			for col,val in row.items():
				d={**d,**{col:val}}
			a.append(d)
		return jsonify(a)

#database write
@app.route("/api/v1/db/write",methods=["POST"])
def write():
	flag=request.get_json()["flag"]
	k=request.get_json()["table"]
	if(flag=="add"):
		j=request.get_json()["insert"]
		if(k=="Rides"):
			xt=db.session.query(func.max(Rides.rideId)).first()
			i=xt[0]+1
			print(i)
			ri= Rides(i,j["created_by"],j["created_by"],j["timestamp"],j["source"],j["destination"])
			db.session.add(ri)
		elif(k=="User"):
			us = User(j["username"],j["password"])
			db.session.add(us)
	elif(flag=="delete"):
		if(k=="Rides"):
                        try:
                                rid=request.get_json()["rideId"]
                                Rides.query.filter_by(rideId=rid).delete()
                        except:
                                un=request.get_json()["username"]
                                stmt = select([text("users")]).select_from(text("Rides"))
                                rs=db.engine.execute(stmt)
                                for i in rs:
                                        b=i[0]
                                        str1=""
                                        li=b.split(',')
                                        if un in li:
                                                li.remove(un)
                                        for h in li:
                                                str1=str1+','+h
                                        str1=str1[1:]
                                        a=Rides.query.filter_by(users=b).update(dict(users=str1)) 
                                db.session.commit()      
	        
		elif(k=="User"):
			un=request.get_json()["username"]
			User.query.filter_by(username=un).delete()
				
	elif(flag=="update"):
		j=request.get_json()["columns"]
		un=j["username"]
		ri=j["rideId"]
		stmt = select([text("users")]).where(text("rideId="+"'"+ri+"'")).select_from(text("Rides"))
		rs=db.engine.execute(stmt)
		for i in rs:
			b=i[0]
		li=b.split(',')
		for h in li:
			if(h==un):
				return ('405')
		a=Rides.query.filter_by(rideId=ri).update(dict(users=b+','+un))		
	db.session.commit()
	return {}

if __name__=="__main__":
	app.debug=True
	app.run()
