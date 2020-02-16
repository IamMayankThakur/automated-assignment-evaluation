from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from models import app, db, Rides, User
import requests
from datetime import datetime

ip = "52.207.1.214"

# API 1
# Add user
@app.route("/api/v1/users",methods=['PUT'])
def add_user():
    if(request.method!='PUT'):
        abort(405)
    req_params = request.get_json()
    if req_params == None:
        abort(400)
    username=req_params["username"]
    password=req_params["password"]
    try:
        hexp=int(password,16)
        if(len(password)!=40):
            abort(400)
        query={"insert":[username,password],"table":"user","columns":["username","password"]}
        x=requests.post("http://" + ip + "/api/v1/db/write",json=query)
        if x.status_code != 200:
            abort(400)
        return("",201)
    except ValueError as e:
        print("Password Error")
        abort(400)

# API 2
# Remove user
@app.route("/api/v1/users/<username>",methods=['DELETE'])
def delete_user(username):
    if(request.method!='DELETE'):
        abort(405)
    find_query = {"table": "user", "columns": ["username"], "where": ["username={}".format(username)]}
    find_resp = requests.post("http://" + ip + "/api/v1/db/read", json=find_query)
    if len(find_resp.json()) == 0:
        abort(400)
    query={"where":["username={}".format(username)],"table":"user"}
    x=requests.delete("http://" + ip + "/api/v1/db/write",json=query)
    return (jsonify(),200)

# API 3
# Create a new ride
@app.route("/api/v1/rides",methods=['POST'])
def create_ride():
    if(request.method!='POST'):
        abort(405)
    req_params=request.get_json()
    if req_params == None:
        abort(400)
    created_by=req_params['created_by']
    old_date=req_params['timestamp']
    new_date=old_date[6:10]+'-'+old_date[3:5]+'-'+old_date[0:2]+':'+old_date[-2:]+'-'+old_date[-5:-3]+'-'+old_date[-8:-6]
    source=req_params['source']
    destination=req_params['destination']
    find_query = {"table": "user", "columns": ["username"], "where": ["username={}".format(created_by)]}
    find_resp = requests.post("http://" + ip + "/api/v1/db/read", json=find_query)
    if len(find_resp.json()) == 0:
        abort(400)
    query={"insert":[created_by,new_date,source,destination],"table":"rides","columns":["created_by","timestamp","source","destination"]}
    x=requests.post("http://" + ip + "/api/v1/db/write",json=query)
    if x.status_code != 200:
        abort(400)

    get_rideid_query = {"table": "rides", "columns": ["rideid"], "where": []}
    get_rideid_res = requests.post("http://" + ip + "/api/v1/db/read", json=get_rideid_query)
    if get_rideid_res.status_code != 200:
        abort(400)
    get_rideid_res = [l[0] for l in get_rideid_res.json()]
    rideid = max(get_rideid_res)

    get_userid_query = {"table": "user", "columns": ["id"], "where": ["username={}".format(created_by)]}
    get_userid_res = requests.post("http://" + ip + "/api/v1/db/read", json=get_userid_query)
    if get_userid_res.status_code != 200:
        abort(400)
    userid = get_userid_res.json()[0][0]

    users_query={"insert":[str(rideid), str(userid)],"table":"ride_user","columns":["rideid","userid"]}
    users_response=requests.post("http://" + ip + "/api/v1/db/write",json=users_query)
    if users_response.status_code != 200:
        abort(400)
    return ("",201)


#API 4
#List all upcoming rides for a given source and destination
@app.route("/api/v1/rides", methods = ['GET'])
def getRides():
    source = request.args.get('source')
    destn = request.args.get('destination')

    data = {"table": "rides", "columns": ["rideid", "created_by", "timestamp"], "where": ["source={}".format(source),"destination={}".format(destn)]}
    read_result = requests.post("http://" + ip + "/api/v1/db/read", json=data)

    if len(read_result.json()) == 0:
        abort(400)
    else:
        net_response = []
        now = datetime.now()
        for result in read_result.json():
            response = {}
            response["rideId"] = int(result[0])
            response["username"] = str(result[1])
            timestamp = datetime.strptime(result[2], "%a, %d %b %Y %H:%M:%S GMT")
            response["timestamp"] = timestamp.strftime("%d-%m-%Y:%S-%M-%H")
            if timestamp > now:
                net_response.append(response)
        if len(net_response) == 0:
            abort(400)
        return jsonify(net_response)


