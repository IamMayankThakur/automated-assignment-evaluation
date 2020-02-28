from flask import Flask, request, flash, url_for, redirect, render_template  , jsonify,json,abort,Response
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt
from datetime import datetime
import pandas as pd
import re
import requests

app = Flask(__name__)  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///RS2.sqlite3'  
app.config['SECRET_KEY'] = "secret key"  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)  

class Users(db.Model):
	ID=db.Column(db.Integer, primary_key = True)
	uname=db.Column(db.String(100),unique=True)
	Password=db.Column(db.String(40))
	
class Ride(db.Model):
	RideID=db.Column(db.Integer, primary_key = True)
	created_by=db.Column(db.String(100))
	timestamp=db.Column(db.String,nullable=False,default=(datetime.now()).strftime("%d-%m-%Y:%S:%M:%H"))
	source=db.Column(db.Integer)
	destination=db.Column(db.Integer)
	def serialize(self):	
		return{
			"rideId":self.RideID,
			"username":self.created_by,
			"timestamp":self.timestamp
		}
def search(source,destination):
	df=pd.read_csv('AreaNameEnum.csv')
	if int(source) in list(df['Area No']) and int(destination) in list(df['Area No']):
		return 1
	else:
		return 0
@app.route('/api/v1/users',methods=['PUT'])
def adduser():
	if(request.method=="PUT"):
		a=request.json.get('username')
		b=request.json.get('password')
		
		if (Users.query.filter_by(uname=a,Password=b).count() < 1):
			insert_data=str(str(a)+';'+str(b))
			dr={'insert':str(insert_data),'op':'A'}
			requests.post('http://localhost:5000/api/v1/db/write',json=dr)
			return Response(json.dumps(dict()),status=200)# Call write db

		else:
			return abort(400 ,description="User already exists!")
	else:
		return abort(405 ,description="Method doesnot support!")
@app.route('/api/v1/rides',methods=['POST','GET'])
def addride():
	if(request.method=="POST"):
		a=request.json.get('created_by')
		#b=request.json.get('timestamp')
		c=request.json.get('source')
		d=request.json.get('destination')
		if (Users.query.filter_by(uname=a).count() >= 1 and search(c,d)):
			insert_data=str(a)+';'+str(c)+';'+str(d)
			dr={'table':'Ride','insert':str(insert_data),'op':'C'}
			requests.post('http://localhost:5000/api/v1/db/write',json=dr)
			return Response(json.dumps(dict()),status=200)
		else:
			return abort(400 ,description="Username doesnot exist!Please register as user!")
	elif(request.method=="GET"):
		source=request.args.get('source')
		destination=request.args.get('destination')
		if (search(source,destination)==1): #call a function to search for valid src and dst 
			insert_data=str(source)+';'+str(destination)
			dr={'table':'Ride','insert':str(insert_data),'op':'F'}
			res=requests.post('http://localhost:5000/api/v1/db/read',json=dr)
			return Response(res,status=200)
			
		#print(Users.query.filter_by(uname=a).count())
			return jsonify(l)
		else:
			return abort(400 ,description="Source or destination is not found!")
	
	else:
		return abort(405 ,description="Method doesnot support!")
	
@app.route('/api/v1/users/<username>',methods=['DELETE'])
def removeUsers(username):
	if(request.method=="DELETE"):
		if (Users.query.filter_by(uname=username).count() >= 1):
			remove_data=str(username)
			dr={'table':'Users','delete':str(remove_data),'op':'B'}
			requests.post('http://localhost:5000/api/v1/db/write',json=dr)
			return Response(json.dumps(dict()),status=200)
		else:
			return abort(400 ,description="User doesnot exist!!")
	else:
		return abort(405 ,description="Method doesnot support!")
@app.route('/api/v1/rides/<rideId>',methods=['DELETE','GET','POST'])
def removeRides(rideId):
	if(request.method=="DELETE"):
		if (Ride.query.filter_by(RideID=rideId).count() >= 1):
			#remove_data=str(username)
			dr={'table':'Ride','delete':rideId,'op':'D'}
			requests.post('http://localhost:5000/api/v1/db/write',json=dr)
			return Response(json.dumps(dict()),status=200)
		else:
			return abort(400 ,description="Ride doesnot exist!!")
	elif(request.method=="GET"):
		if (Ride.query.filter_by(RideID=rideId).count() >= 1):
			dr={'table':'Ride','show':rideId,'op':'E'}
			res=requests.post('http://localhost:5000/api/v1/db/read',json=dr)
			return Response(res,status=200)
		else:
			return abort(400 ,description="Ride doesnot exist!")
	elif(request.method=="POST"):
		if Ride.query.filter_by(RideID=rideId).count() >= 1:
			a=request.json.get('username')
			insert_data=str(a)
			dr={'table':'Ride','join':str(insert_data),'RI':rideId,'op':'G'}
			res=requests.post('http://localhost:5000/api/v1/db/write',json=dr)
			return Response(json.dumps(dict()),status=200)
		else:
			return abort(400 ,description="Ride doesnot exist!")
	else:
		return abort(405 ,description="Method doesnot support!")		
@app.route('/api/v1/db/write',methods=['POST'])
def write_db():
	a=request.json.get('op')
	if(a=='A'):
		b=request.json.get('insert')
		c=b.split(';')
		#u=str(request.json.get('insert_data'))
		u=Users(uname=c[0],Password=c[1])
		db.session.add(u)
		db.session.commit()
		return jsonify()
	if(a=='C'):
		data=request.json.get('insert')
		c,e,f=data.split(';')
		u=Ride(created_by=c,timestamp=(datetime.now()).strftime("%d-%m-%Y:%S:%M:%H"),source=e,destination=f)
		db.session.add(u)
		db.session.commit()
		return jsonify()
	if(a=='B'):
		data=request.json.get('delete')
		#table=request.json.get('table')
		Users.query.filter_by(uname=str(data)).delete()
		db.session.commit()
		return jsonify()
	if(a=='D'):
		data=request.json.get('delete')
		#table=request.json.get('table')
		Ride.query.filter_by(RideID=data).delete()
		db.session.commit()
		return jsonify()
	if(a=='G'):
		df=request.json.get('join')
		ri=request.json.get('RI')
		#table=request.json.get('table')
		data=Ride.query.filter_by(RideID=ri).first()
		src=data.source
		f=data.destination
		u=Ride(created_by=df,timestamp=(datetime.now()).strftime("%d-%m-%Y:%S:%M:%H"),source=src,destination=f)
		db.session.add(u)
		db.session.commit()
		return jsonify()
@app.route('/api/v1/db/read',methods=['POST'])
def read_db():
	a=request.json.get('op')
	if(a=='E'):
			ri=request.json.get('show')
			data=Ride.query.filter_by(RideID=ri).first()
			src=data.source
			b=data.destination
			data1=Ride.query.filter_by(source=src , destination=b)
			#db.session.commit()
			#return jsonify()"rideId":self.RideID,
			l=[d.created_by for d in data1]
			
			#print(Users.query.filter_by(uname=username).count())
			
			return jsonify(
			{"rideId":data.RideID,
			"username":data.created_by,
			"users" : l,
			"timestamp":data.timestamp,
			"source" : data.source,
			"destination" : data.destination})
	if(a=='F'):
			b=request.json.get('insert')
			c=b.split(';')
			ride=Ride.query.filter_by(source=c[0] , destination=c[1])#timestamp=b,
			l=[r.serialize() for r in ride]	
			return jsonify(l)
if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
		

