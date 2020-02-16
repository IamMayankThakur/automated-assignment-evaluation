#!/usr/bin/python
# -*- coding: utf-8 -*-
import flask
import pymongo
import requests
import ast
import re
import csv
import datetime

app = flask.Flask(__name__)

new_ride_id = 1

locations = list()
with open('AreaNameEnum.csv') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    next(reader)
    for row in reader:
        locations.append(int(row[0]))


ip = requests.get('https://checkip.amazonaws.com').text[:-1]
database = pymongo.MongoClient('mongodb://localhost:27017/')['accounts']
api_8_write_url = 'http://' + ip + '/api/v1/db/write'
api_9_read_url = 'http://' + ip + '/api/v1/db/read'


# API 1

@app.route('/api/v1/users', methods=['PUT'])
def addUser():
    try:
        username = flask.request.get_json()['username']
        password = flask.request.get_json()['password'].lower()
    except:
        return flask.Response('Invalid request format!', status=400)
    d = dict()
    d['table'] = 'users'
    d['column'] = ['username']
    d['data'] = [username]
    if len(ast.literal_eval(requests.post(url=api_9_read_url, json=d).text)) == 0:
        if re.search('^[a-fA-F0-9]{40}$', password):
            d['table'] = 'users'
            d['column'] = ['username', 'password']
            d['data'] = [username, password]
            d['flag'] = 'w'
            requests.post(url=api_8_write_url, json=d)
            print('User created')
            return flask.Response('{}', status=201)
        else:
            return flask.Response('Invalid Password: not in SHA-1 format', status=400)
    return flask.Response('Username already exists!', status=400)


# API 2

@app.route('/api/v1/users/<name>', methods=['DELETE'])
def removeUser(name):
    d = dict()
    d['table'] = 'users'
    d['column'] = ['username']
    d['data'] = [name]
    if len(ast.literal_eval(requests.post(url=api_9_read_url, json=d).text)) == 0:
        return flask.Response('User doesn\'t exist!', status=400)
    d = dict()
    d['table'] = 'rides'
    d['column'] = ['created_by']
    d['data'] = [name]
    if ast.literal_eval(requests.post(url=api_9_read_url, json=d).text):
        return flask.Response('User has booked an upcoming ride!', status=400)
    d['table'] = 'users'
    d['column'] = ['username']
    d['data'] = [name]
    d['flag'] = 'd'
    requests.post(url=api_8_write_url, json=d)
    d = dict()
    d['table'] = 'users_rides'
    d['column'] = ['username']
    d['data'] = [name]
    if ast.literal_eval(requests.post(url=api_9_read_url, json=d).text):
        print ('User has joined another ride - Removing them from the ride...')
    d['flag'] = 'd'
    requests.post(url=api_8_write_url, json=d)
    return flask.Response('{}', status=200)


# API 3

@app.route('/api/v1/rides', methods=['POST'])
def createRide():
    try:
        timestamp = flask.request.get_json()['timestamp']
        created_by = flask.request.get_json()['created_by']
        source = int(flask.request.get_json()['source'])
        destination = int(flask.request.get_json()['destination'])
    except:
        return flask.Response('Invalid request format!', status=400)
    try:
        time = datetime.datetime.strptime(timestamp,
                '%d-%m-%Y:%S-%M-%H')
    except:
        return flask.Response('Invalid timestamp!', status=400)
    if source not in locations or destination not in locations or source == destination:
        return flask.Response('Invalid source or destination!', status=400)
    d = dict()
    d['table'] = 'users'
    d['column'] = ['username']
    d['data'] = [created_by]
    if len(ast.literal_eval(requests.post(url=api_9_read_url, json=d).text)) == 0:
        return flask.Response('User doesn\'t exist!', status=400)
    d['table'] = 'rides'
    while True:
        d['column'] = ['ride_id']
        global new_ride_id
        d['data'] = [new_ride_id]
        if len(ast.literal_eval(requests.post(url=api_9_read_url, json=d).text)) == 0:
            break
        new_ride_id += 1
    d['column'] = ['ride_id', 'timestamp', 'created_by',
                          'source', 'destination']
    d['data'] = [new_ride_id, timestamp, created_by, source,
                        destination]
    d['flag'] = 'w'
    requests.post(url=api_8_write_url, json=d)
    d['table'] = 'users_rides'
    d['column'] = ['username', 'ride_id']
    d['data'] = [created_by, new_ride_id]
    d = requests.post(url=api_8_write_url, json=d)
    return flask.Response('{}', status=201)


# API 4

