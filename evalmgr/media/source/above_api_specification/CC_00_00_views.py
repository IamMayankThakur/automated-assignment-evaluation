from flask import Flask, render_template, jsonify, request, abort, Response
from flask_sqlalchemy import SQLAlchemy
from flask_api import status
from collections import defaultdict
import requests
import json
import datetime
from enum import Enum, unique
# CC_0269_0283_1244_1256
# 18.215.69.207


application = Flask(__name__)
application.config.from_object('configuration.DevelopmentConfig')
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(application)

from RideShare_DB import User, Ride, User_Ride

def DPSdateconverttostring(datetimeobj):
    year = datetimeobj.year
    month = datetimeobj.month
    day = datetimeobj.day
    hour = datetimeobj.hour
    minute = datetimeobj.minute
    second = datetimeobj.second
    return str(day)+"-"+str(month)+"-"+str(year)+":"+str(second)+"-"+str(minute)+"-"+str(hour)

def DPSdateconvertstringtodate(datetimestring):
    dsplitt = datetimestring.split(':')
    date = [int(splitval) for splitval in dsplitt[0].split('-')]
    time = [int(splitval) for splitval in dsplitt[1].split('-')]
    
    day = date[0]
    month = date[1]
    year = date[2]
    
    hours = time[2]
    minutes = time[1]
    seconds = time[0]

    return datetime.datetime(year=year, month=month, day=day, hour=hours, minute=minutes,second=seconds)


@application.route('/', methods=["get"])
def fallback():	
    return Response({"Success"}, status=200, mimetype='application/json')
	# return "Server is under maintenance, please visit again in a couple of minutes DATTHESH"


@application.route('/api/v1/db/write', methods=["POST"])
def db_write():	

    # Delete or insert
    case_no = request.get_json()['case']
    
    table_name = request.get_json()['table_name']

    # Insert
    if (case_no == 1):
        
        flag = 1

        if table_name == 'user':
            user_name = request.get_json()['user_name']
            password = request.get_json()['password']
            record = User(user_name, password)
                
            
        elif table_name == 'ride':
            created_by = request.get_json()['created_by']
            source = request.get_json()['source']
            destination = request.get_json()['destination']
            start_time = DPSdateconvertstringtodate(request.get_json()['timestamp'])

            if(start_time >= datetime.datetime.now()):
                record = Ride(created_by, source, destination, start_time)
            else:
                flag = 0
        
        else:
            u_ride_id = request.get_json()['u_ride_id']
            u_user_name = request.get_json()['u_user_name']
            
            record = Ride.query.filter(Ride.ride_id == u_ride_id)
            
            try:
                for i in record:
                    if((i.retjson()['start_time']) >= datetime.datetime.now()):
                        flag = 1
                    else:
                        flag = 0
                record =  User_Ride(u_ride_id, u_user_name)
            except:
                flag = 0

        if case_no == 1 and flag != 0:
            try:
                db.session.add(record)
                db.session.commit()
                flag = 1
            except:
                flag = 0

    else:
        if table_name == 'user':
            record = User.query.get(str(request.get_json()['user_name']))
            
        elif table_name == 'ride':
            record = Ride.query.get(str(request.get_json()['ride_id']))

        try:
            db.session.delete(record)
            db.session.commit()
            flag = 1
        except:
            flag = 0
    
    if flag == 1:
        return "OK"
    else:
        return "NOTOK"


