import copy
from flask import Flask, render_template, jsonify, request, abort
from bson.json_util import loads, dumps
from bson import Binary, Code
import mongoengine
import dbapi
import datetime
import requests
import re

dbapi.myconnect()
app = Flask(__name__)

def get_correct_rides(ridelist):
    newlist = []
    dt = datetime.datetime.now()
    for ele in ridelist:
        if datetime.datetime.strptime(ele["timestamp"], '%d-%m-%Y:%S-%M-%H') > dt:
            newlist.append(ele)
    return newlist

@app.route('/cc', methods = ["GET"])
def index():
    return "<h1>Welcome to our submission for Assignment 1</h1>"


@app.route('/api/v1/users', methods = ["PUT"])
#Status codes 201, 400, 405, 500
def add_user():
    #Getting requried objects from request
    user = dict()
    user["username"] = request.get_json()["username"]
    user["password"] = request.get_json()["password"]

    #check if the user already exists
    r1 = requests.post("http://localhost:5000/api/v1/db/read", json = {"collection":"User", "jsonobj" : {"username" : user["username"]}, "fields":[]})
    if len(r1.json())!=0: #someone check this later
        return "User already exists!", 400

    #check if the password is in the required format
    if not re.compile("^[a-fA-F0-9]{40}$").match(user["password"]):
        return "Password format incorrect", 400

    #write the user object to the database
    r = requests.post("http://localhost:5000/api/v1/db/write", json = {"collection":"User", "jsonobj" : user, "action":"insert"})

    if r.status_code == 200:
        return jsonify({}), 201
    else:
        return "Please check input", 400

@app.route('/api/v1/users/<username>', methods = ["DELETE"])
#Status codes 200,400,405
def remove_user(username):
    #check if the user exists in the database
    r1 = requests.post("http://localhost:5000/api/v1/db/read", json = {"collection":"User", "jsonobj" : {"username" : username}, "fields":[]})
    if len(r1.json())==0: #someone check this later
        return "Username does not exist", 400
    
    #delete the user from the database
    r = requests.post("http://localhost:5000/api/v1/db/write", json = {"collection":"User", "jsonobj" : {"username":username} , "action":"delete"})
    #if the user was deleted, delete his other stuff
    if r.status_code == 200:
        requests.post("http://localhost:5000/api/v1/db/write", json = {"collection":"Ride", "jsonobj" : {"username":username} , "action":"delete"})
        r =requests.post("http://localhost:5000/api/v1/db/read", json = {"collection":"Ride", "jsonobj" : {} , "fields":[]})
        cpy = copy.deepcopy(r.json())
        for obj in cpy:
            if username in obj["users"]:
                obj["users"].remove(username)
        requests.post("http://localhost:5000/api/v1/db/write", json = {"collection":"Ride", "jsonobj" :cpy , "action":"update"})
        return jsonify({}), 200

    elif r.status_code==204:
        return "User not present",400
    else:
        return "Delete operation failed", 400

@app.route('/api/v1/rides', methods = ["POST"])
#Status codes 201,400,405
def create_ride():
    #Getting requried objects from request
    ride = dict()
    ride["username"] = request.get_json()["created_by"]
    ride["timestamp"] = request.get_json()["timestamp"]
    ride["source"] = request.get_json()["source"]
    ride["destination"] = request.get_json()["destination"]

    #same source and destination
    if ride["source"]==ride["destination"]:
        return "Source is same as destination", 400

    try:  #checking if the string is a valid timestamp
        datetime.datetime.strptime(ride['timestamp'], '%d-%m-%Y:%S-%M-%H')
    except:
        return "Invalid timestamp", 400

    #perform API query to insert the ride to the database
    r1 = requests.post("http://localhost:5000/api/v1/db/read", json = {"collection":"User", "jsonobj" : {"username":ride["username"]}, "fields":[]})
    if len(r1.json())>0:
        r = requests.post("http://localhost:5000/api/v1/db/write", json = {"collection":"Ride", "jsonobj" : ride , "action":"insert"})
        if r.status_code == 200 or r.status_code==204:
            return jsonify({}), 201
        else:
            return "a", 400
    else:
        return "User does not exist", 400