#API 5
#List all the details of a given ride
@app.route("/api/v1/rides/<rideId>", methods = ['GET'])
def getRideDetails(rideId):

    data = {"table": "rides", "columns": ["rideid", "created_by", "timestamp", "source", "destination"], "where": ["rideid={}".format(rideId)]}
    read_result = requests.post("http://" + ip + "/api/v1/db/read", json=data)
    if read_result.status_code != 200:
        abort(400)
    if len(read_result.json()) == 0:
        abort(400)
    else:
        userid_query = {"table": "ride_user", "columns": ["userid"], "where": ["rideid={}".format(rideId)]}
        userid_result = requests.post("http://" + ip + "/api/v1/db/read", json=userid_query)
        userid_result = [l[0] for l in userid_result.json()]
        user_list = []
        for userid in userid_result:
            user_query = {"table": "user", "columns": ["username"], "where": ["id={}".format(userid)]}
            user = requests.post("http://" + ip + "/api/v1/db/read", json=user_query)
            user_list.append(user.json()[0][0])
        read_result = read_result.json()[0]
        response = {}
        response["rideId"] = str(read_result[0])
        response["Created_by"] = str(read_result[1])
        response["users"] = user_list
        timestamp = datetime.strptime(read_result[2], "%a, %d %b %Y %H:%M:%S GMT")
        response["Timestamp"] = timestamp.strftime("%d-%m-%Y:%S-%M-%H")

        source_id = read_result[3]
        source_query = {"table": "places", "columns": ["place"], "where": ["placeid={}".format(source_id)]}
        source = requests.post("http://" + ip + "/api/v1/db/read", json=source_query)
        if source.status_code != 200:
            abort(400)
        response["source"] = source.json()[0][0]

        destination_id = read_result[3]
        destination_query = {"table": "places", "columns": ["place"], "where": ["placeid={}".format(destination_id)]}
        destination = requests.post("http://" + ip + "/api/v1/db/read", json=destination_query)
        if destination.status_code != 200:
            abort(400)
        response["destination"] = destination.json()[0][0]

        return jsonify(response)


#API 6
#Join an existing ride
@app.route("/api/v1/rides/<rideid>", methods = ['POST'])
def addUser(rideid):

    req_params = request.get_json()

    if req_params == None:
        abort(400)
    username = req_params["username"]

    userid_query = {"table": "user", "columns": ["id"], "where": ["username={}".format(username)]}
    userid = requests.post("http://" + ip + "/api/v1/db/read", json=userid_query)
    if len(userid.json()) == 0:
        abort(400)
    userid = userid.json()[0][0]

    add_user_query={"insert":[str(rideid), str(userid)],"table":"ride_user","columns":["rideid","userid"]}
    add_user_response=requests.post("http://" + ip + "/api/v1/db/write",json=add_user_query)
    if add_user_response.status_code != 200:
        abort(400)
    return ('', 204)

# API 7
# Delete a ride
@app.route("/api/v1/rides/<rideid>", methods = ['DELETE'])
def delete_ride(rideid):
    find_query = {"table": "rides", "columns": ["rideid"], "where": ["rideid={}".format(rideid)]}
    find_resp = requests.post("http://" + ip + "/api/v1/db/read", json=find_query)
    if len(find_resp.json()) == 0:
        abort(400)
    delete_query = {"where": ["rideid={}".format(rideid)], "table": "rides"}
    delete_resp = requests.delete("http://" + ip + "/api/v1/db/write", json=delete_query)
    return (jsonify(), 200)

# API 8
# Write to db
@app.route("/api/v1/db/write", methods = ['POST', 'DELETE'])
def write_db():
    req_params = request.get_json()
    try:
        if request.method == 'POST':
            columns = ",".join(req_params["columns"])
            table = req_params["table"].lower()
            values = req_params["insert"]
            for index in range(len(values)):
                if not values[index].isnumeric():
                    values[index] = "'{}'".format(values[index])
            values = ",".join(values)
            query = "INSERT INTO {} ({}) VALUES ({});".format(table, columns, values)
            print(query)
            query_result = db.engine.execute(text(query))

        elif request.method == 'DELETE':
            table = req_params["table"].lower()
            where = req_params["where"]
            for index in range(len(where)):
                split_cond = where[index].split("=")
                if not split_cond[1].isnumeric():
                    split_cond[1] = "'{}'".format(split_cond[1])
                where[index] = '='.join(split_cond)
            where = " and ".join(where)
            query = "DELETE FROM {} WHERE {};".format(table, where)
            query_result = db.engine.execute(text(query))
            print("Write Query: Table: {}, Columns: {}, Values: {}".format(table, columns, values))
            return ('Success', 200)
        return ('Success', 200)
    except IntegrityError as e:
        print(e)
        return ('Duplicate Error', 400)
    except Exception as e:
        print(e)
        return ('Query Error', 400)

# API 9
# Read from db
@app.route("/api/v1/db/read", methods = ['POST'])
def read_db():
    req_params = request.get_json()
    try:
        columns = ",".join(req_params["columns"])
        table = req_params["table"].lower()
        where = req_params["where"]
        if len(where) == 0:
            query = "SELECT {} FROM {};".format(columns, table)
        else:
            for index in range(len(where)):
                split_cond = where[index].split("=")
                if not split_cond[1].isnumeric() and split_cond[1] != "NOW()":
                    split_cond[1] = "'{}'".format(split_cond[1])
                where[index] = '='.join(split_cond)
            where = " and ".join(where)
            query = "SELECT {} FROM {} WHERE {};".format(columns, table, where)
        query_result = db.engine.execute(text(query))
        output = [list(i) for i in list(query_result)]
    except Exception as e:
        print("Error:", e)
        return ('Invalid Query', 400)
    print("Read Query: Table: {}, Columns: {}, Where: {}".format(table, columns, where))
    print("Query Result {}\n".format(output))
    return jsonify(output)

if __name__ == '__main__':
    app.run(host='" + ip + "')
