import os
from flask import Flask, request, jsonify, make_response
from flask import render_template, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
#import jwt
import datetime
from functools import wraps
from sqlalchemy import Column, Integer, DateTime
import re
import requests
import json
import pandas as pd

df=pd.read_csv("AreaNameEnum.csv")
d=dict(zip(df['Area No'],df['Area Name']))
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
res=app.test_client()
app.config['SECRET_KEY'] = 'thisissecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'tutorial.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
headers={"Content-Type":"application/json"}
class MyDateTime(db.TypeDecorator):
    impl = db.DateTime
    def process_bind_param(self, value, dialect):
        if type(value) is str:
            return datetime.datetime.strptime(value, '%d-%m-%Y:%S-%M-%H')
        return value
#CREATING USER
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(80))

#CREATING RIDER
class Rider(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_by = db.Column(db.String(50))
    timestamp = db.Column(MyDateTime, default=datetime.datetime.now)
    source = db.Column(db.Integer)
    destination = db.Column(db.Integer)

class Shared(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ride_id = db.Column(db.Integer)
    shared_by = db.Column(db.String(50))

#API:1
@app.route('/api/v1/users', methods=['PUT'])
def create_user():
    data = request.get_json()
    if db.session.query(User).filter_by(name=data['name']).count():
        abort(405)
    pattern = re.compile(r'\b[0-9a-f]{40}\b')
    if(bool(pattern.match(data['password']))!=True):
        abort(405)
    print(data["name"])
    requests.post("http://127.0.0.1:4010/api/v1/db/write", json={"api":"1","name":data['name'],"password":data['password']},headers=headers)
    return {},201

#API:2
@app.route('/api/v1/users/<string:username>', methods=['DELETE'])
def remove_user(username):
    if db.session.query(User).filter_by(name=username).count():
        requests.post("http://127.0.0.1:4010/api/v1/db/write", json ={"api":"2","name":username})
        return {},200
    else:
        abort(405)

#API:3
@app.route('/api/v1/rides', methods=['POST'])
def create_rider():
    data = request.get_json()
    if request.method == 'POST':
        if db.session.query(User).filter_by(name=data['created_by']).count():
            requests.post("http://127.0.0.1:4010/api/v1/db/write", json ={"api":"3","created_by":data['created_by'], "timestamp":data['timestamp'], "source":data['source'], "destination":data['destination']},headers=headers)
            return {},201
    else:
        abort(405)

#API:4
@app.route('/api/v1/rides?source=<int:source>&destination=<int:destination>', methods=['GET'])
def upcoming_rides():
	read_data = requests.post('http://127.0.0.1:4010/api/v1/db/read',json={"api":"4"})
	read_data = read_data.json()
	upcoming = []
	current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	current_time = datetime.now().strptime(current_time,"%Y-%m-%d %H:%M:%S")
	for i in range(len(read_data["created_by"])):
		time1 = datetime.strptime(read_data['timestamp'][i],"%a, %d %b %Y %H:%M:%S %Z" )
		if(source == read_data['source'][i] and destination == read_data['destination'][i] and time1>current_time):
			time1 = datetime.strptime(read_data['timestamp'][i],"%a, %d %b %Y %H:%M:%S %Z" )
			time = datetime.strftime(time1,"%d-%m-%Y:%S-%M-%H")
			upcoming.append({"rideId":read_data['rideId'][i],"username":read_data['created_by'][i],"timestamp":time})
	if(len(upcoming)!=0):
		return jsonify(upcoming),200
	elif(len(upcoming)==0):
		return {},204
	else:
		abort(400)
    #else:
    #abort(405)


#API:5,6,7
@app.route('/api/v1/rides/<int:ride_id>',methods=['GET','DELETE','POST'])
def list_ride(ride_id):
    if request.method == 'GET':
        if db.session.query(Rider).filter_by(id=ride_id).count():
            r=requests.post("http://127.0.0.1:4010/api/v1/db/read", json ={"api":"5","ride_id":ride_id},headers=headers)
            return r.json(),200
        else:
            return {},204
    elif request.method == 'POST':
        if db.session.query(Rider).filter_by(id=ride_id).count() and db.session.query(User).filter_by(name=request.get_json()['username']).one():
            requests.post("http://127.0.0.1:4010/api/v1/db/write", json ={"api":"6","ride_id":ride_id,"shared_by":request.get_json()['username']},headers=headers)
            return {},201
        else:
            return {},204
    elif request.method == 'DELETE':
        if db.session.query(Rider).filter_by(id=ride_id).count():
            return {},200
    else:
        abort(405)

#API:8
@app.route('/api/v1/db/write', methods=['POST'])
def write_db():
    data = request.get_json()
    if(data['api']=="1"):
        new_user = User( name=data['name'], password=data['password'])
        db.session.add(new_user)
        db.session.commit()
    if(data['api']=="2"):
        user_delete= db.session.query(User).filter_by(name=data['name']).one()
        db.session.delete(user_delete)
        db.session.commit()
    if(data['api']=="3"):
        new_rider= Rider( created_by=data['created_by'], timestamp=data['timestamp'], source=data['source'], destination=data['destination'])
        db.session.add(new_rider)
        db.session.commit()
    if(data['api']=="6"):
        new_shared = Shared(ride_id=data['ride_id'],shared_by=data['shared_by'])
        db.session.add(new_shared)
        db.session.commit()
    if(data['api']=="7"):
        rider_delete= db.session.query(Rider).filter_by(id=data['ride_id']).one()
        db.session.delete(rider_delete)
        db.session.commit()

@app.route('/api/v1/db/read', methods=['POST'])
def read_db():
    data = request.get_json()
    if(data['api']=="4"):
        read_data = db.session.query(Rider).all()
        ride_data = dict()
        ride_data['rideId'] = []
        ride_data['created_by'] = []
        ride_data['timestamp'] = []
        ride_data['source'] = []
        ride_data['destination'] = []
        for ride in read_data:
        	ride_data['rideId'].append(ride.id)
        	ride_data['created_by'].append(ride.created_by)
        	ride_data['timestamp'].append(ride.timestamp)
        	ride_data['source'].append(ride.source)
        	ride_data['destination'].append(ride.destination)
        return ride_data
    if(data['api']=="5"):
        ride = db.session.query(Rider).filter_by(id=data['ride_id']).one()
        shared = db.session.query(Shared).filter_by(ride_id=data['ride_id']).all()
        l=[]
        for share in shared:
            l.append(share.shared_by)
        return jsonify(ride_Id=ride.id,Created_by=ride.created_by,users=l,Timestamp=ride.timestamp,source=d[ride.source],destination=d[ride.destination])

@app.route('/test', methods=['GET'])
def test():
	return "hello"

if __name__ == '__main__':
    app.run(host='54.166.240.133',port=80,debug=False)
