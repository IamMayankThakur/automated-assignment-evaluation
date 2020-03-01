from flask import Flask,request,make_response,jsonify
from datetime import datetime
from flask_pymongo import PyMongo
import json
import re

app=Flask(__name__)
app.config['MONGO_URI']='mongodb:/C:/Users/UDAY KIRAN M/Documents/db/mydb.db'
mongo=PyMongo(app)


if __name__ =='__main__':
	app.run(debug=True)


@app.route('/api/v1/users', methods=['PUT'])
def create_user():
	data = request.get_json()
	var_pass=data['password']
	var_user=data['username']
	query = {'collection': 'users','data':{ 'username': var_user}}
    record =requests.post(url='http://ec2-3-214-131-116.compute-1.amazonaws.com/api/v1/db/read', json = query)
    recdata=loads(record.text)

    if(len(recdata) > 0):
    	return jsonify({}),201
    
    else:

    	if re.match(re.compile(r'\b[0-9a-f]{40}\b'), var_pass) is None:
    		return jsonify({}),201
    	else:
    		query = {'collection': 'users','work': 'insert','data':{ 'username': var_user,'password':var_pass}}
        	createuser= requests.post(url='http://ec2-3-214-131-116.compute-1.amazonaws.com/api/v1/db/write',json=query)
        	return jsonify({}),200


@app.route('/api/v1/users/<string:user>', methods=['DELETE'])      
def delete_user(user):
    query = {'collection': 'users','data':{ 'username': user}}
    record = requests.post(url='http://ec2-3-214-131-116.compute-1.amazonaws.com/api/v1/db/read',json=query)
    recdata = loads(record.text)

    if(len(recdata) > 0):
        query = {'collection': 'rides','data':{ 'created_by': user}}
        record = requests.post(url='http://ec2-3-214-131-116.compute-1.amazonaws.com/api/v1/db/read',json=query)
        recdata = loads(record.text)

        if(len(recdata) > 0):
            query = {'collection': 'rides','work': 'delete', 'data':{ 'created_by': user}}
            rec = requests.post(url='http://ec2-3-214-131-116.compute-1.amazonaws.com/api/v1/db/write',json=query)

        query = {'collection': 'users','work': 'delete','data':{ 'username': user}}
        b = requests.post(url='http://ec2-3-214-131-116.compute-1.amazonaws.com/api/v1/db/write',json=query)
        return jsonify({}),200

    else:
        return jsonify({}),400


@app.route('/api/v1/rides', methods=['POST'])
def create_ride():
    req_data = request.get_json()   #getting the input request data
    name = req_data['created_by']

    query = {'collection': 'users','data':{ 'username': name}}
    record = requests.post(url='http://ec2-3-214-131-116.compute-1.amazonaws.com/api/v1/db/read',json=query)
    recdata = loads(record.text)

    rideId = 1
    max = 0

    if(len(recdata) > 0):
        timestamp = req_data['timestamp']
        tm = get_timestamp(timestamp)
        if(tm != "valid"):
            return jsonify({}), 400
        query = {'collection': 'rides','data':{}}
        rec = requests.post(url='http://ec2-3-214-131-116.compute-1.amazonaws.com/api/v1/db/read',json=query)
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

        query = {'collection': 'rides','work': 'insert', 'data': {'rideId': rideId,'created_by': name,'joinee': [],'timestamp' : timestamp,'source':source,'destination': dest}}     
        a = requests.post(url='http://ec2-3-214-131-116.compute-1.amazonaws.com/api/v1/db/write',json=query)
        return jsonify({}),201

    else:
        return jsonify({}),400


@app.route('/api/v1/rides?source={source}&destination={destination}',methods=['GET'])
def ridelist_details():
	source=request.args['source']
	destination=request.args['destination']




@app.route('/api/v1/rides/{rideid}', methods=['POST'])
def join_existing_ride():


@app.route('/api/v1/rides/{ride_id}',methods=['DELETE'])
def deleteride():



@app.route('/api/v1/db/write',methods=['POST'])
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



@app.route('/api/v1/db/read',methods=['POST'])
def read():
    req_data = request.get_json()
    data = req_data['data']
    collection = req_data['collection']
    senddata = db[collection].find(data)
    return dumps(senddata), 200