@application.route('/api/v1/db/read', methods=["POST"])
def db_read():

    table_name = request.get_json()['table_name']

    if table_name == 'user':
        uname = request.get_json()['user_name']
        retval = User.query.get(str(uname))
        # retval = User.query.order_by(User.user_name).all()

        if retval != None:
            retval = retval.retjson()
        
        else:
            retval = {}

    elif table_name == 'ride':
        if request.get_json()['ridesordetails'] == 1:
            source_name = request.get_json()['source']
            dest_name = request.get_json()['destination']
            retquery = Ride.query.filter(Ride.source == source_name, Ride.destination == dest_name, Ride.start_time >= datetime.datetime.now())
            retval = defaultdict(list)
            counter = 0
            for i in retquery:
                store = i.retjson()
                store['start_time'] = DPSdateconverttostring(store['start_time'])
                retval[counter].append(store)
                counter += 1
            
            return retval

        else:
            ride_id = request.get_json()['ride_id']
            retquery = Ride.query.filter_by(ride_id=ride_id)
            retval = defaultdict(list)
            counter = 0
            for i in retquery:
                store = i.retjson()
                store['start_time'] = DPSdateconverttostring(store['start_time'])
                retval[counter].append(store)
                counter += 1
            return retval

    else:
        ride_id = request.get_json()['u_ride_id']
        retquery = Ride.query.filter_by(ride_id=ride_id)
        counter = 0
        retval = dict()
        for i in retquery:
            retval = (i.retjson())
            counter += 1
        
        if(len(retval)):
            retval['start_time'] = DPSdateconverttostring(retval['start_time'])
            
            curruser = retval['created_by']
            retval['users'] = [curruser]

            usersquery = User_Ride.query.filter_by(u_ride_id=ride_id)
            for i in usersquery:
                retval['users'].append(i.retjson()['u_user_name'])

    return retval


# Add user:
@application.route('/api/v1/users', methods=["PUT"])
def add_user():

    username = request.get_json()["username"]	
    password = request.get_json()["password"]

    json_data = {
        "table_name": "user",
        "user_name" : username
    }

    dbtemp = requests.post('http://127.0.0.1:9999/api/v1/db/read', json=json_data)

    # Duplicate Username
    try:
        username == dbtemp.json()['user_name']
        return Response({"Username Already Exists"}, status=400, mimetype='application/json')
    except:
        # Password -> SHA
        if len(password) > 40 or len(password) < 40:
            return Response({"Password not in accordance with the requirement"}, status=400, mimetype='application/json')
        try:
            int(password, 16)
        except ValueError:
            return Response({"Password not in accordance with the requirement"}, status=400, mimetype='application/json')


    json_data = {
        "table_name": "user",
        "user_name" : username,
        "password" : password,
        "case": 1
    }

    dbtemp = requests.post('http://127.0.0.1:9999/api/v1/db/write', json = json_data)
    if dbtemp.text == "OK":
        return Response({"User successfully added"}, status=201, mimetype='application/json')
    else:
        return Response({"DB could not be contacted"}, status=400, mimetype='application/json')


# Remove user:
@application.route('/api/v1/<username>', methods=["DELETE"])
def del_user(username):

    try:
        json_data = {
            "table_name": "user",
            "user_name": username,
            "case" : 2
        }

        dbtemp = requests.post('http://127.0.0.1:9999/api/v1/db/write', json = json_data)

        if dbtemp.text == "OK":
            return Response({"User Deleted"}, status=200, mimetype='application/json')

        else:
            return Response({"User could not be deleted"}, status=400, mimetype='application/json')

    except:
        return Response({"User could not be deleted"}, status=400, mimetype='application/json')


# List upcoming rides:
@application.route('/api/v1/rides', methods=["GET"])
def list_upcoming_rides():

    source = request.args.get('source')
    destination = request.args.get('destination')

    if int(source) <= 198 and int(source) >= 1 and int(destination) <= 198 and int(destination) >= 1:
        rides = list()

        json_data = {
            "table_name": "ride",
            "source" : source,
            "destination" : destination,
            "ridesordetails" : 1
        }
        
        dbtemp = requests.post('http://127.0.0.1:9999/api/v1/db/read', json = json_data)

        for ride in dbtemp.json().values():
            if ride[0]['source'] == source and ride[0]['destination'] == destination:
                newride = dict()
                newride["ride_id"] = ride[0]['ride_id']
                newride["username"] = ride[0]['created_by']
                newride["timestamp"] = ride[0]['start_time']
                rides.append(newride)

        if len(rides) == 0:
            return Response({"Ride(s) could not be found"}, status=204, mimetype='application/json')
        
        else:
            return jsonify(rides), 200
    else:
        return Response({"Our services for the location(s) will be available soon"}, status=400, mimetype='application/json')


