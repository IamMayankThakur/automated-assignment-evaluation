"""
RideShare Application
---------------------
Team Details:
    Abhishek Patil
    Adeesh
    Manthan B Y
    Naveen Karthik

"""
from flask import Flask, request, Response, jsonify, make_response, Response
import requests
from pymongo import MongoClient
import datetime
from bson.json_util import dumps
import json
val_hex = list(range(ord('A'), ord('F') + 1)) + list(range(ord('a'),
                                                           ord('f') + 1)) + list(range(ord('0'), ord('9') + 1))

import pandas as pd
df = pd.read_csv('AreaNameEnum.csv')
cities = df['Area No']
cities = [i for i in cities]
"""
Status Codes:
200 OK
201 Created
204 No Content
400 Bad Request
405 Method Not Allowed
"""

# function to whether the password is valid or not


def validPass(passwd):
    if (len(passwd) != 40):
        return False
    for i in passwd:
        if(ord(i) not in val_hex):
            return False
    return True


app = Flask(__name__)

#client = MongoClient('mongodb://localhost:27017/')
#client = MongoClient('mongodb://admin:manthu1234@52.91.176.118:27017')
client = MongoClient('mongodb://admin:manthu1234@localhost:27017')

url_path = 'http://localhost:5000'
rideDB = client['RideShare']    # db creation
users = rideDB['users']  # collection creation
rides = rideDB['rides']

# we need a unique number for each ride
# so we use this record in rides collection to have a count :)
if(rides.find_one({"title": "rideNo"}) == None):
    rides.insert({
        'title': 'rideNo',
        'currNo': 1
    })


def getRideId():
    """
    This function computes the returns the unique rideId, and increments it in the database,
    for next ride :)
    """
    num = rides.find_one({'title': 'rideNo'})['currNo']
    rides.update_one({'title': 'rideNo'}, {
        '$inc': {'currNo': 1}
    })
    return num

# Write to the database operation, this function will be called internally :)
@app.route("/api/v1/db/write", methods=["POST"])
def write_into_db():
    """
    This API contains all the operations related to the write to the database
    """
    if request.json['type'] == 'add_user':
        username = request.json['username']
        if(rideDB[request.json['table']].find_one({'username': username}) == None):
            rideDB[request.json['table']].insert_one({
                'username': username,
                'password': request.json['password']
            })
            return make_response('', 201)
        else:
            # if the user already exists with the given username then send 400(Bad Request)
            return make_response('', 400)
    if request.json['type'] == 'remove_user':
        username = request.json['username']
        if(rideDB[request.json['table']].find_one({'username': username}) == None):
            # user doesn't exist return 204(No Content) TODO remove_user
            return make_response('', 204)
        rideDB[request.json['table']].delete_one({'username': username})
        return make_response('', 200)
    if request.json['type'] == 'new_ride':
        json_dict = request.json
        if(json_dict['source'] == json_dict['destination']):
            return {}, 400
        if(json_dict['source'] not in cities or json_dict['destination'] not in cities):
            return {}, 400
        table = json_dict['table']
        print(json_dict['created_by'])
        if(rideDB['users'].find_one({'username': json_dict['created_by']}) == None):
            return make_response('', 204)   # username not found TODO username
        try:
            json_dict['timestamp'] = datetime.datetime.strptime(
                json_dict['timestamp'], '%d-%m-%Y:%S-%M-%H')
        except:
            # if the timestamp provided is not correct then return 400(Bad Request)
            return {}, 400
        if(json_dict['timestamp'] < datetime.datetime.now()):
            return {}, 400
        json_dict.pop('type')
        json_dict.pop('table')  # we dont need type and table field anymore
        rideDB[table].insert_one(json_dict)
        return make_response('', 201)
    if request.json['type'] == 'add_user_to_ride':
        # try to get an existing ride
        existing = rides.find_one({
            'rideId': int(request.json['rideId'])
        })
        if(existing == None):
            return {}, 204  # no ride with rideId return 204(No Content)
        user = users.find_one({
            'username': request.json['username']
        })
        if(user == None):
            # if the user doesn't exist return 204(No Content) CHECK ONCE: TODO
            return {}, 204
        rides.update_one(
            {
                'rideId': int(request.json['rideId'])
            },
            {
                '$push': {
                    'users': request.json['username']
                }
            }
        )   # push the new user to the existing ride
        return {}, 200
    if request.json['type'] == 'delete_ride':
        ride = rides.find_one({'rideId': int(request.json['rideId'])})
        if(ride == None):
            return {}, 204  # if the ride doesn't exist return 204(No Content)
        rides.delete_one({'rideId': int(request.json['rideId'])})
        return {}, 200
