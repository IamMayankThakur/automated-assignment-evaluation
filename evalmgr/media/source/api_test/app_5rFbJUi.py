import json
from datetime import datetime
import time
import re
import enum
import csv
from flask import Flask,request,jsonify,Response
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY']='HELLOWORLD'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///ride.db'
debug=False
ALLOWED_HOST = ["*"]

db = SQLAlchemy(app)
res = app.test_client()
# TABLES
class User(db.Model):
	username = db.Column(db.String(),primary_key=True,unique=True)
	password = db.Column(db.String(40))
class RideShare(db.Model):
	rideId = db.Column(db.Integer(),primary_key=True,unique=True,autoincrement=True)
	username = db.Column(db.String())
	timestamp = db.Column(db.String())
	# users = db.Column(db.String(),default="[]")
	source = db.Column(db.Integer())
	destination = db.Column(db.Integer())
class RideShare_User(db.Model):
	Id = db.Column(db.Integer(),primary_key=True,unique=True,autoincrement=True)
	rideId = db.Column(db.Integer())
	users = db.Column(db.String(),default="")


#FUNCTIONS:::::


# Joining new user in the existing list
def users_list(users,new_user):
   #(eg: users=['c'] , new_user='b', u=['c','b'])
    user = ""
    u=[]
    for i in range(len(users)):
        if users[i] in ('[',']','\'',' '):
            continue
        else:
            user = user+users[i]
    if user=="":
        u.append(new_user)
    else:
        u= user.split(',')
        u.append(new_user)
    return str(u)

# Validation of date :::
def valid_date(timedate):
    dt=datetime.now()
    current=dt.strftime("%d-%m-%Y:%S-%M-%H")
    pattern = '%d-%m-%Y:%S-%M-%H'
    epoch1 = int(time.mktime(time.strptime(current, pattern)))
    epoch2 = int(time.mktime(time.strptime(timedate, pattern)))
    if epoch1<epoch2:
        return 1
    else:
        return 0


# REST API'S
#example
#get all the users and there password present
@app.route('/api/v1/users')
def get_all_users():
    tableName='User'
    func_Name='get_all_users'
    user={"tableName":tableName,"func_Name":func_Name}
    get_user=res.post('http://127.0.0.1:5000/api/v1/db/read',json=user)
    return get_user

#----------TASK 1:-------
#create an user and add in db
@app.route('/api/v1/users', methods=['PUT','POST'])
def create_user():
    if request.method not in ['PUT']:
        return {},405
    data = request.get_json()
    l=[]
    for i in data.keys():
        l.append(i)
    if l!=['username','password']:
            return {},400
    username=data['username']
    password=data['password']

    user = User.query.filter_by(username=username).first()
    print(user)
    if user:
        return {},400
    tableName='User'
    func_Name='create_user'
    new_user={"tableName":tableName,"func_Name":func_Name,"username":username,"password":password}
    password=password
    x=re.search("^[0-9a-fA-F]{40}$",password)
    if not(x):
        return {},400
    s=res.post("http://127.0.0.1:5000/api/v1/db/write",json=new_user)
    
    return {},201


#----------TASK 2:-------
#Remove the existing user
@app.route('/api/v1/users/{username}', methods=['DELETE','PUT','POST'])
def delete_user(username):
    if request.method not in ['DELETE']:
        return {},405
    tableName='User'
    func_Name='delete_user'
    delete_user=User.query.filter_by(username=username).first()
    if delete_user==None:
        return {},400
    new_user={"tableName":tableName,"func_Name":func_Name,"username":username}
    s=res.post("http://127.0.0.1:5000/api/v1/db/write",json=new_user)
    return {},200


#----------TASK 3:-------
# Create a new ride::
@app.route('/api/v1/rides', methods=['POST'])
def create_ride():
    if request.method not in ['POST']:
        return {},405
    data = request.get_json()
    l=[]
    for i in data.keys():
        l.append(i)
    if l!=['created_by','timestamp','source','destination']:
            return {},400
    tableName='RideShare'
    func_Name='create_ride'
    new_ride = RideShare(username=data['created_by'],timestamp=data['timestamp'],source=data['source'],destination=data['destination'])
    timedate=new_ride.timestamp

    y=re.search("[0-3]\d-[0-1]\d-\d\d\d\d:[0-6]\d-[0-6]\d-([0-1][0-9]|2[0-4])",timedate)

    if not(y):
        return {},400

    vd=valid_date(timedate)

    if vd==0:
        return {},400

    users=new_ride.username
    user = User.query.filter_by(username=users).first()

    if not user:
        return {},400

    new_ride_json={"tableName":tableName,"func_Name":func_Name,"username":new_ride.username,"timestamp":new_ride.timestamp,"source":new_ride.source,"destination":new_ride.destination}

    s=res.post("http://127.0.0.1:5000/api/v1/db/write",json=new_ride_json)
    return { },201

# EXAMPLE::
# Get all the rides of the db
@app.route('/ride', methods=['GET'])
def get_all_rides():
    tableName='RideShare'
    func_Name='get_all_rides'
    get_ride={"tableName":tableName,"func_Name":func_Name}
    rides=res.post("http://127.0.0.1:5000/api/v1/db/read",json=get_ride)
    return rides

#----------TASK 4:-------
# List all upcoming rides for a given source and destination
@app.route('/api/v1/rides?source={source}&destination={destination}', methods=['GET'])
def get_specific_ride(source,destination):

    tableName='RideShare'
    func_Name='get_specific_ride'

    get_ride={"tableName":tableName,"func_Name":func_Name,"source":source,"destination":destination}
    rides=res.post("http://127.0.0.1:5000/api/v1/db/read",json=get_ride)
    return rides


