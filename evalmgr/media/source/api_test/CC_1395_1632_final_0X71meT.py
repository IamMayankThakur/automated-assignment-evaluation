from flask import Flask, jsonify, request,\
abort, Response,  redirect, url_for
from pymongo import MongoClient
from datetime import datetime
from bson import Binary, Code
from bson.json_util import dumps, loads
import json
import hashlib
import requests
import datetime
import re


app = Flask(__name__)
client = MongoClient("mongodb://127.0.0.1:27017")  # host uri
db = client.mymongodb  # Select the database

# const shortid = require('shortid')
# @app.route('/api/v1/users',methods = ['POST', 'DELETE'])
# def add_():
#      return jsonify({}), 405


@app.route('/api/v1/users',methods=['PUT'])
def add_user():
    req_data = request.get_json()
    
    name = req_data['username']
    passw = req_data['password']
    
    if(name == "" or passw == ""):
        return jsonify({}), 400

    hash_pass = hashlib.sha1(passw.encode())
    #print(hash_pass.hexdigest(),'-----------' ,hash_pass)
    
    query = {'collection': 'users','data':{ 'username': name}}
    rec = requests.post(url='http://52.45.188.30/api/v1/db/read',json=query)
    rdata = loads(rec.text) 
    #print(rdata)

    if(len(rdata) > 0):
        #return "Take diff username"
        return jsonify({}),400

    query = {'collection': 'users','work': 'insert', 'data': {'username': name, 'password': hash_pass.hexdigest()}}
    a = requests.post(url='http://52.45.188.30/api/v1/db/write',json=query)
    #print(a.status_code, a.reason,a.text)
    return jsonify({}),201



@app.route('/api/v1/users/<string:user>', methods=['DELETE'])
def delete_user(user):
    query = {'collection': 'users','data':{ 'username': user}}
    rec = requests.post(url='http://52.45.188.30/api/v1/db/read',json=query)
    rdata = loads(rec.text) 
    #print(rdata)

    if(len(rdata) > 0):
        query = {'collection': 'rides','data':{ 'created_by': user}}
        rec = requests.post(url='http://52.45.188.30/api/v1/db/read',json=query)
        rdata = loads(rec.text)
        
        if(len(rdata) > 0):
            query = {'collection': 'rides','work': 'delete', 'data':{ 'created_by': user}}
            rec = requests.post(url='http://52.45.188.30/api/v1/db/write',json=query)

        #data = db.users.find({"username": user})
        query = {'collection': 'users','work': 'delete','data':{ 'username': user}}
        a = requests.post(url='http://52.45.188.30/api/v1/db/write',json=query)
        return jsonify({}),200

    else:
        return jsonify({}),400



#@app.route('/api/time', methods=['POST'])
def get_timestamp(timestamp):
    #req_data = request.get_json()
    #timestamp = req_data["timestamp"]
    date,time = timestamp.split(':')
    dd,mm,yy = date.split('-')
    ss,min,hh = time.split('-')

    isValidDate = True

    try:
        datetime.datetime(int(yy),int(mm),int(dd))
    except ValueError:
        isValidDate = False
    if(isValidDate):
        if(int(ss) > 59 or int(min) > 59 or int(hh) > 23):
            return "not-valid"
        else:
            return "valid"
    else:
        return "not-valid"


@app.route('/api/v1/rides', methods=['POST'])
def create_ride():
    req_data = request.get_json()
    name = req_data['created_by']

    #data = db.users.find({'username': name})
    query = {'collection': 'users','data':{ 'username': name}}
    rec = requests.post(url='http://52.45.188.30/api/v1/db/read',json=query)
    rdata = loads(rec.text)

    rideId = 1
    max = 0

    if(len(rdata) > 0):
        timestamp = req_data['timestamp']
        # query = {'timestamp': timestamp}
        # rec = requests.post(url='http://52.45.188.30/api/time',json=query)
        tm = get_timestamp(timestamp)
        if(tm != "valid"):
            return jsonify({}), 400


        #rides = list(db.rides.find())
        query = {'collection': 'rides','data':{}}
        rec = requests.post(url='http://52.45.188.30/api/v1/db/read',json=query)
        rides = loads(rec.text)

        if(len(rides) <= 0):
            rideId = 1
        else:
            
            for i in range(0,len(rides)):
                
                if(rides[i]['rideId'] > max):
                    max = rides[i]['rideId']
                    rideId = max+1


        source = req_data['source']
        if(int(source) < 1 or int(source) > 198):
            return jsonify({}), 400

        dest = req_data['destination']
        if(int(dest) < 1 or int(dest) > 198):
            return jsonify({}), 400
        # db.rides.insert({
            # 'rideId': rideId,
            # 'created_by': name,
            # 'joinee': [],
            # 'timestamp' : timestamp,
            # 'source':source,
            # 'destination': dest
        # })
        query = {'collection': 'rides','work': 'insert', 'data': {'rideId': rideId,'created_by': name,'users': [],
            'timestamp' : timestamp,'source':source,'destination': dest}}
        a = requests.post(url='http://52.45.188.30/api/v1/db/write',json=query)
        return jsonify({}),201
    
    else:
        return jsonify({}),400
    