# Create ride:
@application.route("/api/v1/rides", methods = ["POST"])
def create_ride():
    
    try:
        new_ride = {
            "table_name": "ride",
            "created_by": request.get_json()['created_by'],
            "source": request.get_json()['source'],
            "destination": request.get_json()['destination'],
            "timestamp" : request.get_json()['timestamp'],
            "case": 1
        }

        dbtemp = requests.post("http://127.0.0.1:9999/api/v1/db/write", json=new_ride)
        if dbtemp.text == "OK":
            return Response({"Ride created successfully"}, 201, mimetype='application/json')
        else:
            return Response({"Cannot create the ride at the moment."}, status=400, mimetype='application/json')

    except:
        return Response({"Cannot create the ride at the moment."}, status=400, mimetype='application/json')



# Delete a ride:
@application.route("/api/v1/rides/<rideID>", methods=["DELETE"])
def delete_ride(rideID):

    try:
        json_data = {
            "table_name": "ride",
            "ride_id": rideID,
            "case" : 2
        }

        dbtemp = requests.post('http://127.0.0.1:9999/api/v1/db/write', json = json_data)

        if dbtemp.text == "OK":
            return Response({"Ride deleted"}, status=200, mimetype='application/json')

        else:
            return Response({"Ride cannot be deleted"}, status=400, mimetype='application/json')

    except:
        return Response({"Ride cannot be deleted"}, status=400, mimetype='application/json')


# Join existing ride:
@application.route("/api/v1/rides/<rideID>", methods=["POST"])
def join_existing_ride(rideID):

    json_request_params = {
        "table_name": "ride",
        "ride_id": rideID,
        "ridesordetails" : 2
    }
    
    dbtemp = requests.post("http://127.0.0.1:9999/api/v1/db/read", json=json_request_params)
    
    if len(dbtemp.json()) == 0:
        return Response({"Ride not found"}, status=400, mimetype='application/json')
        # response = Response({"Ride not found"}, 204, mimetype='application/json')

    else:

        user_name = request.get_json()["username"]
        
        json_request_params = {
            "table_name": "user",
            "user_name": user_name
        }
        
        dbtemp2 = requests.post("http://127.0.0.1:9999/api/v1/db/read", json=json_request_params)
        
        if(len(dbtemp2.json()) > 0):
            
            new_join = dict()
            new_join["table_name"] = "user_ride"
            new_join["u_ride_id"] = rideID
            new_join['u_user_name'] = user_name
            new_join["case"] = 1
            
            dbtemp3 = requests.post("http://127.0.0.1:9999/api/v1/db/write", json=new_join)
            
            if dbtemp3.text == "OK":
                return Response({"You have joined the ride"}, status=200, mimetype='application/json')
            else:
                return Response({"You are already a part of the ride or the start time has elapsed"}, status=400, mimetype='application/json')
            
        else:
            return Response({"Invalid username"}, status=400, mimetype='application/json')


# List details of a ride:
@application.route('/api/v1/rides/<rideId>', methods=["GET"])
def list_ride_details(rideId):

    json_data = {
        "table_name": "user_ride",
        "u_ride_id": rideId
    }

    dbtemp = requests.post("http://127.0.0.1:9999/api/v1/db/read", json=json_data)

    if(len(dbtemp.json())):
        printformat = dict()
        printformat["rideId"] = dbtemp.json()['ride_id']
        printformat["Created_by"] = dbtemp.json()['created_by']
        printformat["users"] = dbtemp.json()['users']
        printformat["Timestamp"] = dbtemp.json()['start_time']
        printformat["source"] = dbtemp.json()['source']
        printformat["destination"] = dbtemp.json()['destination']
        return jsonify(printformat)
    else:
        return Response({"Invalid Ride ID"}, status=400, mimetype='application/json')


# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':	
	application.debug=True
	application.run()