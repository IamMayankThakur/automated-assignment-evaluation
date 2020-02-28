from flask import Flask, jsonify, request, render_template, abort, Response
import json
#import flask_restful
import re
import pymongo
import requests
from datetime import datetime
import time

#WORKING  WITH THE DATABASE

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["RideShare"]
users = mydb["users"]
rides = mydb['rides']

app = Flask(__name__)

def validateTimestamp(tz):
        try:
            datetime.strptime(tz, "%d-%m-%Y:%S-%M-%H")
            return 1
        except:
            return 0

def compare_time(to_check):
    pattern = "%Y%m%d%S%M%H"
    dt = datetime.now()
    current= dt.strftime(pattern)
    # print(current)
    # to_check = "10-11-2022:12-12-08"
    # to_check = to_check.strftime("%Y-%m-%d:%S-%M-%H")
    li = to_check.split(":")
    date = li[0]
    time = li[1]
    temp = date.split("-")
    time = time.split("-")
    temp_var = temp[2]
    temp[2] = temp[0]
    temp[0] = temp_var
    to_check = ""
    for i in temp:
        to_check += i
    for i in time:
        to_check += i
    if (to_check > current):
        return 1
    return 0

@app.errorhandler(404)
def not_found_error(error):
    return "Not found", 404

@app.errorhandler(400)
def bad_request_error(error):
    return "Bad Request", 400

@app.errorhandler(405)
def method_not_allowed_error(error):
    return "Methods Not Allowed", 405

@app.errorhandler(500)
def internal_server_error(error):
    return "Internal Server Error", 500

#API'S

@app.route('/')
def test():
    return "HELLO WORLD"

@app.route('/api/v1/users', methods = ['PUT'])
def add_user():
    if (request.method == 'PUT'):
        dataDict = request.get_json()
        password = dataDict["password"]
        pattern = re.compile(r'\b[0-9a-f]{40}\b')
        match = re.match(pattern, password)
        if ( match == None):
            return {}, 400    #PASSWORD NOT IN THE CORRECT FORMAT
        else:
            d = {}
            d["table"] = "users"
            d["work"] = "INSERT"
            d["data"] = dataDict
            d["check"] = "user"
            found = requests.post("http://localhost:8000/api/v1/db/read", data = json.dumps(d))
            found = found.text
            found = int(found)
            if (found == 1):
                return {}, 400  #username already exists
            else:
                retjson = requests.post("http://localhost:8000/api/v1/db/write", data = json.dumps(d))
                return {}, 201  #successfully inserted
    else:
        return {}, 405   #IF METHOD USED IS NOT PUT


@app.route('/api/v1/users/<username>', methods = ['DELETE'])
def remove_user(username):
    if (request.method == 'DELETE'):
        dataDict = {"username" : username}
        d = {}
        d["table"] = "users"
        d["work"] = "DELETE"
        d["data"] = dataDict
        d["check"] = "user"
        found = requests.post("http://localhost:8000/api/v1/db/read", data = json.dumps(d))
        found = found.text
        found = int(found)
        if (found == 0):
            return {}, 400    #USERNAME NOT FOUND
        else:
            retjson = requests.post("http://localhost:8000/api/v1/db/write", data = json.dumps(d))
            return {}, 200
    else:
        return {}, 405 #IF THE METHOD USED IS NOT DELETE


@app.route('/api/v1/rides', methods = ['POST'])
def new_ride():
    if (request.method == 'POST'):
        dataDict = request.get_json()
        source = dataDict["source"]
        source = int(source)
        destination = dataDict["destination"]
        destination = int(destination)
        username = dataDict["created_by"]
        timestamp = dataDict['timestamp']   #VALIDATE TIMESTAMP
        # print("check")
        if not(validateTimestamp(timestamp)):
            return {}, 400
        # print("check1")
        if (source >= 1 and source <= 198) and (destination >= 1 and destination <= 198):
            d = {}
            d["table"] = "rides"
            d["work"] = "INSERT"
            d["data"] = dataDict
            # d["rideid"] = 0
            d["check"] = "user"
            d["data"]["username"] = username
            found = requests.post("http://localhost:8000/api/v1/db/read", data = json.dumps(d))
            found = found.text
            # print(found)
            
            found = int(found)
            if found == 0:
                return {}, 400  
            else:        
                # d["rideid"] = 1
                d["check"] = None
                rideid = requests.post("http://localhost:8000/api/v1/db/read", data = json.dumps(d))
                rideid = rideid.text
                rideid = int(rideid)
                d["data"]["ride_id"] = rideid
                retjson = requests.post("http://localhost:8000/api/v1/db/write", data = json.dumps(d))
                return {}, 201
        else:
            return {}, 400
    else:
        return {}, 405  #POST METHOD NOT USED


