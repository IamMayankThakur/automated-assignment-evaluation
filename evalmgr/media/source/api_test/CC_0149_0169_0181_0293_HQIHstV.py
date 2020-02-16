from flask import Flask, request, jsonify, redirect, url_for, Response
from datetime import datetime
import time
from pymongo import MongoClient
import json, requests
import re, csv

app = Flask(__name__)

client = MongoClient("localhost", 27017)

def db_api(key, database, collection, mode):
    key_string = json.dumps(key)
    if mode == "read":
        json_string = {'query' : key_string, 'database' : database, 'collection' : collection}
        jstring = json.dumps(json_string)
        r = requests.post("http://127.0.0.1:8000/api/v1/db/read/", json=jstring)
        return r
    else:
        json_string = {'query' : key_string, 'database' : database, 'collection' : collection, "mode" : mode}
        jstring = json.dumps(json_string)
        r = requests.post("http://127.0.0.1:8000/api/v1/db/write/", json=jstring)
        return r

#Function to create new users.      
@app.route("/api/v1/users/", methods=['PUT'])
def create_user():
    try:
        try:
            username = request.json["username"]
            password = request.json["password"]
        except:
            return Response("", status="400", mimetype="application/json")

        u = db_api({'username':username},"users","users","read")

        if u.text == "400":
            if len(password) == 40 and re.match("([a-f0-9]{40})", password):
                insert = {'username' : username, 'password' : password}
                try:
                    r = db_api(insert,"users","users","insert")
                    if r.json():
                        return Response("{}", status="201", mimetype="application/json")
                    else:
                        return Response("", status="500", mimetype="application/json")
                except:
                    return Response("", status="500", mimetype="application/json")

            else:
                return Response("", status="400", mimetype="application/json")
        
        else:
            return Response("", status="400", mimetype="application/json")
        
    except:
        return Response("", status="500", mimetype="application/json")

#Function to delete users.
@app.route("/api/v1/users/<username>", methods=['DELETE'])
def delete_user(username):
    """
       Function to delete users.
       """
    try:
        u = db_api({'username':username},"users","users","read")

        if u.text == "400":
            return Response("Username does not exist", status="400", mimetype="application/json")
 
        else:
            delete = {'username' : username}
            try:
                ur = db_api({"created_by":username},"rides","rides","read")
                if ur.text == "400":
                    r = db_api(delete,"users","users","delete")
                    if r.text == "200":
                        return Response("{}", status="200", mimetype="application/json")
                    else:
                        return Response("", status="500", mimetype="application/json")
                else:
                    return Response("this user cannot be deleted as he is associated with a ride", status="400", mimetype="application/json")
            except:
                return Response("", status="500", mimetype="application/json")
        
    except:
        return Response("", status="500", mimetype="application/json")

#Function to create a new ride.
@app.route("/api/v1/rides", methods=['POST'])
def create_ride():
    db_api({'name':'rideId','rideId':'1000'},"rides","id","insert")
    r = db_api({'name': "rideId"},"rides","id","read")
    rideId = int(r.text)
    try:
        try:
            username = request.json["created_by"]
            timestamp = request.json["timestamp"]
            try:
                time.strptime(timestamp,"%d-%m-%Y:%S-%M-%H")
                timestamp2 = str(datetime.now().replace(microsecond=0))
                t1 = datetime.strptime(timestamp, "%d-%m-%Y:%S-%M-%H")
                t2 = datetime.strptime(timestamp2, "%Y-%m-%d %H:%M:%S")
                if(t2>t1):
                    return Response ("",status=400, mimetype="application/json")
            except:
                return Response ("",status=400, mimetype="application/json")
            source = request.json["source"]
            destination = request.json["destination"]
            if source == destination:
                return Response ("",status=400, mimetype="application/json")
            csv_data = []
            c1 = []
            try:
                with open('AreaNameEnum.csv', 'r') as f:
                  reader = csv.reader(f)
                  csv_data = list(reader)
                for ij in csv_data:
                    c1.append(int(ij[0]))
            except:
                return Response("", status="500", mimetype="application/json")

            if(int(source) in c1 and int(destination) in c1):
                pass
            else:
                return Response("", status="400", mimetype="application/json")
                
        except:
            return Response("", status="400", mimetype="application/json")
        u = db_api({'username':username},"users","users","read")
        if u.text == "400":
            return Response("", status="400", mimetype="application/json")
        else:
            insert = {'rideId' : int(rideId),'created_by' : username, 'users' : [], 'timestamp' : timestamp, 'source' : source, 'destination' : destination}
            try:
                r = db_api(insert,"rides","rides","insert")
                if r.json():
                    rideId += 1
                    r2 = db_api({'rideId' : str(rideId)},"rides","id","update")
                    if r2.text == "201":
                        return Response("{}", status="201", mimetype="application/json")
                    else:
                        return Response("", status="500", mimetype="application/json")                    
            except:
                return Response("", status="500", mimetype="application/json")        
    except:
        return Response("", status="500", mimetype="application/json")