#----------TASK 5:-------
# List all the details of a given ride
@app.route('/api/v1/rides/{rideId}', methods=['GET'])
def ride_details(rideId):
    tableName='RideShare'
    func_Name='ride_details'
    get_ride={"tableName":tableName,"func_Name":func_Name,"rideId":rideId}

    rides=res.post("http://127.0.0.1:5000/api/v1/db/read",json=get_ride)
    return rides

#----------TASK 6:-------
# Joining the existing ride
@app.route('/api/v1/rides/{rideId}', methods=['POST'])
def join_ride(rideId):
    tableName='RideShare_User'
    func_Name='join_ride'
    data = request.get_json()
    append_user={"tableName":tableName,"func_Name":func_Name,"rideId":rideId,"username":data['username']}

    rides=res.post("http://127.0.0.1:5000/api/v1/db/write",json=append_user)
    return rides


#----------TASK 7:-------
# Delete the ride
@app.route('/api/v1/rides/{rideId}', methods=['DELETE'])
def delete_ride(rideId):
    tableName='RideShare'
    method='DELETE'
    delete_ride={"tableName":tableName,"func_Name":"delete_ride","rideId":rideId}
    s=res.post("http://127.0.0.1:5000/api/v1/db/write",json=delete_ride)
    return {},200


#----------TASK 8:-------
#Write to db
@app.route('/api/v1/db/write', methods=['POST'])
def write_to_db():
    data=request.get_json()
    tableName=data["tableName"]
    X=eval(tableName)
    func_Name=data['func_Name']
    #1. Add user
    if tableName=='User' and func_Name=='create_user':
        
        new_user=X(username=data['username'],password=data['password'])
        db.session.add(new_user)
        db.session.commit()
        return "done"
    #2. Remove user
    if tableName=='User' and func_Name=='delete_user':
        username=data['username']
        X=eval(tableName)
        delete_user=User.query.filter_by(username=username).first()
        db.session.delete(delete_user)
        db.session.commit()
        return "done"

    #3. Create a new ride
    if tableName=='RideShare' and func_Name=='create_ride':
        X=eval(tableName)
        new_ride=X(username=data['username'],timestamp=data['timestamp'],source=data['source'],destination=data['destination'])
        
        db.session.add(new_ride)
        db.session.commit()
        return "done"


     #6. Join an existing ride
    if tableName=='RideShare_User' and func_Name=='join_ride':
        rideId=data['rideId']
        append_username=data['username']

        created_by = RideShare.query.filter_by(rideId=rideId).first()
        created_by_user=created_by.username
        if append_username==created_by_user:
            return {},400

        validate_user = User.query.filter_by(username=append_username).first()
        if not validate_user:
            return {},400
        validate_rideId=RideShare.query.filter_by(rideId=rideId).first()
        if not validate_rideId:
            return {},400

        rideShares=RideShare_User.query.filter_by(rideId=rideId)
        users=[i.users for i in rideShares]

        if append_username in users:
            return {},400

        new_ride=X(rideId=data['rideId'],users=append_username)
        db.session.add(new_ride)
        db.session.commit()
        return {},200


    #7. Delete a ride
    if tableName=='RideShare' and func_Name=='delete_ride':
        X=eval(tableName)
        rideId=data['rideId']
        ride = RideShare.query.filter_by(rideId=rideId).first()
        if not ride:
            return {},400
        db.session.delete(ride)
        db.session.commit()
        return "done"


#----------TASK 9:-------
#Read from db
@app.route('/api/v1/db/read', methods=['POST'])
def read_to_db():
    data=request.get_json()
    tableName=data['tableName']
    func_Name=data['func_Name']
    X=eval(tableName)

    #example to get all users
    if tableName=='User' and func_Name=='get_all_users':
        users = X.query.all()
        output = []
        for user in users:
            user_data={}
            user_data["username"] = user.username
            user_data["password"] = user.password
            output.append(user_data)
        return jsonify({'users':output})

    # example to get all rides
    if tableName=='RideShare' and func_Name=='get_all_rides':
        rides = X.query.all()
        output = []
        for ride in rides:
            ride_data={}
            ride_data["rideId"] = ride.rideId
            ride_data["username"] = ride.username
            ride_data["timestamp"]=ride.timestamp
            ride_data["source"] = ride.source
            ride_data["destination"] = ride.destination
            output.append(ride_data)
        return jsonify({'rides':output})

     #4. List all upcoming rides for a given source and destination
    if tableName=='RideShare' and func_Name=='get_specific_ride':
        source=data['source']
        destination=data['destination']
        if int(source)>198 or int(source)<1:
            return {},400
        if int(destination)>198 or int(destination)<1:
            return {},400
        rides = X.query.filter_by(source=source,destination=destination).all()
        output=[]
        for ride in rides:
            timedate=ride.timestamp
            vd=valid_date(timedate)
            
            if vd==1:

                ride_data={}
                ride_data['rideId']=ride.rideId
                ride_data['username']=ride.username
                ride_data['timestamp']=ride.timestamp

                output.append(ride_data)

        return jsonify({"rides":output})

     # 5. List all the details of a given ride
    if tableName=='RideShare' and func_Name=='ride_details':
        rideId=data['rideId']
        rides = X.query.filter_by(rideId=rideId).all()
        rideShares=RideShare_User.query.filter_by(rideId=rideId)
        users=[i.users for i in rideShares]
        output=[]
        if not rides:
            return {},400
        for ride in rides:
            ride_data={}
            ride_data['rideId']=ride.rideId
            ride_data['created_by']=ride.username
            ride_data['users']=users
            ride_data['timestamp']=ride.timestamp
            ride_data['source']=ride.source
            ride_data['destination']=ride.destination
            output.append(ride_data)
        return jsonify({"rides":output})
    


if __name__=='__main__':
     app.run(debug=True)
