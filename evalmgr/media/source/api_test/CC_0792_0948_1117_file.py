from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy 
from flask_marshmallow import Marshmallow
from sqlalchemy.orm.attributes import flag_modified
import os
from sqlalchemy import PickleType
import requests
import re
import sys
from datetime import datetime
AreaEnum=list(range(1,199))

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db1.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
# Init db
db = SQLAlchemy(app)
# Init ma
ma = Marshmallow(app)

# User Class/Model
class User(db.Model):
  userId = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String())
  password = db.Column(db.String())
 
  def __init__(self, username, password):
    self.username = username
    self.password = password

# User Schema
class UserSchema(ma.Schema):
  class Meta:
    fields = ('username', 'password')

# Init schema
user_schema = UserSchema()
users_schema = UserSchema(many=True)

# Ride Class/Model
class Ride(db.Model):
  rideId = db.Column(db.Integer, primary_key=True)
  created_by = db.Column(db.String())
  timestamp = db.Column(db.String())
  source = db.Column(db.Integer)
  destination = db.Column(db.Integer)
  riders_list = db.Column(db.PickleType())

  def __init__(self, created_by, timestamp, source, destination, riders_list=[]):
    self.created_by = created_by
    self.timestamp = timestamp
    self.source = source
    self.destination = destination
    self.riders_list = riders_list

# Ride Schema
class RideSchema(ma.Schema):
  class Meta:
    fields = ('rideId','timestamp','created_by', 'source', 'destination', 'riders_list')

# Init schema
ride_schema = RideSchema()
rides_schema = RideSchema(many=True)

db.create_all()

#API's

#1.Add user
@app.route('/api/v1/users', methods=['PUT'])
def add_user():
  if(request.method!= 'PUT'):
    return jsonify({}), 405
  username = request.json['username']
  password = request.json['password']
  pattern=re.compile(r'\b([0-9a-f]|[0-9A-F]){40}\b')
  dic={}
  dic["username"]=username
  dic["password"]=password
  dic["some"]="add_user"
  urlr=" http://0.0.0.0:80/api/v1/db/read"
  headers={'Content-type':'application/json','Accept':'text/plain'}
  r=requests.post(url=urlr,json=dic,headers=headers)
  result= r.text
  if((result=="None") and (re.search(pattern, password)) and len(username)!=0):
    urlw=" http://0.0.0.0:80/api/v1/db/write"
    w=requests.post(url=urlw,json=dic,headers=headers)
    return jsonify({}), 201
  else:
    return jsonify({}), 400

#2.Delete user
@app.route('/api/v1/users/<username>', methods=['DELETE'])
def remove_user(username):
  if(request.method!= 'DELETE'):
    return jsonify({}), 405
  dic={}
  dic["some"]="remove_user"
  dic["username"]=username
  urlr=" http://0.0.0.0:80/api/v1/db/read"
  headers={'Content-type':'application/json','Accept':'text/plain'}
  r=requests.post(url=urlr,json=dic,headers=headers)
  result = r.text
  if(result=="None"):
    return jsonify({}), 400
  else:
    urlw=" http://0.0.0.0:80/api/v1/db/write"
    w=requests.post(url=urlw,json=dic,headers=headers)
    return jsonify({}), 200

#3.New ride
@app.route('/api/v1/rides', methods=['POST'])
def add_ride():
  if(request.method!= 'POST'):
    return jsonify({}), 405
  timepat=re.compile(r'\b[0-9][0-9](-)[0-9][0-9](-)[0-9][0-9][0-9][0-9](:)[0-9][0-9](-)[0-9][0-9](-)[0-9][0-9]')
  timevalid=re.compile(r'\b(?:(?:31(-)(?:0?[13578]|1[02]))\1|(?:(?:29|30)(-)(?:0?[13-9]|1[0-2])\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29(-)0?2\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])(-)(?:(?:0?[1-9])|(?:1[0-2]))\4(?:(?:1[6-9]|[2-9]\d)?\d{2})(:)([0-5][0-9])(-)([0-5][0-9])(-)([0-1][0-9]|2[0-3])\b')
  created_by = request.json['created_by']
  timestamp = request.json['timestamp']
  source = request.json['source']
  destination = request.json['destination']
  dic={}
  dic["created_by"]=created_by
  dic["timestamp"]=timestamp
  dic["source"]=source
  dic["destination"]=destination
  dic["some"]="add_ride"
  urlr="http://0.0.0.0:80/api/v1/db/read"
  headers={'Content-type':'application/json','Accept':'text/plain'}
  r=requests.post(url=urlr,json=dic,headers=headers)
  result= r.text
  if(result=="None"):
    return jsonify({}), 400
  elif(int(source) not in AreaEnum or int(destination) not in AreaEnum or (int(source)==int(destination))):
    return jsonify({}), 400
  else:
    if(re.search(timepat, timestamp)):
      if(re.search(timevalid, timestamp) and len(created_by)!=0):
        urlw="http://0.0.0.0:80/api/v1/db/write"
        w=requests.post(url=urlw,json=dic,headers=headers)
        return jsonify({}), 201
      else:
        return jsonify({}), 400
    else:
      return jsonify({}), 400


