import pymongo
from flask import abort, request, json, Flask, Response
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
    data = request.get_json()
    print(data)
    print("yee")
    print("\n")
    if not is_sha1(data["password"]):
        return Response(json.dumps({"success": "false"}),status=400,mimetype="application/json")

    if not(data["username"] or data["password"]):
        return Response(json.dumps({"success": "false"}),status=400,mimetype="application/json")

    query = {"username": data["username"]}
    print(query)
    doc = usersCol.find(query)
    l = []
    for x in doc:
        l.append(x)
    if l:
        return Response(json.dumps({"success": "false"}),status=400,mimetype="application/json")
    print("syee\n")
    data["table"] = 'users'
    data['type'] = 'insert'
    response = requests.post(
        "http://localhost:5000/api/v1/db/write", json=data)

    if response.status_code == 201:
        return Response(json.dumps({"success": "true"}),status=201,mimetype="application/json")

    return Response(json.dumps({"success": "false"}),status=400,mimetype="application/json")


@app.route("/api/v1/users/<username>", methods=["DELETE"])  # 2
def remove_user(username):
    try:
        data = request.get_json()
        print(data)
    except:
        pass
    if data or not username:
        return Response(json.dumps({"success": "false"}),status=400,mimetype="application/json")

    query = {"username": username}
    print(query)
    doc = usersCol.find(query)
    l = []
    for x in doc:
        l.append(x)
    if not l:
        return Response(json.dumps({"success": "false"}),status=400,mimetype="application/json")
    print("yee")
    data['table'] = 'users'
    data['type'] = 'delete'
    data['username'] = username

    response = requests.post(
        "http://localhost:5000/api/v1/db/write", json=data)

    if response.status_code == 200:
        return Response(json.dumps({"success": 'true'}),status=200,mimetype="application/json")

    return Response(json.dumps({"success": "false"}),status=400,mimetype="application/json")


@app.route("/api/v1/rides", methods=["POST", "GET"])  # 3 and 4
def create_ride():
    if request.method == "POST":

        try:
            data = request.get_json()
            print(data)
        except:
            return Response(json.dumps({"success": "false"}),status=400,mimetype="application/json")

        if not(data["created_by"] or data["timestamp"] or data["source"] or data["destination"]):
            return Response(json.dumps({"success": "false"}),status=400,mimetype="application/json")

        query = {"username": data["created_by"]}
        doc = usersCol.find(query)
        l = []
        for x in doc:
            l.append(x)
        print(query)

        if not l:
            return Response(json.dumps({"success": "false"}),status=400,mimetype="application/json")
        print("yee")

        data['table'] = 'rides'
        data['type'] = 'insert'
        response = requests.post(
            "http://localhost:5000/api/v1/db/write", json=data)
        print("syee")

        if response.status_code == 201:
            return Response(json.dumps({"success": "true"}),status=201,mimetype="application/json")

    elif request.method == "GET":

        data = request.get_json()
        if data:
            return Response(json.dumps({"success": "false"}),status=400,mimetype="application/json")

        source = request.args.get("source")
        destination = request.args.get("destination")

        query = {"source": source, "destination": destination}
        doc = ridesCol.find(query)
        l = []
        for x in doc:
            l.append(x)
        if not l:
            return Response(json.dumps({"success": "empty body"}),status=204,mimetype="application/json")

        data['table'] = 'rides'
        data['type'] = 'read'
        data['source'] = source
        data['destination'] = destination
        response = requests.post(
            "http://localhost:5000/api/v1/db/read", json=data)

        if response.status_code == 400:
            return Response(json.dumps({"success": "false"}),status=400,mimetype="application/json")

        elif response.status_code == 200:
            data1 = response.json()
            final = []
            for x in data1:
                temp = {}
                temp['rideId'] = x['rideId']
                temp['username'] = x["created_by"]
                temp['timestamp'] = x['timestamp']
                final.append(temp)

            return Response(json.dumps(final),status=200,mimetype="application/json")


