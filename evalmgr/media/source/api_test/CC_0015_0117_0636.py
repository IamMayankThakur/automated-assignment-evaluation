import pymongo
from flask import abort, request, jsonify, Flask , Response
from random import randint
import enum
import requests
import json

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
app = Flask(__name__)

mydb = myclient["Assignment1"]
ridesCol = mydb["rides"]
usersCol = mydb["users"]
rideId = set()


def is_sha1(maybe_sha):
    if len(maybe_sha) != 40:
        return False
    try:
        sha_int = int(maybe_sha, 16)
    except ValueError:
        return False
    return True


def validate_timestamp(t):
    temp = t.split(':')
    date1 = temp[0]
    time1 = temp[1]
    time = time1.split('-')
    date = date1.split('-')
    if len(date) != 3 or len(time) != 3:
        return False
    if int(date[0]) <= 31 and int(date[1]) <= 12:
        if int(time[0]) <= 60 and int(time[1]) <= 60 and int(time[2]) <= 12:
            return True
    return False


def generate_id():
    l = [1]
    while l:
        n = randint(1, 9999)
        query = {"rideId": n}
        doc = ridesCol.find(query)
        l = []
        for x in doc:
            l.append(x)
    return n


@app.route("/api/v1/users", methods=["PUT"])  # 1
def add_users():
    try:
        data = request.get_json()
    except:
        return {"success": "false"}, 400, {"ContentType": "application/json"}

    if not is_sha1(data["password"]):
        return {"success": "false"}, 400, {"ContentType": "application/json"}

    if not(data["username"] or data["password"]):
        return {"success": "false"}, 400, {"ContentType": "application/json"}

    query = {"username": data["username"]}
    doc = usersCol.find(query)
    l = []
    for x in doc:
        l.append(x)
    if l:
        return {"success": "false"}, 400

    data["table"] = 'users'
    data['type'] = 'insert'
    response = requests.post(
        "http://localhost:5000/api/v1/db/write", data=json.dumps(data))

    if response.status_code == 201:
        return {"success": "true"}, 201, {"ContentType": "application/json"}

    return {"success": 'false'}, 400


@app.route("/api/v1/users/<username>", methods=["DELETE"])  # 2
def remove_user(username):
    data = ""
    try:
        data = request.get_json()
    except:
        pass
    if data or not username:
        return {"success": "false"}, 400

    query = {"username": username}
    doc = usersCol.find(query)
    l = []
    for x in doc:
        l.append(x)
    if not l:
        return {"success": "false"}, 400

    data['table'] = 'users'
    data['type'] = 'delete'
    data['username'] = username

    response = requests.post(
        "http://localhost:5000/api/v1/db/write", data=json.dumps(data))

    if response.status_code == 200:
        return {"success": 'true'}, 200

    return {"success": 'false'}, 400


@app.route("/api/v1/rides", methods=["POST", "GET"])  # 3 and 4
def create_ride():
    if request.method == "POST":

        try:
            data = request.get_json()
        except:
            return {"success": "false"}, 400

        if not(data["created_by"] or data["timestamp"] or data["source"] or data["destination"]):
            return {"sucess": "false"}, 400

        query = {"username": data["created_by"]}
        doc = usersCol.find(query)
        l = []
        for x in doc:
            l.append(x)

        if not l:
            return {"success": "false"}, 400

        data['table'] = 'rides'
        data['type'] = 'insert'
        response = requests.post(
            "http://localhost:5000/api/v1/db/write", data=json.dumps(data))

        if response.status_code == 201:
            return {"success": "true"}, 201

    elif request.method == "GET":

        data = request.get_json()
        if data:
            return {"success": "false"}, 400

        source = request.args.get("source")
        destination = request.args.get("destination")

        query = {"source": source, "destination": destination}
        doc = ridesCol.find(query)
        l = []
        for x in doc:
            l.append(x)
        if not l:
            return {"success": "empty body"}, 204

        data['table'] = 'rides'
        data['type'] = 'read'
        data['source'] = source
        data['destination'] = destination
        response = requests.post(
            "http://localhost:5000/api/v1/db/read", data=json.dumps(data))

        if response.status_code == 400:
            return {"success": "false"}, 400

        elif response.status_code == 200:
            data1 = response.json()
            final = []
            for x in data1:
                temp = {}
                temp['rideId'] = x['rideId']
                temp['username'] = x["created_by"]
                temp['timestamp'] = x['timestamp']
                final.append(temp)

            return jsonify(final), 200


