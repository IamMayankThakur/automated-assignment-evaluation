from requests import post
from datetime import datetime
from csv import reader

from flask import *
from pymongo import MongoClient
from re import compile

app = Flask(__name__)

enums = list()
with open('AreaNameEnum.csv') as csv_file:
    csv_reader = reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            line_count = 1
            continue
        enums.append(row[1].lower())

client = MongoClient("mongodb://localhost:27017/")
db = client["rideshare"]
users = db["users"]
rides = db["rides"]

@app.route('/api/v1/users', methods=["PUT"])
def add_user():
    rjson = request.get_json()
    rkeys = list(rjson.keys())

    if not rjson:
        return Response("invalid request", 400)
    elif not "username" in rkeys:
        return Response("invalid request", 400)
    elif not "password" in rkeys:
        return Response("invalid request", 400)
    password = rjson['password']
    pattern = compile(r'\b[0-9a-fA-F]{40}\b')
    match = pattern.match(password)

    if not match:
        return Response("invalid request", 400)

    wjson = {"data" : rjson, "table" : "user", "action" : "check"}
    read = post("http://35.174.170.204/api/v1/db/read", json=wjson)
    print(read.status_code)

    if read.status_code == 400:
        return Response('user already exists', 400)
    
    wjson = {"data" : rjson, "table" : "user", "action" : "add"}
    wjson["data"]["ride"] = ""
    write = post("http://35.174.170.204/api/v1/db/write", json=wjson)

    return Response("{}",status=201,mimetype="application/json")

@app.route('/api/v1/users/<username>', methods=["DELETE"])
def remove_user(username):
    data = {"username" : username}
    wjson = {"data" : data, "table" : "user", "action" : "check"}
    
    read = post("http://35.174.170.204/api/v1/db/read", json=wjson)

    if read.status_code == 200:
        return Response('user not found', 400)
    

    wjson = {"data" : data, "table" : "user", "action" : "delete"}
    write = post("http://35.174.170.204/api/v1/db/write", json=wjson)

    print(write.text)

    return Response(f'user {username} has been removed', 200)

@app.route('/api/v1/rides', methods=["POST"])
def create_new_ride():
    rjson = request.get_json()
    rkeys = list(rjson.keys())
    
    if not rjson:
        return Response("invalid request", 400)
    elif not "created_by" in rkeys:
        return Response("invalid request", 400)
    elif not "timestamp" in rkeys:
        return Response("invalid request", 400)
    elif not "source" in rkeys:
        return Response("invalid request", 400)
    elif not "destination" in rkeys:
        return Response("invalid request", 400)

    data = {"username" : rjson["created_by"]}
    wjson = {"data" : data, "table" : "user", "action" : "check"}
    read = post("http://35.174.170.204/api/v1/db/read", json=wjson)
    if read.status_code == 200:
        return Response('user not found', 400)
    dtimestamp = 0
    try:
        dtimestamp =  datetime.strptime(rjson["timestamp"], "%d-%m-%Y:%S-%M-%H")
    except ValueError:
        return Response('invalid timestamp', 400)

    rjson['source'] = rjson['source'].lower()
    rjson['destination'] = rjson['destination'].lower()

    if not rjson['source'] in enums:
        return Response('invalid source', 400)
    elif not rjson['destination'] in enums:
        return Response('invalid destination', 400)
    elif rjson['source'] == rjson['destination']:
        return Response('source and destination cannot be same', 400)

    data = rjson
    data["members"] = list()
    data["members"].append(data["created_by"])

    wjson = dict()
    wjson = {"data" : data, "table" : "ride", "action" : "create"}

    write = post("http://35.174.170.204/api/v1/db/write", json=wjson)
    if write.status_code == 400:
        return Response('database error', 500)

    return Response('ride created successfully', 200)


@app.route('/api/v1/rides', methods=["GET"])
def list_rides():
    source = request.args.get('source')
    if not source:
        return Response('invalid source request', 400)

    destination = request.args.get('destination')
    if not destination:
        return Response('invalid destination request', 400)

    source = int(source)
    if source > len(enums):
        return Response('invalid source request', 400)
 
    destination = int(destination)
    if destination > len(enums):
        return Response('invalid destination request', 400)

    source = enums[source-1]
    destination = enums[destination-1]

    data = {"source" : source, "destination" : destination}
    wjson = {"data" : data, "table" : "ride", "action" : "list"}
    read = post("http://35.174.170.204/api/v1/db/read", json=wjson)

    print(read.json())

    ret_str = ""
    for entry in read.json():
        ret_str += f"{entry}\n"


    return Response(ret_str, 200)