# Here Completes the implementation of write operations


@app.route("/api/v1/db/read", methods=["POST"])
def read_from_db():
    if request.json['type'] == 'list_rides':
        arr = rides.aggregate([
            {
                '$match': {
                    'source': request.json['source'],
                    'destination': request.json['destination']
                }
            },
            {
                '$project': {
                    '_id': False,
                    'rideId': '$rideId',
                    'username': '$created_by',
                    'timestamp': {"$dateToString": {"format": "%d-%m-%Y:%S-%M-%H", "date": "$timestamp"}}
                }
            }
        ])
        arr = dumps(arr)
        print(len(arr))
        if(len(arr) > 2):
            return make_response(arr, 200)
        return make_response('', 204)
    if request.json['type'] == 'ride_detail':
        ride = rides.find_one({
            'rideId': int(request.json['rideId'])
        }, {
            '_id': 0,
            'rideId': 1,
            'created_by': 1,
            'users': 1,
            'timestamp': 1,
            'source': 1,
            'destination': 1
        })
        print(ride)
        if(ride != None):
            return make_response(ride, 200)
        return {}, 204


@app.route('/api/v1/users', methods=["PUT"])
def add_user():
    user_data = request.get_json()
    # check for validity of the password
    password = user_data['password']
    if(not validPass(password)):
        return {}, 400
    write_request_data = {'username': user_data['username'],
                          'password': password,
                          'table': 'users',
                          'type': 'add_user'}
    db_resp = requests.post(
        url=url_path + '/api/v1/db/write', json=write_request_data)
    return {}, db_resp.status_code


@app.route('/api/v1/users/<username>', methods=["DELETE"])
def remove_user(username):
    write_request_data = {'username': username,
                          'table': 'users',
                          'type': 'remove_user'}
    db_resp = requests.post(
        url=url_path + '/api/v1/db/write', json=write_request_data)
    return {}, db_resp.status_code


@app.route('/api/v1/rides', methods=["GET", "POST"])
def ride_details():
    # if GET request
    if(request.method == "GET"):
        source = request.args.get('source')
        destination = request.args.get('destination')
        write_request_data = {'source': source,
                              'destination': destination,
                              'table': 'rides',
                              'type': 'list_rides'}
        db_resp = requests.post(
            url=url_path + '/api/v1/db/read', json=write_request_data)
        if(db_resp.status_code == 204):
            return {}, 204
        return db_resp.text, db_resp.status_code, {'Content-Type': 'application/json; charset=utf-8'}
    if request.method == "POST":
        data = request.get_json()
        username = data['created_by']
        source = data['source']
        destination = data['destination']
        write_request_data = {
            'rideId': getRideId(),
            'created_by': username,
            'users': [username],
            'timestamp': data['timestamp'],
            'source': source,
            'destination': destination,
            'type': 'new_ride',
            'table': 'rides'
        }
        db_resp = requests.post(
            url=url_path + '/api/v1/db/write', json=write_request_data)
        return {}, db_resp.status_code


@app.route('/api/v1/rides/<rideId>', methods=["GET", "POST", "DELETE"])
def get_ride_details(rideId):
    if request.method == 'GET':
        write_request_data = {'rideId': int(rideId),
                              'type': 'ride_detail'}
        db_resp = requests.post(
            url=url_path + '/api/v1/db/read', json=write_request_data)
        return db_resp.text, db_resp.status_code, {'Content-Type': 'application/json; charset=utf-8'}
    if request.method == 'POST':
        ride = request.get_json()
        write_request_data = {'rideId': int(rideId),
                              'type': 'add_user_to_ride',
                              'username': ride['username']}
        db_resp = requests.post(
            url=url_path + '/api/v1/db/write', json=write_request_data)
        return db_resp.text, db_resp.status_code, {'Content-Type': 'application/json; charset=utf-8'}
    if request.method == 'DELETE':
        write_request_data = {'rideId': int(rideId),
                              'type': 'delete_ride'}
        db_resp = requests.post(
            url=url_path + '/api/v1/db/write', json=write_request_data)
        return {}, db_resp.status_code


if(__name__ == '__main__'):
    app.debug = True
    app.run()
