from flask import Flask, render_template, jsonify, request, abort, make_response, json
import requests
import pymongo
from pprint import pprint
from utils import *
import datetime

app = Flask(__name__)
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["CC"]


port = '5000'
server = 'http://127.0.0.1:' + port

"""
API - 1

Add User

request: username and password(sha1 checksum) are sent
response: {}

if valid, they are stored in the database
status codes:
    201 CREATED - successfully created the user
    400 BAD REQUEST - password not SHA1 checksum
    XXXXXXXXXXXXXXXX - User already exists

"""

@app.route("/api/v1/users", methods = ["PUT"])
def addUser():

    try:
        username = request.get_json()["username"]
        password = request.get_json()["password"]
    except KeyError:
        return make_response("invalid request", 400)

    if not is_sha1(password):
        return make_response("error: invalid password", 400)

    dataToCheck = {"operation" : "read", "selectFields" : {"_id" : 0}, "collection" : "users", "data": {"username" : username}}
    requestToCheck = requests.post(server + "/api/v1/db/read", json = dataToCheck)
    exists = len(requestToCheck.json())

    if exists:
        return make_response("error : User already exists", 409)

    dataToAdd = {"operation" : "add", "collection" : "users", "data": {"username" : username, "password": password}}
    requestToAdd = requests.post(server + "/api/v1/db/write", json = dataToAdd)

    if requestToAdd.status_code == 200:
        return make_response(jsonify({}), 201)

    else:
        return make_response(requestToAdd.text, requestToAdd.status_code)


"""
API - 2

Delete User

deletes an existing user

request: username, DELETE
response: {}

status codes: 200 OK - successfully deleted
            400 BAD REQUEST - user does not exist
"""

@app.route("/api/v1/users/<username>", methods = ["DELETE"])
def removeUser(username):
    dataToDelete = {"operation" : "delete", "collection" : "users", "data" : {"username" : username}}
    req = requests.post(server + "/api/v1/db/write", json = dataToDelete)

    if req.status_code == 200:
         return make_response(jsonify({}), 200)
    else:
        return make_response("Error: User not found", 400)



"""
API - 3

API to create a ride

request: POST created_by, timestamp, source, destination
response: {}

status codes: 201 - successful creation
            400 - invalid user, invalid location, empty fields

TODO: Check timestamp

"""
@app.route("/api/v1/rides", methods = ["POST"])
def createRide():
    data = request.get_json()

    try:
        username = data["created_by"]
        source, destination = data["source"], data["destination"]
        timestamp = datetime.datetime.strptime(data["timestamp"], "%d-%m-%Y:%H-%M-%S")

    except KeyError:
        return make_response("Enter all valid details", 400)

    except ValueError:
        return make_response("Invalid timestamp", 400)

    if not find_area(source) or not find_area(destination):
        return make_response("invalid area", 400)


    dataToCheck = {"operation": "read", "selectFields" : {"_id" : 0}, "collection" : "users", "data": {"username" : username}}
    requestToCheck = requests.post(server + "/api/v1/db/read", json = dataToCheck)
    exists = len(requestToCheck.json())

    if not exists:
        return make_response("Error: Invalid user", 400)

    reqNewIDData = {"operation" : "getNewRideID", "collection": "rideID"}
    reqNewID = requests.post(server + "/api/v1/db/read", json = reqNewIDData)

    if(reqNewID.status_code != 200):
        return make_response(reqNewID.text, reqNewID.status_code)

    newID = float(reqNewID.text)
    data["rideID"] = int(newID)

    data["users"] = []

    # updating new Ride id first, because if creating a new ride fails, the next time we get a new id, it will still be unique
    # but if we update ride first but if updation of ride ID fails, there will be duplication of ride rideIDs
    updateID = {"operation" : "set", "collection" : "rideID", "data" : {}, "ID": newID}
    updateReq = requests.post(server + "/api/v1/db/write", json = updateID)

    if updateReq.status_code != 200:
        return make_response(updateReq.text, updateReq.status_code)

    dataToAdd = {"operation" : "add", "selectFields" : {"_id" : 0}, "collection" : "rides", "data" : data}
    req = requests.post(server + "/api/v1/db/write", json = dataToAdd)

    if req.status_code != 200:
        return make_response(req.text, req.status_code)

    return make_response(jsonify({}), 201)




"""
API - 4

The request is in the format mentioned below for source 2 to destination 3
/api/v1/rides?source=2&destination=3

TODO: add timestamps

request: GET, source and destination
response: { rideid, username, timestamp}

"""

# check route
# TODO: add timestamp checking
@app.route('/api/v1/rides', methods = ["GET"])
def getUpcomingRides():

    try:
        source = request.args.get('source')
        destination = request.args.get('destination')

    except:
        return make_response("select source and destination", 400)

    if source == "" or destination == "" or not find_area(source) or not find_area(destination):
        return make_response("select valid source and desintation", 400)


    current_time = datetime.datetime.now()
    dtFormat = "%d-%m-%Y:%H-%M-%S"

    dataToMatch = {"operation" : "read", "collection": "rides", "selectFields": {"timestamp" : 1, "created_by": 1, "rideID": 1, "_id" : 0}, "data" : {"source" : source, "destination" : destination}}
    req = requests.post(server + "/api/v1/db/read", json = dataToMatch)
    # data = req.json()
    # data = req.json()

    matches = []
    for i in req.json():
        newJson = req.json()[i]
        if(datetime.datetime.now() < datetime.datetime.strptime(newJson["timestamp"], dtFormat)):
            newJson["username"] = newJson.pop("created_by")
            # req.json()[i].pop("created_by")
            matches.append(newJson)



    return make_response(jsonify(matches), req.status_code)


