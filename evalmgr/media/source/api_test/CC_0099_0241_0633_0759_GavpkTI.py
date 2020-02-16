import flask
from flask import Flask, render_template,jsonify,request,abort,Response
from flask_sqlalchemy import SQLAlchemy
import requests
import json
from area import *
from datetime import datetime
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/userride.db'
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'user'
    username = db.Column(db.String(80), primary_key = True)
    password = db.Column(db.String(40), unique = False, nullable = False)

class Ride(db.Model):
    __tablename__ = 'ride'
    ride_id = db.Column(db.Integer, primary_key = True)
    source = db.Column(db.Integer, nullable = False)
    destination = db.Column(db.Integer, nullable = False)
    timestamp = db.Column(db.String(80), unique = False, nullable = False)
    creator_name = db.Column(db.String(80), db.ForeignKey('user.username'), nullable = False)

class Users_and_Rides(db.Model):
    __tablename__ = 'users_and_rides'
    id = db.Column(db.Integer, primary_key = True)
    ride_id = db.Column(db.Integer, db.ForeignKey('ride.ride_id'), nullable = False)
    username = db.Column(db.String(80), db.ForeignKey('user.username'), nullable = False)


db.create_all()

tv = re.compile(r'\d{2}-\d{2}-\d{4}:\d{2}-\d{2}-\d{2}')
hex_digits = ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f']
url_read = 'http://127.0.0.1:80/api/v1/db/read'
url_write = 'http://127.0.0.1:80/api/v1/db/write'


def validate_password(password):
    if( len(password) != 40):
        return False
    else:
        for i in password:
            j = i.lower()
            if j not in hex_digits:
                return False
        return True        


@app.route('/api/v1/users',methods=['PUT'])
def add_user():
    try:
        data = flask.request.json
        user_name = data["username"]
        password = data["password"]

        user_dict = { "table" : "user", "method": "PUT", "username": user_name }
        user_json = json.dumps(user_dict)

        user_results = requests.post(url_read,json = user_json)
        user_results = json.loads(user_results.text)

        if user_results['empty'] == 1:
            resu = True
        else:
            resu = False
        resp = validate_password(password)

        if resu and resp:
            user_dict = { "table" : "user", "method" : "PUT", "username" : user_name , "password" : password}
            user_json = json.dumps(user_dict)

            requests.post(url_write,json = user_json)
            # Correct code
            return Response(json.dumps({}),status = 201)

        else:
            if not resu:
                #Correct code
                return Response("Username already exists",status = 400)
            else:
                #Correct code
                return Response("Password is not allowed",status = 400)
    
    except:
        return Response("Error while providing data",status = 400)
    

@app.route('/api/v1/users/<username>',methods=['DELETE'])
def remove_user(username):
    try:
        user_dict = {"table" : "user", "method" : "DELETE", "username" : username}
        user_json = json.dumps(user_dict)

        user_results = requests.post(url_read,json = user_json)
        user_results = json.loads(user_results.text)

        if user_results['empty'] == 1:
            #Correct code
            return Response("No such user exists",status = 400)
        
        else:
            if user_results['rides_created']:
                # Correct code
                return Response("User is associated with ride, cant be deleted",status = 400)

            else:
                user_dict = { "table" : "user", "method" : "DELETE", "username" : username}
                user_json = json.dumps(user_dict)
                requests.post(url_write,json = user_json)
                #Correct code
                return Response(json.dumps({}),status = 200)
    
    except:
        return Response(status = 400)