@app.route('/api/v1/rides', methods = ["GET"])
#Status codes 200 204 400 405
def list_rides():
    source = request.args.get('source')
    destination = request.args.get('destination')
    if source is None or destination is None:
        return "Enter both source and destination", 400
    try:
        source, destination = int(source), int(destination)
    except:
        return "Missing source or destination", 400
    if source not in range(1,199) or destination not in range(1,199) or (source == destination):
        return "Please provide valid source and destination numbers", 400
    r1 = requests.post("http://localhost:5000/api/v1/db/read", json = {"collection":"Ride", "jsonobj" : {"source" : source, "destination":destination}, "fields":["rideId", "username","timestamp"]})
    if len(r1.json())==0:
        return jsonify(r1.json()), 204, {"Content-type":"application/json"}
    else:
        return jsonify(get_correct_rides(r1.json())), 200, {"Content-type":"application/json"}


@app.route('/api/v1/rides/<rideId>', methods = ["GET"])
#Status codes 200 204 405
def list_ride_details(rideId):
    r1 = requests.post("http://localhost:5000/api/v1/db/read", json = {"collection":"Ride", "jsonobj" : {"rideId" : rideId}, "fields":[]})
    if len(r1.json())==0:
        return jsonify({}), 204
    else:
        return jsonify(r1.json()), 200, {"Content-type":"application/json"}

@app.route('/api/v1/rides/<rideId>' , methods = ["POST"])
#Status code 200, 204, 405
def join_ride(rideId):
    username = request.get_json()["username"]
    r1 = requests.post("http://localhost:5000/api/v1/db/read", json = {"collection":"User", "jsonobj" : {"username" : username}, "fields":[]})
    if len(r1.json())==0: #someone check this later
        return "Username does not exist", 400
    r1 = requests.post("http://localhost:5000/api/v1/db/read", json = {"collection":"Ride", "jsonobj" : {"rideId" : rideId}, "fields":[]})
    if len(r1.json())==0: #someone check this later
        return "Ride does not exist", 400
    obj = r1.json()[0]
    if username in obj["users"]:
        return jsonify({}), 200
    else:
        obj["users"].append(username)
        r1 = requests.post("http://localhost:5000/api/v1/db/write", json = {"collection":"Ride", "jsonobj" : [obj], "action":"update"})
        if r1.status_code == 200:
            return jsonify({}), 200
        else:
            return "a", 400 #check

@app.route('/api/v1/rides/<rideId>', methods=["DELETE"])
#STatus codes 200 405
def delete_ride(rideId):
    r1 = requests.post("http://localhost:5000/api/v1/db/read", json = {"collection":"Ride", "jsonobj" : {"rideId" : rideId}, "fields":[]})
    if len(r1.json())==0: #someone check this later
        return "Ride does not exist", 400
    r =requests.post("http://localhost:5000/api/v1/db/write", json = {"collection":"Ride", "jsonobj" : {"rideId":rideId} , "action":"delete"})
    if r.status_code == 200 or r.status_code==204:
        return jsonify({}), 200
    else:
        return "Delete Failed", 400

@app.route('/api/v1/db/write', methods=["POST"])
def write_db():
    #Getting requried objects from request

    action = request.get_json()["action"]
    jsonobj = request.get_json()["jsonobj"]
    collection = request.get_json()["collection"]

    if action == "delete":
        try:
            dbapi.delete(collection, jsonobj)
        except mongoengine.errors.DoesNotExist:
            return jsonify({}), 200
        else:
            return jsonify({}), 200

    elif action == "insert":
        try:
            dbapi.insert(collection, jsonobj)
        except (mongoengine.errors.ValidationError, mongoengine.errors.NotUniqueError):
            return "Insert Error", 400
        else:
            return jsonify({}), 200
    elif action == "update":
        dbapi.update(collection, jsonobj)
        return jsonify({}), 200

@app.route('/api/v1/db/read',methods=["POST"])
def read_db():
    #Getting requried objects from request
    collection = request.get_json()["collection"]
    jsonobj = request.get_json()["jsonobj"]
    fields = request.get_json()["fields"]

    return dbapi.query(collection, jsonobj, fields), 200, {"Content-type":"application/json"}

