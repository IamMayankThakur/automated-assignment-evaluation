from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy 
from flask_marshmallow import Marshmallow
from sqlalchemy.orm.attributes import flag_modified
import os
import re
import sys
from sqlalchemy import PickleType
import requests
from datetime import datetime
AreaEnum=list(range(1,199))

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db3.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
# Init db
db = SQLAlchemy(app)
# Init ma
marshow = Marshmallow(app)

# User Class/Model
class User(db.Model):
  userId = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String())
  password = db.Column(db.String())
 
  def __init__(self, username, password):
    self.username = username
    self.password = password

# User Schema
class UserSchema(marshow.Schema):
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
  pooling_users= db.Column(db.PickleType())

  def __init__(self, created_by, timestamp, source, destination, pooling_users=[]):
    self.created_by = created_by
    self.timestamp = timestamp
    self.source = source
    self.destination = destination
    self.pooling_users = pooling_users

# Ride Schema
class RideSchema(marshow.Schema):
  class Meta:
    fields = ('rideId','created_by','timestamp', 'source', 'destination', 'pooling_users')

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
  abra = request.json['username']
  dabra = request.json['password']
  pats_sha1=re.compile(r'\b([0-9a-f]|[0-9A-F]){40}\b')
  kiki={}
  kiki["un"]=abra
  kiki["pw"]=dabra
  kiki["meghs"]="add_user"
  redford="http://0.0.0.0:80/api/v1/db/read"
  bonkhead={'Content-type':'application/json','Accept':'text/plain'}
  road=requests.post(url=redford,json=kiki,headers=bonkhead)
  rash= road.text
  if((rash=="None") and (re.search(pats_sha1, dabra)) and len(abra)!=0):
    ryt_url=" http://0.0.0.0:80/api/v1/db/write"
    w=requests.post(url=ryt_url,json=kiki,headers=bonkhead)
    return jsonify({}), 201
  else:
    return jsonify({}), 400

#2.Delete user
@app.route('/api/v1/users/<username>', methods=['DELETE'])
def remove_user(username):
  if(request.method!= 'DELETE'):
    return jsonify({}), 405
  kiki={}
  kiki["meghs"]="remove_user"
  kiki["u_naam"]=username
  redford=" http://0.0.0.0:80/api/v1/db/read"
  bonkhead={'Content-type':'application/json','Accept':'text/plain'}
  road=requests.post(url=redford,json=kiki,headers=bonkhead)
  rash = road.text
  if(rash=="None"):
    return jsonify({}), 400
  else:
    ryt_url=" http://0.0.0.0:80/api/v1/db/write"
    witch=requests.post(url=ryt_url,json=kiki,headers=bonkhead)
    return jsonify({}), 200