# 5 and 6 and 7
@app.route("/api/v1/rides/<rideId>", methods=["GET", "POST", "DELETE"])
def list_details(rideId):

    if request.method == "GET":
        data = request.get_json()
        if data:
            return Response(json.dumps({"success": "false"}),status=400,mimetype="application/json")

        data = {}
        data['table'] = 'rides'
        data['type'] = 'rideId'
        data['rideId'] = rideId
        response = requests.post(
            "http://localhost:5000/api/v1/db/read", json=data)

        if response.status_code == 204:
            return Response(json.dumps({"success": "empty body"}),status=204,mimetype="application/json")

        elif response.status_code == 200:
            data1 = response.json()
            return Response(json.dumps(data1),status=200,mimetype="application/json")

    elif request.method == "POST":
        try:
            data = request.get_json()
        except:
            return Response(json.dumps({"success": "false"}),status=400,mimetype="application/json")

        data['rideId'] = rideId
        data['table'] = 'rides'
        data['type'] = 'join'

        response = requests.post(
            "http://localhost:5000/api/v1/db/write", json=data)

        if response.status_code == 204:
            return Response(json.dumps({"success": "false"}),status=204,mimetype="application/json")
        elif response.status_code == 200:
            return Response(json.dumps({"success": "true"}),status=200,mimetype="application/json")

    elif request.method == "DELETE":
        data = request.get_json()
        if data:
            return Response(json.dumps({"success": "false"}),status=400,mimetype="application/json")

        data = {}
        data['table'] = 'rides'
        data['type'] = 'delete'
        data['rideId'] = rideId

        response = requests.post(
            "http://localhost:5000/api/v1/db/write", json=data)

        if response.status_code == 204:
            return Response(json.dumps({"success": "false"}),status=204,mimetype="application/json")

        elif response.status_code == 200:
            return Response(json.dumps({"success": 'true'}),status=200,mimetype="application/json")


@app.route("/api/v1/db/write", methods=["POST"])
def write():

    data = request.get_json()
    print(data)
    if data['table'] == 'users':
        if data['type'] == 'insert':
            # data to be inserted
            temp = {"username": data["username"], 'password': data['password']}
            a = usersCol.insert(temp)
            print("hey")
            return Response(json.dumps({"success": 'true'}),status=201,mimetype="application/json")

        elif data['type'] == 'delete':
            temp = {"username": data['username']}
            usersCol.delete_one(temp)
            return Response(json.dumps({"success": 'true'}),status=200,mimetype="application/json")

    elif data['table'] == 'rides':
        if data['type'] == 'insert':
            n = generate_id()
            temp = {"rideId": n, "created_by": data["created_by"], "users": [], "timestamp": data["timestamp"],
                    "source": data["source"], "destination": data["destination"]}

            a = ridesCol.insert(temp)
            return Response(json.dumps({"success": "true"}),status=201,mimetype="application/json")

        elif data['type'] == 'join':
            print(data)
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
            print(queryUser)
            print(queryRide)
            print("yee")

            if not lU or not lR:
                return Response(json.dumps({"success": "false"}),status=204,mimetype="application/json")

            print("hey")
            lR[0]['users'].append(data['username'])
            query = {"rideId": int(data['rideId'])}
            new = {"$set": {"users": lR[0]['users']}}
            print(query)
            ridesCol.update_one(query, new)
            print("heyy")
            return Response(json.dumps({"success": "true"}),status=200,mimetype="application/json")

        elif data['type'] == 'delete':
            query = {"rideId": int(data['rideId'])}

            doc = ridesCol.find(query)

            l = []
            for x in doc:
                l.append(x)
            print(l)

            if not l:
                return Response(json.dumps({"success": "false"}),status=204,mimetype="application/json")

            ridesCol.delete_one(query)

            return Response(json.dumps({"success": "true"}),stauts=200,mimetype="application/json")


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
                    return Response(json.dumps({"success": "false"}),status=400,mimetype="application/json")

                x.pop("_id")
                temp.append(x)
            # print("\n\n\n",temp,"\n\n\n")
            return json.dumps(temp), 200

        elif data['type'] == 'rideId':

            query = {"rideId": int(data["rideId"])}
            doc = ridesCol.find(query)
            l = []
            for x in doc:
                l.append(x)

            if not l:
                return Response(json.dumps({"success": "empty body"}),status=204,mimetype="application/json")

            temp = l[0]
            temp.pop('_id')
            return Response(json.dumps(temp),status=200,mimetype="application/json")


if __name__ == "__main__":
    app.debug = True
    app.run()