"""
API - 5
List all details of a ride



"""
# TODO: add the right status codes
@app.route("/api/v1/rides/<rideID>", methods = ["GET"])
def getRideDetails(rideID):

    rideID = int(rideID)
    dataToMatch = {"operation": "read", "selectFields" : {"_id" : 0}, "collection" : "rides" , "data" : {"rideID" : rideID}}
    req = requests.post(server + "/api/v1/db/read", json = dataToMatch)

    # Ride does not exist
    if(req.status_code == 400):
         return(make_response("rideID does not exist", 400))

    else:
        data = req.json()["0"]
        # rideIDs being unique will only have one entry in the response

        return make_response(data, 200)



"""
API - 6

"""
@app.route("/api/v1/rides/<rideID>", methods = ["POST"])
def joinRide(rideID):

    rideID = int(rideID)

    user = request.get_json()["username"]

    dataToCheck = {"operation": "read", "selectFields" : {"_id" : 0}, "collection" : "users", "data": {"username" : user}}
    requestToCheck = requests.post(server + "/api/v1/db/read", json = dataToCheck)
    exists = len(requestToCheck.json())

    if not exists:
        return make_response("Error: Invalid user", 400)

    dataToCheckUser = {"operation": "read", "selectFields" : {"_id" : 0, "created_by" : 1}, "collection" : "rides", "data": {"rideID" : rideID}}
    requestToCheckUser = requests.post(server + "/api/v1/db/read", json = dataToCheckUser)
    createdBy = requestToCheckUser.json()["0"]["created_by"]
    #
    if(user == createdBy):
        return make_response("Error: user cannot join their own ride", 400)

    # print(requestToCheckUser.json())
    dataToUpdate = {"operation": "update", "collection": "rides", "data" : {"rideID": rideID}, "extend": {"users" : user}}
    req = requests.post(server + "/api/v1/db/write", json = dataToUpdate)

    if(req.status_code == 200):
        return make_response("", 200)
    else:
        return make_response("", req.status_code)




"""
API - 7


"""
@app.route("/api/v1/rides/<rideID>", methods = ["DELETE"])
def deleteRide(rideID):

    rideID = int(rideID)
    dataToDelete = {"operation" : "delete", "collection" : "rides", "data" : {"rideID" : rideID}}
    req = requests.post(server + "/api/v1/db/write", json = dataToDelete)

    if req.status_code == 200:
         return make_response("", 200)
    else:
        abort(req.status_code)


"""

API - 8

use this API to write to the database
Currently using mongodb as the database to store information about rides

sending data through POST:
the post request is to be structured as follows (JSON):
["operation": "add/delete/update/set", "collection" : "<collection_name>", "data" : {data_to_insert}, "extend"(if using update) : {"users" : "user"} ]

add : to add to db
delete : to delete from db
update: mostly used to append a new user to the users in a ride. can be used to add any value to any array on the db with minor tweaks.
set: used almost exclusively setting a new rideid


The API must support the following operations:
1. write username and hashed password
2. delete a user
3. create a new ride
4. join an existing ride
5. delete a ride

returns status code 200 OK if successful.

"""

@app.route('/api/v1/db/write', methods=["POST"])
def write():

    req = request.get_json()
    collection = db[req["collection"]]
    data = req["data"]

    if req["operation"] == "add":
        try:
            add = collection.insert_one(data)
        except:
            abort(500)

    elif req["operation"] == "delete":
        try:
            delete = collection.delete_one(data)

            if(delete.deleted_count == 0):
                return make_response("", 400)
            else:
                return make_response("", 200)
        except:
            return(make_response("", 500))

    elif req["operation"] == "update":
        try:
            user = req["extend"]["users"]

            update = collection.update_one(data, {"$addToSet" : {"users" : user}})

        except:
            return make_response("", 500)

    elif req["operation"] == "set":
        try:
            newID = req["ID"]
            update = collection.update(collection.find_one(), {"$set" : {"maxRideID" : newID}})
        except:
            return(make_response("", 500))

    else:
        return(make_response("", 500))
    return make_response("", 200)



"""
API 9
use this API to read from the database
Currently using mongodb as the database to store information about rides

sending data through POST:
the post request is to be structured as follows (JSON):
["operation": "getNewRideID/read", "collection" : "<collection_name>", "data_to_match" : {data_to_match}]

The API must support the following operations:
1. list upcoming rides given a source and destination
2. given a ride id, list all its details

returns the data in json format.
"""

# TODO: return less generic status codes
@app.route('/api/v1/db/read', methods=["POST"])
def read():

    req = request.get_json()
    collection = db[req["collection"]]

    if req["operation"] == "getNewRideID":
            # newRide = list(collection.find().sort([("rideIDn",-1)]).limit(1))[0]["rideIDn"]
            # return make_response(str(newRide + 1), 200)
            try:
                newRide = collection.find_one()["maxRideID"]
                return make_response(str(newRide + 1), 200)
            except:
                return make_response("", 500)

    else:
        match = req["data"]
        selectFields = req["selectFields"]

        try:
            # not returning _id, plus having _id has problems with jsonify
            records = collection.find(match, selectFields)

            matches = {}
            c = 0

            for x in records:
                matches.update({c: x})
                c += 1

            if c == 0:
                 return make_response(jsonify({}), 400)

            return make_response(jsonify(matches), 200)
        except:
            make_response("", 500)


if __name__ == '__main__':
	app.debug=True
	app.run(port = port)