#4.upcoming rides
@app.route('/api/v1/rides', methods=['GET'])
def upcoming_rides():
  if(request.method != 'GET'):
    return jsonify({}), 405
  dic={}
  dic["some"]="upcoming_rides"
  s=request.args.get('source')
  d=request.args.get('destination')
  dic["s"]=s
  dic["d"]=d
  if(int(s) not in AreaEnum or int(d) not in AreaEnum or (int(s)==int(d))):
    return jsonify({}), 400
  else:
    urlr=" http://0.0.0.0:80/api/v1/db/read"
    headers={'Content-type':'application/json','Accept':'text/plain'}
    r=requests.post(url=urlr,json=dic,headers=headers)
    result=r.json()
    if(not bool(result)):
      return jsonify({}), 204
    else:
      return r.text, 200


#5.Ride details
@app.route('/api/v1/rides/<rideId>', methods=['GET'])
def ride_details(rideId):
  if(request.method != 'GET'):
    return jsonify({}), 405
  dic={}
  dic["some"]="ride_details"
  dic["rideId"]=rideId
  urlr=" http://0.0.0.0:80/api/v1/db/read"
  headers={'Content-type':'application/json','Accept':'text/plain'}
  r=requests.post(url=urlr,json=dic,headers=headers)
  result=r.json()
  if(not bool(result)):
    return jsonify({}), 204
  else:
    return r.text, 200

#6.Join ride 
@app.route('/api/v1/rides/<rideId>', methods=['POST'])
def join_ride(rideId):
  if(request.method!= 'POST'):
    return jsonify({}), 405
  username = request.json['username']
  dic={}
  dic["rideId"]=rideId
  dic["username"]=username
  dic["some"]="join_ride"
  urlr=" http://0.0.0.0:80/api/v1/db/read"
  headers={'Content-type':'application/json','Accept':'text/plain'}
  r=requests.post(url=urlr,json=dic,headers=headers)
  result = r.text
  if(result=="False"):
    return jsonify({}), 204
  else:
    urlw= "http://0.0.0.0:80/api/v1/db/write"
    w=requests.post(url=urlw,json=dic,headers=headers)
    wcheck=w.text
    if(w.text=="None" or len(username)==0):
      return jsonify({}), 400
    else:
      return jsonify({}), 200

#7.Delete ride
@app.route('/api/v1/rides/<rideId>', methods=['DELETE'])
def delete_ride(rideId):
  if(request.method!= 'DELETE'):
    return jsonify({}), 405
  dic={}
  dic["some"]="delete_ride"
  dic["rideId"]=rideId
  urlr=" http://0.0.0.0:80/api/v1/db/read"
  headers={'Content-type':'application/json','Accept':'text/plain'}
  r=requests.post(url=urlr,json=dic,headers=headers)
  result = r.text

  if(result=="None"):
    return jsonify({}), 400
  else:
    urlw=" http://0.0.0.0:80/api/v1/db/write"
    w=requests.post(url=urlw,json=dic,headers=headers)
    return jsonify({}), 200