#3.New ride
@app.route('/api/v1/rides', methods=['POST'])
def add_ride():
  if(request.method!= 'POST'):
    return jsonify({}), 405
  timepat=re.compile(r'\b[0-9][0-9](-)[0-9][0-9](-)[0-9][0-9][0-9][0-9](:)[0-9][0-9](-)[0-9][0-9](-)[0-9][0-9]')
  timevalid=re.compile(r'\b(?:(?:31(-)(?:0?[13578]|1[02]))\1|(?:(?:29|30)(-)(?:0?[13-9]|1[0-2])\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29(-)0?2\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])(-)(?:(?:0?[1-9])|(?:1[0-2]))\4(?:(?:1[6-9]|[2-9]\d)?\d{2})(:)([0-5][0-9])(-)([0-5][0-9])(-)([0-1][0-9]|2[0-3])\b')
  bheem = request.json['created_by']
  indu = request.json['timestamp']
  raju = request.json['source']
  chutki = request.json['destination']
  kiki={}
  kiki["creator"]=bheem
  kiki["samay"]=indu
  kiki["shuru"]=raju
  kiki["khatam"]=chutki
  kiki["meghs"]="add_ride"
  redford="http://0.0.0.0:80/api/v1/db/read"
  bonkhead={'Content-type':'application/json','Accept':'text/plain'}
  road=requests.post(url=redford,json=kiki,headers=bonkhead)
  rash= road.text
  if(rash=="None"):
    return jsonify({}), 400
  elif(int(raju) not in AreaEnum or int(chutki) not in AreaEnum or (int(raju)==int(chutki))):
    return jsonify({}), 400
  else:
    if(re.search(timepat, indu)):
      if(re.search(timevalid, indu) and len(bheem)!=0):
        ryt_url="http://0.0.0.0:80/api/v1/db/write"
        witch=requests.post(url=ryt_url,json=kiki,headers=bonkhead)
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
  kiki={}
  kiki["meghs"]="upcoming_rides"
  shuru=request.args.get('source')
  khatam=request.args.get('destination')
  kiki["shuru"]=shuru
  kiki["khatam"]=khatam
  if(int(shuru) not in AreaEnum or int(khatam) not in AreaEnum or (int(shuru)==int(khatam))):
    return jsonify({}), 400
  else:
    redford="http://0.0.0.0:80/api/v1/db/read"
    bonkhead={'Content-type':'application/json','Accept':'text/plain'}
    road=requests.post(url=redford,json=kiki,headers=bonkhead)
    rash=road.json()
    if(not bool(rash)):
      return jsonify({}), 204
    else:
      return road.text, 200


#5.Ride details
@app.route('/api/v1/rides/<rideId>', methods=['GET'])
def ride_details(rideId):
  if(request.method != 'GET'):
    return jsonify({}), 405
  kiki={}
  kiki["meghs"]="ride_details"
  kiki["rideId"]=rideId
  redford="http://0.0.0.0:80/api/v1/db/read"
  bonkhead={'Content-type':'application/json','Accept':'text/plain'}
  road=requests.post(url=redford,json=kiki,headers=bonkhead)
  rash=road.json()
  if(not bool(rash)):
    return jsonify({}), 204
  else:
    return road.text, 200

#6.Join ride 
@app.route('/api/v1/rides/<rideId>', methods=['POST'])
def join_ride(rideId):
  if(request.method!= 'POST'):
    return jsonify({}), 405
  un = request.json['username']
  kiki={}
  kiki["rideId"]=rideId
  kiki["u_name"]=un
  kiki["meghs"]="join_ride"
  redford=" http://0.0.0.0:80/api/v1/db/read"
  bonkhead={'Content-type':'application/json','Accept':'text/plain'}
  road=requests.post(url=redford,json=kiki,headers=bonkhead)
  rash = road.text
  if(rash=="False"):
    return jsonify({}), 204
  else:
    ryt_url= "http://0.0.0.0:80/api/v1/db/write"
    witch=requests.post(url=ryt_url,json=kiki,headers=bonkhead)
    #wcheck=witch.text
    if(witch.text=="None" or len(un)==0):
      return jsonify({}), 400
    else:
      return jsonify({}), 200

#7.Delete ride
@app.route('/api/v1/rides/<rideId>', methods=['DELETE'])
def delete_ride(rideId):
  if(request.method!= 'DELETE'):
    return jsonify({}), 405
  kiki={}
  kiki["meghs"]="delete_ride"
  kiki["rideId"]=rideId
  redford=" http://0.0.0.0:80/api/v1/db/read"
  bonkhead={'Content-type':'application/json','Accept':'text/plain'}
  road=requests.post(url=redford,json=kiki,headers=bonkhead)
  rash = road.text

  if(rash=="None"):
    return jsonify({}), 400
  else:
    ryt_url=" http://0.0.0.0:80/api/v1/db/write"
    witch=requests.post(url=ryt_url,json=kiki,headers=bonkhead)
    return jsonify({}), 200