@app.route('/api/v1/rides',methods=['POST'])
def new_ride():
    try:
        data = flask.request.json
        id_creator = data['created_by']
        timestamp = data['timestamp']
        source = data['source']
        dest = data['destination']

        if not tv.match(timestamp):
            #Correct code
            return Response("Timestamp entered in invalid format",status = 400)
        
        now = datetime.now()

        ride_date = datetime.strptime(timestamp, '%d-%m-%Y:%S-%M-%H')
        if ride_date < now:
            #Correct code
            return Response("Can't creade ride with a timestamp that has already passed",status = 400)
        
        if source == dest:
            #Correct code
            return Response("Source and destination are same",status = 400)

        if(source not in areas.keys() or dest not in areas.keys()):
            ressd = False
        else:
            ressd = True

        user_dict = {"table" : "user", "method" : "POST", "username" : id_creator}
        user_json = json.dumps(user_dict)

        user_results = requests.post(url_read,json = user_json)
        user_results = json.loads(user_results.text)

        if user_results['empty'] == 0:
            resu = True
        else:
            resu = False

        if ressd and resu:
            ride_dict = {"table" : "ride", "method" : "POST", "created_by" : id_creator, "timestamp" : timestamp, "source" : source, "destination" : dest}
            ride_json = json.dumps(ride_dict)

            requests.post(url_write,json = ride_json)
            
            #Correct code
            return Response(json.dumps({}),status = 201)
        
        else:
            if not resu:
                #Correct code
                return Response("No such user exists",status = 400)
            else:
                #Correct code
                return Response("Source or destination invalid",status = 400)
    
    except:
        return Response("Error while providing data",status = 400)


@app.route('/api/v1/rides',methods=['GET'])
def upcoming_rides():
    try:
        source = int(request.args.get('source'))
        destination = int(request.args.get('destination'))
        
        if source not in areas.keys() or destination not in areas.keys():
            #Correct code
            return Response("Source or destination invalid",status = 400)
        
        else:
            ride_dict = {"table" : "ride", "method" : "GET", "source" : source, "destination" : destination}
            ride_json = json.dumps(ride_dict)

            ride_results = requests.post(url_read,json = ride_json)
            ride_results = json.loads(ride_results.text)

            if not ride_results:
                #Correct code
                return Response(status = 204)
            
            else:
                now = datetime.now()

                l = []

                for i in ride_results.keys():
                    ride_date = ride_results[i]['timestamp']
                    ride_date = datetime.strptime(ride_date, '%d-%m-%Y:%S-%M-%H')

                    if ride_date >= now:
                        l.append(json.dumps(ride_results[i]))
                
                if len(l) == 0:
                    # Correct code
                    return Response(status = 204)
                
                else:
                    data_returned = "[\n"
                    for i in l:
                        data_returned += "{\n"
                        for j in i.keys():
                            data_returned += "\"" + j + "\"" + ": " + "\"" + str(i[j]) + "\"" +",\n"
                        
                        data_returned = data_returned.strip()
                        data_returned = data_returned.rstrip(",")
                        data_returned += "\n},\n"
                    
                    data_returned = data_returned.strip()
                    data_returned = data_returned.rstrip(",")
                    data_returned += "\n]"
                    
                    #Correct code
                    # return Response(data_returned,status = 200)
                    return Response(l,status = 200)
        
    except:
        return Response("Error while providing data",status = 400)



@app.route('/api/v1/rides/<ride_id>',methods=['GET'])
def details(ride_id):
    try:
        ride_id = int(ride_id)
        ride_dict = {"table" : "ride and users_and_rides", "method" : "GET", "ride_id" : ride_id}
        ride_json = json.dumps(ride_dict)

        ride_results = requests.post(url_read,json = ride_json)
        ride_results = json.loads(ride_results.text)
        
        if ride_results['empty'] == 1:
            # Correct code
            return Response(status = 204)
            
        else:
            del ride_results['empty']
            data_returned = "{\n"
            for i in ride_results.keys():
                data_returned += "\"" + i + "\"" + ": " + "\"" + str(ride_results[i]) + "\"" +",\n"
            
            data_returned = data_returned.strip()
            data_returned = data_returned.rstrip(",")
            data_returned += "\n}"
            
            #Correct code
            return Response(json.dumps(ride_results),status = 200)
    
    except:
        return Response("Error while providing data",status = 400)