#8.Write db
@app.route('/api/v1/db/write', methods=['POST'])
def write_db():
  content=request.json
  if(content["some"]=="add_user"):
    user=content["username"]
    pswd=content["password"]
    new_user=User(user, pswd)
    db.session.add(new_user)
    db.session.commit()
    return user_schema.jsonify(new_user)

  elif (content["some"]=="remove_user"):
    user1=content["username"]
    #user = User.query.get(user1)
    ride=Ride.query.filter_by(created_by=user1).all()
    sk=str(ride)
    x=map(int, re.findall(r'\d+',sk))
    z=list(x)
    for i in z:
      print(i)
      y=Ride.query.get(i)
      db.session.delete(y)
      db.session.commit()
    user = User.query.filter_by(username=user1).first()
    db.session.delete(user)
    db.session.commit()
    '''ride1=Ride.query.filter_by(user1 in Ride.riders_list).all()
    print(ride1)'''
    return content
    #the next created rideid starts from 23
    #existingusers-meghs
    #source and desti=4 and 5, 4 and 6

  elif(content["some"]=="add_ride"):
    user=content["created_by"]
    ts=content["timestamp"]
    src=content["source"]
    dst=content["destination"]
    new_ride=Ride(user, ts, src, dst )
    db.session.add(new_ride)
    db.session.commit()
    return ride_schema.jsonify(new_ride)

  elif (content["some"]=="delete_ride"):
    ride1=content["rideId"]
    #ride = Ride.query.get(ride1)
    ride = Ride.query.filter_by(rideId=ride1).first()
    db.session.delete(ride)
    db.session.commit()
    return content
  
  elif(content["some"]=="join_ride"):
    content=request.json
    user=content["username"]
    rideId=content["rideId"]
    ride = Ride.query.filter_by(rideId=rideId).first()
    ucheck=ride.created_by
    print(ucheck)
    l=ride.riders_list
    if ((user not in l) and (ucheck!=user)):
      l.append(user)
      ride.riders_list=l
      flag_modified(ride,"riders_list")
      db.session.merge(ride)
      db.session.flush()
      db.session.commit()
      return ride_schema.jsonify(ride)
    else:
      return "None"



#9.Read db
@app.route('/api/v1/db/read', methods=['POST'])
def read_db():
  content=request.json
  if(content["some"]=="add_user"):
    user1=content["username"]
    user = User.query.filter_by(username=user1).first()
    return str(user)

  elif (content["some"]=="remove_user"):
    content=request.json
    user1=content["username"]
    user = User.query.filter_by(username=user1).first()
    return str(user)

  elif (content["some"]=="add_ride"):
    content=request.json
    user1=content["created_by"]
    #user = Ride.query.get(user1)
    user = User.query.filter_by(username=user1).first()
    return str(user)

  elif (content["some"]=="upcoming_rides"):
    source1=content["s"]
    destination1=content["d"]
    '''timestamp=content["timestamp"]
    dt_string2=timestamp[:10]+" "+timestamp[11:]
    dt_value = datetime.strptime(dt_string2, '%d-%m-%Y %S-%M-%H')
    present_ts=datetime.now()'''
    ride2=Ride.query.filter(Ride.source==int(source1),Ride.destination==int(destination1)).all()
    #print(ride2)
    #print(type(ride2))

    sk=str(ride2)
    upcoming=[]
    x=map(int, re.findall(r'\d+',sk))
    z=list(x)
    if(len(z)==0):
      return ride_schema.jsonify(ride2)
    #print(list(x))
    else:
      for i in z: 
        y=Ride.query.get(i)
        tstamp=y.timestamp
        dt_string2=tstamp[:10]+" "+tstamp[11:]
        dt_value = datetime.strptime(dt_string2, '%d-%m-%Y %S-%M-%H')
        present_ts=datetime.now()
        user1=y.created_by
        ucheck=User.query.filter_by(username=user1).first()
        if(str(ucheck)=="None"):
          pass
        elif(dt_value>present_ts):
          lol={}
          lol["rideId"]=y.rideId
          lol["username"]=y.created_by
          lol["timestamp"]=y.timestamp
          upcoming.append(lol)
      if(len(upcoming)==0):
          return "None"
      else:
        return jsonify(upcoming)

  elif (content["some"]=="ride_details"):
    ride1=content["rideId"]
    ride = Ride.query.get(ride1)
    return ride_schema.jsonify(ride)

  elif (content["some"]=="delete_ride"):
    ride1=content["rideId"]
    #ride=Ride.query.get(ride1)
    ride = Ride.query.filter_by(rideId=ride1).first()
    return str(ride)
  
  elif(content["some"]=="join_ride"):
    user1=content["username"]
    user = User.query.filter_by(username=user1).first()
    ride1=content["rideId"]
    ride = Ride.query.filter_by(rideId=ride1).first()
    a=str(user)
    b=str(ride)
    if(a!="None" and b!="None"):
    	return "True"
    else:
    	return "False"
    

# Run Server
if __name__ == '__main__':
  app.run(debug=True)