@app.route('/api/v1/rides', methods=['GET'])
def upcomingRides():
    try:
        source = int(flask.request.args.get('source', None))
        destination = int(flask.request.args.get('destination', None))
    except:
        return flask.Response('Invalid request format!', status=400)
    if source not in locations or destination not in locations or source == destination:
        return flask.Response('Invalid source or destination!', status=400)
    d = dict()
    d['column'] = ['source', 'destination']
    d['data'] = [source, destination]
    d['table'] = 'rides'
    l = requests.post(url=api_9_read_url, json=d)
    if len(ast.literal_eval(l.text)) == 0:
        print('No upcoming rides')
        return flask.Response(status=204)
    l = ast.literal_eval(l.text)
    filtered_list = list()
    for row in l:
        time = datetime.datetime.strptime(row['timestamp'],
                '%d-%m-%Y:%S-%M-%H')
        current = datetime.datetime.now()
        if time >= current:
            filtered_list.append({'rideId': row['ride_id'],
                                 'username': row['created_by'],
                                 'timestamp': row['timestamp']})
    if len(filtered_list) == 0:
        return flask.Response(status=204)
    return flask.Response(str(filtered_list), status=200)


# API 5

@app.route('/api/v1/rides/<rideId>', methods=['GET'])
def getRideDetails(rideId):
    d = dict()
    d['column'] = ['ride_id']
    d['data'] = [int(rideId)]
    d['table'] = 'rides'
    details = ast.literal_eval(requests.post(url=api_9_read_url, json=d).text)
    if len(details) == 0:
        print('Ride doesn\'t exist')
        return flask.Response(status=204)
    d['column'] = ['ride_id']
    d['data'] = [int(rideId)]
    d['table'] = 'users_rides'
    users = [_['username'] for _ in ast.literal_eval(requests.post(url=api_9_read_url, json=d).text)]
    users.remove(details[0]['created_by'])
    response = str({
        'rideId': int(rideId),
        'created_by': details[0]['created_by'],
        'users': users,
        'timestamp': details[0]['timestamp'],
        'source': details[0]['source'],
        'destination': details[0]['destination'],
        })
    return flask.Response(response, status=200)


# API 6

@app.route('/api/v1/rides/<rideId>', methods=['POST'])
def joinRide(rideId):
    d = dict()
    d['column'] = ['ride_id']
    d['data'] = [int(rideId)]
    d['table'] = 'rides'
    ride_details = ast.literal_eval(requests.post(url=api_9_read_url, json=d).text)
    if len(ride_details) == 0:
        return flask.Response('Ride doesn\'t exist', status=400)
    timestamp = ride_details[0]['timestamp']
    time = datetime.datetime.strptime(timestamp,
                '%d-%m-%Y:%S-%M-%H')
    current = datetime.datetime.now()
    if time < current:
        return flask.Response('The ride has already started!', status=400)
    try:
        username = flask.request.get_json()['username']
    except:
        return flask.Response('Invalid request format!', status=400)
    d['column'] = ['username']
    d['data'] = [username]
    d['table'] = 'users'
    if len(ast.literal_eval(requests.post(url=api_9_read_url, json=d).text)) == 0:
        return flask.Response('User doesn\'t exist', status=400)
    if ride_details[0]['created_by'] == username:
        return flask.Response('User cannot join their own ride!', status=400)
    d['column'] = ['username', 'ride_id']
    d['data'] = [username, int(rideId)]
    d['table'] = 'users_rides'
    if ast.literal_eval(requests.post(url=api_9_read_url, json=d).text):
        return flask.Response('User has already joined the ride!', status=400)
    d['flag'] = 'w'
    requests.post(url=api_8_write_url, json=d)
    return flask.Response('{}', status=200)


# API 7

@app.route('/api/v1/rides/<rideId>', methods=['DELETE'])
def deleteRide(rideId):
    d = dict()
    d['table'] = 'rides'
    d['column'] = ['ride_id']
    d['data'] = [int(rideId)]
    if len(ast.literal_eval(requests.post(url=api_9_read_url, json=d).text)) == 0:
        return flask.Response('Ride doesn\'t exist!', status=400)
    d['flag'] = 'd'
    requests.post(url=api_8_write_url, json=d)
    d['table'] = 'users_rides'
    requests.post(url=api_8_write_url, json=d)
    return flask.Response('{}', status=200)


# API 8

@app.route('/api/v1/db/write', methods=['POST'])
def writeToDatabase():
    d = dict()
    flag = flask.request.get_json()['flag']
    column = flask.request.get_json()['column']
    table = flask.request.get_json()['table']
    data = flask.request.get_json()['data']
    mycol = database[table]
    mydict = dict()
    for i in range(len(data)):
        mydict[column[i]] = data[i]
    if flag == 'w':
        x = mycol.insert_one(mydict)
        print ('Inserted, id:', x.inserted_id)
    elif flag == 'd':
        x = mycol.remove(mydict)
        print ('Deleted')
    else:
        return flask.Response('Invalid flag!', status=400)
    return flask.jsonify({})


# API 9

@app.route('/api/v1/db/read', methods=['POST'])
def readFromDatabase():
    d = dict()
    table = flask.request.get_json()['table']
    column = flask.request.get_json()['column']
    data = flask.request.get_json()['data']
    mycol = database[table]
    mydict = dict()
    for i in range(len(data)):
        mydict[column[i]] = data[i]
    l = [_ for _ in mycol.find(mydict, {'_id': False})]
    if l:
        return flask.jsonify(l)
    return flask.jsonify({})