@app.route('/api/v1/rides', methods = ['GET']) #CHECK FOR THE SOURCE AND DESTINATION
def upcoming_rides():
    if (request.method == 'GET'):
        source = request.args.get("source")
        if source == None or source == '':
            return {}, 400
        source = int(source)
        destination = request.args.get("destination")
        if destination == None or destination == '':
            return {}, 400
        destination = int(destination)
        if (source >= 1 and source <= 198) and (destination >= 1 and destination <= 198):
            d = {}
            d["table"] = "rides"
            d["work"] = "GET_RIDES"
            dataDict = {"source" : source, "destination" : destination}
            d["data"] = dataDict
            d["check"] = None
            dbquery = requests.post("http://localhost:8000/api/v1/db/read", data = json.dumps(d))
            dbquery = json.loads(dbquery.text)
            for i in dbquery:
                return jsonify(dbquery), 200
            else:
                return {}, 204
        else:
            return {}, 400
    else:
        return {}, 405


@app.route('/api/v1/rides/<rideId>', methods = ['GET'])
def list_all_details(rideId):
    if (request.method == 'GET'):
        rideid = int(rideId)
        d = {}
        d["table"] = "rides"
        d["work"] = "ALL_DETAILS"
        dataDict = {"ride_id" : rideid}
        d["data"] = dataDict
        d["check"] = None
        dbquery = requests.post("http://localhost:8000/api/v1/db/read", data = json.dumps(d))
        if (dbquery.status_code == 400):
            return {}, 400
        dbquery = json.loads(dbquery.text)

        return jsonify(dbquery), 200
    else:
        return {}, 405

        
@app.route('/api/v1/rides/<rideId>', methods = ['POST'])
def join_ride(rideId):
    if (request.method == 'POST'):
        rideid = int(rideId)
        dataDict = request.get_json()
        dataDict["ride_id"] = rideid
        d = {}
        d["table"] = "rides"
        d["work"] = "JOIN_EXISTING"
        d["data"] = dataDict
        d["check"] = None
        dbquery = requests.post("http://localhost:8000/api/v1/db/read", data = json.dumps(d))
        dbquery = dbquery.text
        if dbquery == "00":
            return {}, 204
        elif dbquery == "10":
            return {}, 400
        else:
            retjson = requests.post("http://localhost:8000/api/v1/db/write", data = json.dumps(d))
            return {}, 200


@app.route('/api/v1/rides/<rideId>', methods = ['DELETE'])
def delete_ride(rideId):
    if (request.method == 'DELETE'):
        rideid = int(rideId)
        d = {}
        d["table"] = "rides"
        d["work"] = "DELETE"
        d["check"] = None
        dataDict = {"ride_id" : rideid}
        d["data"] = dataDict
        found = requests.post("http://localhost:8000/api/v1/db/read", data = json.dumps(d))
        found = int(found.text)
        if (found == 0):
            return {}, 400
        retjson = requests.post("http://localhost:8000/api/v1/db/write", data = json.dumps(d))
        return {}, 200
    else:
        return {}, 405