#8.Write db
@app.route('/api/v1/db/write', methods=['POST'])
def write_db():
  content=request.json
  if(content["meghs"]=="add_user"):
    user=content["un"]
    pswd=content["pw"]
    new_user=User(user, pswd)
    db.session.add(new_user)
    db.session.commit()
    return user_schema.jsonify(new_user)

  elif (content["meghs"]=="remove_user"):
    user1=content["u_naam"]
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

  elif(content["meghs"]=="add_ride"):
    un=content["creator"]
    tim_stmp=content["samay"]
    sorce=content["shuru"]
    destn=content["khatam"]
    new_ride=Ride(un, tim_stmp, sorce, destn)
    db.session.add(new_ride)
    db.session.commit()
    return ride_schema.jsonify(new_ride)

  elif (content["meghs"]=="delete_ride"):
    rid_1=content["rideId"]
    #ride = Ride.query.get(ride1)
    h = Ride.query.filter_by(rideId=rid_1).first()
    db.session.delete(h)
    db.session.commit()
    return content
  
  elif(content["meghs"]=="join_ride"):
    content=request.json
    us_er=content["u_name"]
    rideId=content["rideId"]
    mm = Ride.query.filter_by(rideId=rideId).first()
    ucheck=mm.created_by
    print(ucheck)
    l=mm.pooling_users
    if ((us_er not in l) and (ucheck!=us_er)):
      l.append(us_er)
      mm.pooling_users=l
      flag_modified(mm,"pooling_users")
      db.session.merge(mm)
      db.session.flush()
      db.session.commit()
      return ride_schema.jsonify(mm)
    else:
      return "None"



#9.Read db
@app.route('/api/v1/db/read', methods=['POST'])
def read_db():
  content=request.json
  if(content["meghs"]=="add_user"):
    uer1=content["un"]
    usr = User.query.filter_by(username=uer1).first()
    return str(usr)

  elif (content["meghs"]=="remove_user"):
    content=request.json
    usr1=content["u_naam"]
    uer = User.query.filter_by(username=usr1).first()
    return str(uer)

  elif (content["meghs"]=="add_ride"):
    content=request.json
    user1=content["creator"]
    #user = Ride.query.get(user1)
    user = User.query.filter_by(username=user1).first()
    return str(user)

  elif (content["meghs"]=="upcoming_rides"):
    source1=content["shuru"]
    destination1=content["khatam"]
    '''timestamp=content["timestamp"]
    dt_string2=timestamp[:10]+" "+timestamp[11:]
    dt_value = datetime.strptime(dt_string2, '%d-%m-%Y %S-%M-%H')
    present_ts=datetime.now()'''
    r_2=Ride.query.filter(Ride.source==int(source1),Ride.destination==int(destination1)).all()
    #print(ride2)
    #print(type(ride2))
    sk=str(r_2)
    upcoming=[]
    x=map(int, re.findall(r'\d+',sk))
    z=list(x)
    if(len(z)==0):
      return ride_schema.jsonify(r_2)
    #print(list(x))
    else:
      for i in z: 
        y=Ride.query.get(i)
        tstmp=y.timestamp
        dt_string2=tstmp[:10]+" "+tstmp[11:]
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

  elif (content["meghs"]=="ride_details"):
    identi=content["rideId"]
    detls = Ride.query.get(identi)
    return ride_schema.jsonify(detls)

  elif (content["meghs"]=="delete_ride"):
    identi=content["rideId"]
    #detls=Ride.query.get(identi)
    detls = Ride.query.filter_by(rideId=identi).first()
    return str(detls)
  
  elif(content["meghs"]=="join_ride"):
    user1=content["u_name"]
    us_er = User.query.filter_by(username=user1).first()
    rid1=content["rideId"]
    rde = Ride.query.filter_by(rideId=rid1).first()
    a=str(us_er)
    b=str(rde)
    if(a!="None" and b!="None"):
    	return "True"
    else:
    	return "False"
    

# Run Server
if __name__ == '__main__':
  app.run(debug=True)