#Function to show rides for a given source and destination.
@app.route("/api/v1/rides", methods=['GET'])
def show_rides():
    try:
        
        try:
            source = request.args['source']
            destination = request.args['destination']
        except:
            try:
                if(request.get_json()):
                    return Response("", status="405", mimetype="application/json")
            except:
                pass
            return Response("", status="400", mimetype="application/json")

        csv_data = []
        c1 = []
        try:
            with open('AreaNameEnum.csv', 'r') as f:
              reader = csv.reader(f)
              csv_data = list(reader)
            for ij in csv_data:
                c1.append(int(ij[0]))
        except:
            return Response("", status="500", mimetype="application/json")

        if(int(source) in c1 and int(destination) in c1):
            ride = db_api({'source' : int(source), 'destination' : int(destination)},"rides","rides","read")
        else:
            return Response("", status="400", mimetype="application/json")
            

        if ride.text == "400":
            return Response("", status="204", mimetype="application/json")
        return Response(ride.content, status="200", mimetype="application/json")
        
    except:
        return Response("", status="500", mimetype="application/json")

#Function to list details of a given ride.
@app.route("/api/v1/rides/<rideId>", methods=['GET'])
def ride_details(rideId):
    try:

        r = db_api({'rideId': int(rideId)},"rides","rides","read")

        if r.text == "400":
            return Response("", status="204", mimetype="application/json")
            
        else:
            return Response(r.content, status="200", mimetype="application/json")
                    
    except:
        return Response("", status="500", mimetype="application/json")

#Function to add user to a ride.
@app.route("/api/v1/rides/<rideId>", methods=['POST'])
def add_user_to_ride(rideId):
    try:
        try:
            username = request.json["username"]
        except:
            return Response("", status="405", mimetype="application/json")

        u = db_api({'username':username},"users","users","read")

        if u.text != "400":
            r = db_api({'rideId': int(rideId)},"rides","rides","read")

            if r.text == "400":
                return Response("", status="400", mimetype="application/json")

            else:
                ur = db_api({'rideId': int(rideId), "username": username},"rides","rides","update")
                if ur.text == "400":
                    return Response("", status="400", mimetype="application/json")
                return Response("{}", status="200", mimetype="application/json")
        
        else:
            return Response("", status="400", mimetype="application/json")
        
    except:
        return Response("", status="500", mimetype="application/json")

#Function to delete rides.
@app.route("/api/v1/rides/<rideId>", methods=['DELETE'])
def delete_ride(rideId):
    try:
        r = db_api({'rideId': int(rideId)},"rides","rides","read")
        if r.text != "400":
            db_api({'rideId': int(rideId)},"rides","rides","delete")
            return Response("{}", status="200", mimetype="application/json")
        else:
            return Response("", status="405", mimetype="application/json")        
    except:
        return Response("", status="500", mimetype="application/json")