# 5 and 6 and 7
@app.route("/api/v1/rides/<rideId>", methods=["GET", "POST", "DELETE"])
def list_details(rideId):

    if request.method == "GET":
        data = request.get_json()
        if data:
            return {"success": "false"}, 400

        data = {}
        data['table'] = 'rides'
        data['type'] = 'rideId'
        data['rideId'] = rideId
        response = requests.post(
            "http://localhost:5000/api/v1/db/read", data=json.dumps(data))

        if response.status_code == 204:
            return {"success": "empty body"}, 204

        elif response.status_code == 200:
            data1 = response.json()
            return data1, 200

    elif request.method == "POST":
        try:
            data = request.get_json()
        except:
            return {"success": "false"}, 400

        data['rideId'] = rideId
        data['table'] = 'rides'
        data['type'] = 'join'

        response = requests.post(
            "http://localhost:5000/api/v1/db/write", data=json.dumps(data))

        if response.status_code == 204:
            return {"success": "false"}, 204
        elif response.status_code == 200:
            return {"success": "true"}, 200

    elif request.method == "DELETE":
        data = request.get_json()
        if data:
            return {"success": "false"}, 400

        data = {}
        data['table'] = 'rides'
        data['type'] = 'delete'
        data['rideId'] = rideId

        response = requests.post(
            "http://localhost:5000/api/v1/db/write", data=json.dumps(data))

        if response.status_code == 204:
            return {"success": "false"}, 204

        elif response.status_code == 200:
            return {"success": 'true'}, 200


@app.route("/api/v1/db/write", methods=["POST"])
def write():

    data = request.get_data()
    data = json.loads(data)

    if data['table'] == 'users':
        if data['type'] == 'insert':
            # data to be inserted
            temp = {"username": data["username"], 'password': data['password']}
            a = usersCol.insert(temp)
            return Response(None,201,mimetype="application/json")

        elif data['type'] == 'delete':
            temp = {"username": data['username']}
            usersCol.delete_one(temp)
            return Response(None,200,mimetype="application/json")

    elif data['table'] == 'rides':
        if data['type'] == 'insert':
            n = generate_id()
            temp = {"rideId": n, "created_by": data["created_by"], "users": [], "timestamp": data["timestamp"],
                    "source": data["source"], "destination": data["destination"]}

            a = ridesCol.insert(temp)
            return Response(None,201,mimetype="application/json")

        elif data['type'] == 'join':
            queryUser = {"username": data['username']}
            queryRide = {"rideId": int(data['rideId'])}

            docU = usersCol.find(queryUser)
            docR = ridesCol.find(queryRide)
            lU = []
            lR = []

            for x in docU:
                lU.append(x)
            for x in docR:
                lR.append(x)
            # if lR['created_by']==data['username']:
            #     return {"success":"false"},400

            if not lU or not lR:
                return Response(None,204,mimetype="application/json")

            lR[0]['users'].append(data['username'])
            query = {"rideId": int(data['rideId'])}
            new = {"$set": {"users": lR[0]['users']}}
            ridesCol.update_one(query, new)
            return Response(None,200,mimetype="application/json")

        elif data['type'] == 'delete':
            query = {"rideId": int(data['rideId'])}

            doc = ridesCol.find(query)

            l = []
            for x in doc:
                l.append(x)
            print(l)

            if not l:
                return {"success": "false"}, 204

            ridesCol.delete_one(query)

            return Response(None,200,mimetype="application/json")


@app.route("/api/v1/db/read", methods=["POST"])
def read():

    data = request.get_data()
    data = json.loads(data)

    if data['table'] == 'rides':
        if data['type'] == 'read':

            temp = []
            query = {"source": data['source'],
                     "destination": data["destination"]}
            doc = ridesCol.find(query)

            for x in doc:
                if not validate_timestamp(x['timestamp']):
                    Response(None,400,mimetype="application/json")

                x.pop("_id")
                temp.append(x)
            # print("\n\n\n",temp,"\n\n\n")
            return Response(jsonify(temp),200,mimetype="application/json")

        elif data['type'] == 'rideId':

            query = {"rideId": int(data["rideId"])}
            doc = ridesCol.find(query)
            l = []
            for x in doc:
                l.append(x)

            if not l:
                return Response(None,204,mimetype="application/json")

            temp = l[0]
            temp.pop('_id')
            return Response(jsonify(temp),200,mimetype="application/json")


if __name__ == "__main__":
    app.debug = True
    app.run()