@app.route('/api/v1/db/read', methods = ['POST'])
def db_read():

    dataDict = json.loads(request.data)
    table = dataDict["table"]
    work = dataDict["work"]
    data = dataDict["data"]
    check = dataDict["check"]
    if table != '' and table != None and work != None and work != '':
        if check == "user":
            username = data["username"]
            search = {"username" : username}
            users = mydb["users"]
            dbquery = users.find(search)
            for i in dbquery:
                return "1"
            return "0"
        
        elif table == "rides" and work == "INSERT":
            rideid = 1000
            dbquery = rides.find({})
            count = 0
            for i in dbquery:
                count += 1
            if count == 0:
                rideid = 1000
            else:
                rideid = rides.find_one(sort = [("ride_id", -1)])["ride_id"]
                rideid += 10
            rideid = str(rideid)
            return rideid
        
        elif table == "rides" and work == "GET_RIDES":
            source = int(data["source"])
            destination = int(data["destination"])
            search = {"source" : source, "destination" : destination}
            dbquery = rides.find(search)
            li = []
            found = 0
            # now = datetime.now().strftime("%d-%m-%Y:%S-%M-%H")
            for i in dbquery:
                d = dict()
                d["rideId"] = i["ride_id"]   ##GLOBALLY UNIQUE CHECK
                d["username"] = i["created_by"]
                d["timestamp"] = i["timestamp"]
                if compare_time(i["timestamp"]):
                    li.append(d)
                else:
                    pass
                found = 1
            # print(li)

            return jsonify(li)

        elif table == "rides" and work == "ALL_DETAILS":
            rideid = data["ride_id"]
            search = {"ride_id" : rideid}
            dbquery = rides.find(search)
            found = 0
            for i in dbquery:
                found += 1
                created_by = i["created_by"]
                users = i["users_rides"]
                timestamp = i["timestamp"]
                source = i["source"]
                destination = i["destination"]
            if (found == 0):
                return Response(None, status = 400, mimetype = 'application/json')
            else:
                retjson = {
                "rideId" : rideid,
                "created_by" : created_by,
                "users" : users,
                "timestamp" : timestamp,
                "source" : source,
                "destination" : destination
            }
            return jsonify(retjson), 200

        elif table == "rides" and work == "JOIN_EXISTING":
            rideid = data["ride_id"]
            username = data["username"]
            search = {"username" : username}
            users = mydb["users"]
            dbquery = users.find(search)
            username_exists = 0
            for i in dbquery:
                username_exists = 1
            if username_exists == 0:
                return  "00" #username doesnot exists
            search = {"ride_id" : rideid}
            dbquery = rides.find(search)
            ride_exists = 0
            for i in dbquery:
                ride_exists = 1
            if ride_exists == 0:
                return  "10" #rideis doesnot exist
            return  "11" #both exists

        elif table == "rides" and work == "DELETE":
            rideid = data["ride_id"]
            search = {"ride_id" : rideid}
            dbquery = rides.find(search)
            for i in dbquery:
                return "1"
            return "0"
        
    else:
        return {}, 400


@app.route('/api/v1/db/write', methods = ['POST'])
def db_write():
    dataDict = json.loads(request.data)
    table = dataDict["table"]
    work = dataDict["work"]
    data = dataDict["data"]
    if table != '' and table != None and work != None and work != '':
        if table == "users" and work == "INSERT":
            username = data["username"]
            password = data["password"]
            users.insert(({"username" : username, "password" : password}))
            return {}, 201

        elif table == "users" and work == "DELETE":
            username = data["username"]
            search = {"username" : username}
            x = users.delete_many(search)
            return "Successfully deleted"

        elif table == "rides" and work == "INSERT":
            rideid = data["ride_id"]
            username = data["created_by"]
            timestamp = data["timestamp"]
            source = int(data["source"])
            destination = int(data["destination"])
            rides.insert({"ride_id" : rideid, "created_by" : username, "timestamp" : timestamp, "source" : source, "destination" : destination, "users_rides" : [username]})
            return "Successfully Inserted"

        elif table == "rides" and work == "JOIN_EXISTING":
            rideid = data["ride_id"]
            select = {"ride_id" : rideid}
            dbquery = rides.find(select)
            username = data["username"]
            # found = 0
            for i in dbquery:
                li = i["users_rides"]
                li.append(username)            
            new_value = {"$set" : {"users_rides" : li}}
            rides.update(select, new_value)
            return Response(None, status = 200, mimetype = 'application/json')

        elif table == "rides" and work == "DELETE":
            rideid = data["ride_id"]
            search = {"ride_id" : rideid}
            x = rides.delete_many(search)
            return "Successfully deleted"

    else:
        return "Bad request", 400

if __name__ == "__main__":
    app.run(debug=True)