@app.route('/api/v1/rides/<rideId>', methods=["GET"])
def get_details(rideId):
    wjson = {"data" : rideId, "table" : "ride", "action" : "get"}
    read = post("http://35.174.170.204/api/v1/db/read", json=wjson)

    if read.status_code == 404:
        return Response(f'no ride with id {rideId} found', 400)
    
    return Response(f'{read.json()}', 200)

@app.route('/api/v1/rides/<rideId>', methods=["POST"])
def join_ride(rideId):

    wjson = {"data" : rideId, "table" : "ride", "action" : "get"}
    read = post("http://35.174.170.204/api/v1/db/read", json=wjson)
    if read.status_code == 404:
        return Response(f'no ride with id {rideId} found', 400)
 
    rjson = request.get_json()
    rkeys = list(rjson.keys())
    
    if not rjson:
        return Response("invalid request", 400)
    elif not "username" in rkeys:
        return Response("invalid request", 400)
    data = rjson
    data["id"] = rideId
    wjson = {"data" : data, "table" : "ride", "action" : "is_member"}
    read = post("http://35.174.170.204/api/v1/db/read", json=wjson)
    if read.status_code == 400:
        return Response('already memeber of ride', 400)

    
    wjson = {"data" : data, "table" : "ride", "action" : "join"}
    write = post("http://35.174.170.204/api/v1/db/write", json=wjson)

    if write.status_code == 500:
        return Response('database error', 500)

    return 'ok', 200


@app.route('/api/v1/rides/<rideId>', methods=["DELETE"])
def delete_ride(rideId):
    wjson = {"data" : rideId, "table" : "ride", "action" : "get"}
    read = post("http://35.174.170.204/api/v1/db/read", json=wjson)
    if read.status_code == 404:
        return Response(f'no ride with id {rideId} found', 400)


    wjson = {"data" : rideId, "table" : "ride", "action" : "delete"}
    write = post("http://35.174.170.204/api/v1/db/write", json=wjson)
    if write.status_code == 500:
        return Response('database error', 500)

    return Response('', 200)


@app.route('/api/v1/db/write', methods=["POST"])
def write_to_db():
    rjson = request.get_json()
    if rjson['table'] == "user":
        if rjson["action"] == "add":
            query = users.insert_one(rjson["data"])
            if not query:
                return Response('', 400)

        elif rjson["action"] == "delete":
            query = users.delete_one(rjson["data"])
            if not query:
                return Response('', 400)
    elif rjson["table"] == "ride":
        if rjson["action"] == "create":
            query = rides.insert_one(rjson["data"])
            if not query:
                return Response('', 400)

        if rjson["action"] == "join":
            data = rjson['data']
            query=rides.find()
            n = 0
            for i in query:
                n += 1
                if n == int(data['id']):
                    y = i['members']
                    y.append(data['username'])
                    change = {"$set":{'members':y}}
                    rides.find_one_and_replace({'_id' : i['_id']}, i)
                    return Response('',200)

        if rjson["action"] == "delete":
            query=rides.find()
            n = 0
            for i in query:
                n += 1
                if n == int(rjson['data']):
                    rides.delete_one(i)

                return Response('',200)


            return Response('error', 400)

    return Response("boom", 200)

@app.route('/api/v1/db/read', methods=["POST"])
def read_from_db():
    rjson = request.get_json()
    if rjson["table"] == "user":
        if rjson["action"] == "check":
            query = users.find(rjson["data"])
            for i in query:
                if i:
                    return Response('user already exists', 400)

    elif rjson["table"] == "ride":

        if rjson["action"] == "list":
            print("query: ", rjson["data"])
            query = rides.find()
            resp = list()
            n = 0
            for i in query:
                n += 1
                if i['source'] == rjson['data']['source'] and i['destination'] == rjson['data']['destination']:
                    resp.append({'rideId' : f'{n}', 'username' : i['created_by'], 'timestamp' : i['timestamp']})

            if not n:
                return Response('no rides found', 404)
            else:
                print(resp)
                return jsonify(resp)

        elif rjson["action"] == "get":
            query=rides.find()
            n = 0
            for i in query:
                n += 1
                if n == int(rjson["data"]):
                    resp = list()
                    resp.append({'rideId' : f'{n}', 'created_by' : i['created_by'], 'users' : i['members'], 'timestamp' : i['timestamp'],
                        'source' : i['source'], 'destination' : i['destination']})
                    print("read.... a:", resp)

                    return jsonify(resp)
            return Response('ride not found', 404)

        elif rjson["action"] == "is_member":
            data = rjson['data']
            query=rides.find()
            n = 0
            for i in query:
                n += 1
                if n == int(data['id']):
                    if data["username"] in i['members']:
                        return Response('', 400)


        return Response('ok', 200)