@app.route('/api/v1/rides/<ride_id>',methods=['POST'])
def join_existing_ride(ride_id):
    try:
        ride_id = int(ride_id)
        data = flask.request.json
        username = data['username']

        ride_dict = {"table" : "ride", "method" : "POST", "ride_id" : ride_id}
        ride_json = json.dumps(ride_dict)

        ride_results = requests.post(url_read,json = ride_json)
        ride_results = json.loads(ride_results.text)

        user_dict = { "table" : "user", "method": "POST", "username": username }
        user_json = json.dumps(user_dict)

        user_results = requests.post(url_read,json = user_json)
        user_results = json.loads(user_results.text)

        if user_results['empty'] == 1:
            # Correct code
            return Response("No user with that username exists",status = 400)
        
        else:
            if ride_results['empty'] == 1:
                # Correct code
                return Response("No ride with that id exists",status = 400)
            
            else:
                ride_date = ride_results['timestamp']
                now = datetime.now()
                ride_date = datetime.strptime(ride_date, '%d-%m-%Y:%S-%M-%H')

                if ride_date < now:
                    #Correct code
                    return Response("Ride has already expired",status = 400)

                if ride_results['ride_creator'] == username:
                    # Correct code
                    return Response("This user has ceated the ride",status = 400)

                elif username in ride_results['users_joined']:
                    # Correct code
                    return Response("This user has already joined ride",status = 400)

                else:
                    user_joining_dict = {"table" : "users_and_rides", "method" : "POST", "ride_id" : ride_id, "username" : username}
                    user_joining_json = json.dumps(user_joining_dict)

                    requests.post(url_write,json = user_joining_json)

                    # Correct Code
                    return Response(json.dumps({}),status = 200)
    except:
        return Response("Error while providing data",status = 400)


@app.route('/api/v1/rides/<ride_id>',methods=['DELETE'])
def delete_ride(ride_id):
    try:
        ride_id = int(ride_id)
        ride_dict = {"table" : "ride", "method" : "DELETE", "ride_id" : ride_id}
        ride_json = json.dumps(ride_dict)

        ride_results = requests.post(url_read,json = ride_json)
        ride_results = json.loads(ride_results.text)

        if ride_results['empty'] == 1:
            #Correct code
            return Response("No ride with that ride_id exists",status = 400)
        
        else:
            ride_and_users_dict = {"table" : "ride", "method" : "DELETE", "ride_id" : ride_id}
            ride_and_users_json = json.dumps(ride_and_users_dict)

            requests.post(url_write,json = ride_and_users_json)

            #Correct code
            return Response(json.dumps({}),status = 200)
    except:
        return Response(status = 400)



@app.route('/api/v1/db/write',methods=['POST'])
def db_write():
    data = flask.request.json
    data = json.loads(data)
    table_chosen = data['table']
    method_used = data['method']

    if table_chosen == "user":
        if method_used == "PUT":
            user_name = data['username']
            password = data['password']
            new_user = User(username = user_name,password = password)
            db.session.add(new_user)
            db.session.commit()
            return "Added"

        elif method_used == "DELETE":
            user_name = data['username']

            user_being_removed = User.query.filter_by(username = user_name).first()

            db.session.delete(user_being_removed)
            db.session.commit()

            rides_joined = Users_and_Rides.query.filter_by(username = user_name).all()

            if len(rides_joined) != 0:
                for i in rides_joined:
                    db.session.delete(i)
                    db.session.commit()

            return "Deleted"

    elif table_chosen == "ride":
        if method_used == "POST":
            ride_creator_username = data['created_by']
            timestamp = data['timestamp']
            source = data['source']
            dest = data['destination']

            new_ride = Ride(source = source, destination = dest,timestamp = timestamp, creator_name = ride_creator_username)
            db.session.add(new_ride)
            db.session.commit()

            return "Added"
        
        elif method_used == "DELETE":
            ride_id = data['ride_id']

            ride_dets = Ride.query.filter_by(ride_id = ride_id).first()
            db.session.delete(ride_dets)
            db.session.commit()

            users_joined = Users_and_Rides.query.filter_by(ride_id = ride_id).all()
            if len(users_joined) !=0:
                for i in users_joined:
                    db.session.delete(i)
                    db.session.commit()
            
            return "Deleted"
    
    elif table_chosen == "users_and_rides":
        if method_used == "POST":
            ride_id = data['ride_id']
            username = data['username']

            new_user_joined = Users_and_Rides(ride_id = ride_id,username = username)
            db.session.add(new_user_joined)
            db.session.commit()

            return "Added"