#Function to write to the DB.
@app.route("/api/v1/db/write/", methods=['POST'])
def write_db():
    r_db = client.rides
    r_col = r_db.rides
    ridesIdcol = r_db.id

    u_db = client.users
    u_col = u_db.users

    try:

        try:
            ins = request.json
            insert_data = json.loads(ins)

            query = json.loads(insert_data["query"])
            collection = insert_data["collection"]
            database = insert_data["database"]
            mode = insert_data["mode"]

        except:
            return Response("", status="400", mimetype="application/json")

        if mode == "insert":
            if database == "rides":
                if collection == "rides":
                    ride_id = r_col.insert(query)
                    find = r_col.find_one({'_id' : ride_id})
                    output = {'created_by' : find['created_by'], 'rideId' : find['rideId'], 'users' : find['users'], 'timestamp' : find['timestamp'], 'source' : find['source'], 'destination' : find['destination']}
                    return jsonify({'result' : output})

                else:
                    if collection == "id":
                        i = ridesIdcol.find_one({'name': 'rideId'})
                        if i:
                            return
                        else:
                            ridesIdcol.insert(query)
                            return
            
            else:
                if database == "users":
                    user_id = u_col.insert(query)
                    new_user = u_col.find_one({'_id' : user_id})
                    output = {'username' : new_user['username'], 'password' : new_user['password']}
                    return jsonify(output)

        else:
            if mode == "update":
                if collection == "rides":
                    ur = r_col.find_one({'rideId':query['rideId']})
                    if query['username'] in ur['users']:
                        return "400"
                    r_col.find_one_and_update({'rideId' : query['rideId']},{"$push": {"users": query['username']}})
                    return Response("", status="200", mimetype="application/json")

                else:
                    ridesIdcol.find_one_and_update({'name': 'rideId'},{"$set": {"rideId": str(query['rideId'])}})
                    return "201"
            else:
                if database == "users":
                    u_col.find_one_and_delete({'username' : query['username']})
                    return "200"


                else:
                    r_col.find_one_and_delete({'rideId' : query['rideId']})
                    return "200"        
    except:
        return Response("Service Unavailable", status="500", mimetype="application/json")

#Function to read from the DB.
@app.route("/api/v1/db/read/", methods=['POST'])
def read_db():
    r_db = client.rides
    r_col = r_db.rides
    ridesIdcol = r_db.id

    u_db = client.users
    u_col = u_db.users

    try:

        try:
            read = request.json
            read_data = json.loads(read)

            query = json.loads(read_data['query'])
            collection = read_data["collection"]
            database = read_data["database"]

        except:
            return "400"

        if database == "rides":
            if collection == "rides":
                if 'rideId' in query:
                    find = r_col.find_one(query)
                    if find:
                        output = {'created_by' : find['created_by'], 'rideId' : find['rideId'], 'users' : find['users'], 'timestamp' : find['timestamp'], 'source' : find['source'], 'destination' : find['destination']}
                        return jsonify(output)
                    else:
                        return "400"
                else:
                    ride = r_col.find(query)
                    output = []
                    for r in ride:
                        out = {"rideId":r['rideId'], "timestamp":r['timestamp'], "created_by":r['created_by']}                
                        timestamp2 = str(datetime.now().replace(microsecond=0))
                        timestamp_obj = datetime.strptime(out["timestamp"], "%d-%m-%Y:%S-%M-%H")
                        current_date_obj = datetime.strptime(timestamp2, "%Y-%m-%d:%H-%M-%S")
                        if (timestamp_obj >= current_date_obj):
                            output.append(out)
                    if output:
                        return jsonify(output)
                    else:
                        return "400"

            else:
                if collection == "id":
                    
                    find = ridesIdcol.find_one(query)
                    if find:
                        return find['rideId']
                    else:
                        return "400"
            
        else:
            if database == "users":
                find = u_col.find_one(query)
                if find:
                    output = {'username' : find['username'], 'password' : find['password']}
                    return jsonify(output)
                else:
                    return "400"        
    except:
        return Response("", status="500", mimetype="application/json")

if __name__ == '__main__':
    app.run(debug=True)