@app.route('/api/v1/db/write', methods=['POST'])
def write():
    req_data = request.get_json()
    collection = req_data['collection']
    data = req_data['data']

    if(req_data['work'] == 'insert'):    
        db[collection].insert(data)
        return jsonify({}), 201

    if(req_data['work'] == 'delete'):
        db[collection].remove(data)
        return jsonify({}), 201

    if(req_data['work'] == 'update'):
        data = req_data['data']
        #print("updatea here --- ",data[0],data[1])
        db[collection].update(data[0],data[1])
        return jsonify({}), 201    



@app.route('/api/v1/db/read', methods=['POST'])
def read():
    req_data = request.get_json()
    collection = req_data['collection']
    data = req_data['data']
    send_data = db[collection].find(data)
    return dumps(send_data), 200



@app.route('/api/v1/rides', methods=['GET'])
def upcoming_rides():

    if('source' in request.args):
        source = request.args['source']
    else:
        return jsonify({}), 400

    if('destination' in request.args):
        destination = request.args['destination']
    else:
        return jsonify({}), 400

    

    if(int(source) < 1 or int(source) > 198):
        return jsonify({}), 400

    if(int(destination) < 1 or int(destination) > 198):
        return jsonify({}), 400

    #data = list(db.rides.find({'source':source , 'destination':destination}))
    query = {'collection': 'rides','data':{'source':source , 'destination':destination}}
    rec = requests.post(url='http://52.45.188.30/api/v1/db/read',json=query)
    rdata = loads(rec.text) 
    #print(rdata)

    rides_list = []
    if(len(rdata) > 0):
        j=len(rdata)
        for i in range(0,j):
            rides_list.append(  {"rideId" : rdata[i]['rideId'],
            "username" : rdata[i]['created_by'] ,
            "timestamp" : rdata[i]['timestamp']
            })

        return json.dumps(rides_list),200
    else:
        return json.dumps(rides_list),204


@app.route('/api/v1/rides/<int:rideId>', methods=['GET'])
def ride_detail(rideId):
    #data = db.rides.find({'rideId': rideId})
    query = {'collection': 'rides','data':{'rideId': rideId}}
    rec = requests.post(url='http://52.45.188.30/api/v1/db/read',json=query)
    rdata = loads(rec.text)
    
    if(len(rdata) > 0):
        #print('==========',rdata[0])
        dic = dict()
        dic = rdata[0]
        dic.pop("_id")
        return json.dumps(dic),200
    else:
        return 204



@app.route('/api/v1/rides/<int:rideId>', methods=['POST'])   
def join_ride(rideId):
    req_data = request.get_json()
    name = req_data['username']
    #dbname = db.users.find({'username': name})
    query = {'collection': 'users','data':{ 'username': name}}
    rec = requests.post(url='http://52.45.188.30/api/v1/db/read',json=query)
    rdata = loads(rec.text) 
    #print(rdata)

    if(len(rdata) > 0):
        #dbid = db.rides.find({'rideId': rideId})
        query = {'collection': 'rides','data':{ 'rideId': rideId}}
        rec = requests.post(url='http://52.45.188.30/api/v1/db/read',json=query)
        rdata = loads(rec.text) 
        #print(rdata, rdata[0]['rideId'])

        if(len(rdata) > 0):
        #if(dbid.count() > 0):
            #db.rides.update({'rideId': rideId}, {'$push': {'joinee': name}} )
            query = {'collection': 'rides','work': 'update', 'data': ({'rideId': rideId},{'$push': {'users': name}} )}
            a = requests.post(url='http://52.45.188.30/api/v1/db/write',json=query)
            #return a.text

            return jsonify({}), 201
        else:
            return jsonify({}), 400
    else:
        return jsonify({}), 400



@app.route('/api/v1/rides/<int:rideId>', methods=['DELETE'])   
def delete_ride(rideId):
    query = {'collection': 'rides','data':{ 'rideId': rideId}}
    rec = requests.post(url='http://52.45.188.30/api/v1/db/read',json=query)
    rdata = loads(rec.text) 

    if(len(rdata) > 0):
        query = {'collection': 'rides','work': 'delete', 'data':{ 'rideId': rideId}}
        rec = requests.post(url='http://52.45.188.30/api/v1/db/write',json=query)
        return jsonify({}), 200
    else:
        return jsonify({}), 400

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"MyError" : "method not allowed"}),405

@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"MyError" : "Page not found"}),404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"MyError" : "Server Error"}),500

if __name__ == '__main__':
    app.run(host='0.0.0.0')
   