@app.route('/api/v1/db/read',methods=['POST'])
def db_read():
    data = flask.request.json
    data = json.loads(data)
    table_chosen = data['table']
    method_used = data['method']
    if table_chosen == "user":
        user_name = data['username']
        username_checking = User.query.filter_by(username = user_name).first()
        
        user_details = dict()

        if username_checking is None:
            user_details["empty"] = 1
            return json.dumps(user_details)

        else:
            user_details["empty"] = 0
            user_details["username"] = user_name
            user_details["password"] = username_checking.password
            
            user_details["rides_created"] = []
            rides_list_query = Ride.query.filter_by(creator_name = user_name).all()
            for i in rides_list_query:
                user_details["rides_created"].append(i.ride_id)
            
            user_details["rides_joined"] = []
            rides_joined_query = Users_and_Rides.query.filter_by(username = user_name).all()
            for i in rides_joined_query:
                user_details["rides_joined"].append(i.ride_id)
            
            return json.dumps(user_details)  
    
    elif table_chosen == "ride":
        if method_used == "GET":
            source = data['source']
            dest = data['destination']

            all_rides = Ride.query.filter_by(source = source, destination = dest).all()

            count = 0
            ride_details = dict()
            for i in all_rides:
                ride_details[count] = dict()
                ride_details[count]["rideId"] = i.ride_id
                ride_details[count]["username"] = i.creator_name
                ride_details[count]["timestamp"] = i.timestamp

                count += 1

            return json.dumps(ride_details)
        
        elif method_used == "POST":
            ride_id = data['ride_id']

            ride_details = dict()
            req_ride = Ride.query.filter_by(ride_id = ride_id).first()
            
            if req_ride is None:
                ride_details["empty"] = 1

            else:
                ride_details["empty"] = 0
                ride_details["ride_creator"] = req_ride.creator_name
                ride_details["users_joined"] = []
                ride_details["timestamp"] = req_ride.timestamp

                users_joined = Users_and_Rides.query.filter_by(ride_id = ride_id).all()
                for i in users_joined:
                    ride_details["users_joined"].append(i.username)

            return json.dumps(ride_details)

        elif method_used == "DELETE":
            ride_id = data['ride_id']

            ride_details = dict()
            req_ride = Ride.query.filter_by(ride_id = ride_id).first()

            if req_ride is None:
                ride_details["empty"] = 1

            else:
                ride_details["empty"] = 0
            return json.dumps(ride_details)
    
    elif table_chosen == "ride and users_and_rides":
        if method_used == "GET":
            ride_id = data['ride_id']

            req_ride = Ride.query.filter_by(ride_id = ride_id).first()

            ride_details = dict()
            if req_ride is None:
                ride_details["empty"] = 1
                return json.dumps(ride_details)
            
            else:
                ride_details["empty"] = 0
                ride_details["rideId"] = ride_id
                ride_details["Created_by"] = req_ride.creator_name
                ride_details["users"] = []
                ride_details["timestamp"] = req_ride.timestamp
                ride_details["source"] = req_ride.source
                ride_details["destination"] = req_ride.destination

                users_joined = Users_and_Rides.query.filter_by(ride_id = ride_id).all()
                for i in users_joined:
                    ride_details["users"].append(i.username)
                
                return json.dumps(ride_details)

if __name__=="__main__":
        app.run()
