import constants
import flask
import json
import mysql.connector
import requests

from app_helper import *
from flask import Flask
from flask import jsonify
from flask import Response
from flask import request
from flask import url_for

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(
    TEST = False,
    DATABASE = "RideShare",
    HOST = "localhost",
    PASSWD = "admin@123",
    USER = "admin"))

@app.route('/')
@app.route('/Index')
def index_page():
    """Default page."""
    return 'Ride Sharing App. Assignment 1.'

@app.route(constants.API1_URL, methods = ["PUT"])
def add_user():
    """API 1

    Adding an user"""

    # Extracting parameters.
    request_json = request.get_json()
    if "username" not in request_json.keys() or "password" not in request_json.keys():
        return Response("{}", status = 400, mimetype = 'application/json')

    username =  request_json["username"]
    password =  request_json["password"]

    if not is_SHA1(password):
        return Response("{}", status = 400, mimetype = 'application/json')

    # Use API 9 to ensure username is unique. 
    api9_url = constants.API_URL + constants.API9_URL
    request_data = {}
    request_data["columns"] = ["username"]
    request_data["table"] = "USERS"
    request_data["wheres"] = ["{} = \"{}\"".format("username", username)]

    api9_response = requests.post(url = api9_url, json = request_data)
    if api9_response.status_code == 200:
        if len(api9_response.json()['query_result']):
            return Response(
                "{}", 
                status = 400, 
                mimetype = 'application/json')
    else:
        return Response(str(api9_response.json()), status = 500, mimetype = 'application/json')

    # Use API 8 to insert username and password. 
    api8_url = constants.API_URL + constants.API8_URL
    request_data = {}
    request_data["columns"] = ["username", "password"]
    request_data["operation"] = "INSERT"
    request_data["table"] = "USERS"
    request_data["values"] = [username, password]
    
    api8_response = requests.post(url = api8_url, json = request_data)
    if(api8_response.status_code == 200):
        return Response("Entry added.", status = 201, mimetype = 'application/json')
    else:
        return Response("{}", status = 500, mimetype = 'application/json')

@app.route(constants.API2_URL + "/<username>", methods = ["DELETE"])
def remove_user(username):
    """API 2

    Removing an user."""

    if username == None:
        return Response("{}", status = 400, mimetype = 'application/json')

    # Using API 9 to ensure username exists in database
    api9_url = constants.API_URL + constants.API9_URL
    request_data = {}
    request_data["columns"] = ["username"]
    request_data["table"] = "USERS"
    request_data["wheres"] = ["{} = '{}'".format("username", username)]
    api9_response = requests.post(url = api9_url, json =  request_data)

    if api9_response.status_code == 200:
        if len(api9_response.json()['query_result']) == 0:
            return Response(
                "{}", 
                status = 400, 
                mimetype = 'application/json')
    else:
        return Response(
            "{}", 
            status = 500, 
            mimetype = 'application/json')

    # Use API 8 to delete entry.
    api8_url = constants.API_URL + constants.API8_URL
    request_data = {}
    request_data["columns"] = ["username"]
    request_data["operation"] = "DELETE"
    request_data["table"] = "USERS"
    request_data["values"] = [username]
    
    api8_response = requests.post(url = api8_url, json =  request_data)
    if(api8_response.status_code == 200):
        return Response(".", status = 200, mimetype = 'application/json')
    else:
        return Response("{}", status = 500, mimetype = 'application/json')

@app.route(constants.API3_URL, methods = ["POST"])
def new_ride():
    """API 3

    Adding a ride"""
    
    # Extracting parameters.
    request_json = request.get_json()

    if "created_by" not in request_json.keys() or \
        "destination" not in request_json.keys() or \
        "source" not in request_json.keys() or \
        "timestamp" not in request_json.keys():
        return Response("{}", status = 400, mimetype = 'application/json')

    creator_username = request_json["created_by"]
    destination = int(request_json["destination"])
    source = int(request_json["source"])
    timestamp = request_json["timestamp"]

    # Using API 9 to ensure username exists in database
    api9_url = constants.API_URL + constants.API9_URL
    request_data = {}
    request_data["columns"] = ["username"]
    request_data["table"] = "USERS"
    request_data["wheres"] = ["{} = \"{}\"".format("username", creator_username)]

    api9_response = requests.post(url = api9_url, json =  request_data)
    if api9_response.status_code == 200:
        if len(api9_response.json()['query_result']) == 0:
            return Response(
                "Username not in database.", 
                status = 400, 
                mimetype = 'application/json')
    else:
        return Response(
            "Internal Server Error", 
            status = 500, 
            mimetype = 'application/json')

    # Checking if source and destinationination is valid.
    if source not in constants.area_dict.keys() or \
        destination not in constants.area_dict.keys() or \
            source == destination:
        return Response(
                "Source or destinationination invalid.", 
                status = 400, 
                mimetype = 'application/json')

    # Checking if timestamp is valid.
    if not is_ridetime_valid(timestamp):
        return Response(
                "Timestamp invalid.", 
                status = 400, 
                mimetype = 'application/json')

    # Use API 8 to insert ride to ride table.
    api8_url = constants.API_URL + constants.API8_URL
    request_data = {}       
    request_data["columns"] = [
        "created_by", 
        "destination",
        "source",
        "timestamp"]
    request_data["operation"] = "INSERT"
    request_data["table"] = "RIDES"
    request_data["values"] = [
        creator_username,
        destination,
        source,
        timestamp]
    
    api8_response = requests.post(url = api8_url, json = request_data)
    if(api8_response.status_code == 200):
        return Response("Entry added.", status = 201, mimetype = 'application/json')
    else:
        return Response("", status = 500, mimetype = 'application/json')


@app.route(constants.API4_URL, methods = ["GET"])
def list_rides():
    """API 4

    List all upcoming rides for a given source and destination."""

    # Extracting parameters.
    request_json = dict(request.args)
    
    if "destination" not in request_json.keys() or \
        "source" not in request_json.keys() : 
        return Response("{}", status = 400, mimetype = 'application/json')

    destination = int(request_json["destination"])
    source = int(request_json["source"])

    api9_url = constants.API_URL + constants.API9_URL
    request_data = {}
    request_data["columns"] = ["rideId", "created_by", "timestamp"]
    request_data["table"] = "RIDES"
    request_data["wheres"] = [
        "{} = {}".format("source", source),
        "{} = {}".format("destination", destination)]

    
    api9_response = requests.post(url = api9_url, json =  request_data)
    if api9_response.status_code == 200:
        query_result = api9_response.json()['query_result']
        future_rides = []
        for row in query_result:
            if is_ridetime_in_future(row[2]):
                future_rides.append(dict(
                    rideId = str(row[0]),
                    username = row[1],
                    timestamp = row[2]))
        print(future_rides)
        if len(future_rides) != 0:
            return Response(
                json.dumps(future_rides),
                status = 200, 
                mimetype = 'application/json')     
        else:
            return Response(
                "No Content",
                status = 204, 
                mimetype = 'application/json')
    else:
        return Response(
            "Internal Server Error", 
            status = 500, 
            mimetype = 'application/json')


@app.route(constants.API4_URL + "/<rideId>", methods = ["GET"])
def list_ride_details(rideId):
    """API 5

    List all the details of a given ride."""

    if rideId == None:
        return Response("{}", status = 400, mimetype = 'application/json')
    
    api9_url = constants.API_URL + constants.API9_URL

    # Using API 9 to get ride details from the RIDE table.
    request_data = {}
    request_data["columns"] = [
        "rideId", 
        "created_by", 
        "timestamp", 
        "source", 
        "destination"]
    request_data["table"] = "RIDES"
    request_data["wheres"] = ["{} = {}".format("rideId", rideId)]

    api9_response_rides = requests.post(url = api9_url, json =  request_data)
    
    if api9_response_rides.status_code != 200:
        return Response(
            "Internal Server Error", 
            status = 500, 
            mimetype = 'application/json')

    api9_result = api9_response_rides.json()['query_result']
    if len(api9_result) == 0:
        return Response(
            "No such ride",
            status = 400, 
            mimetype = 'application/json')        
    api9_result = api9_result[0]
    ride_details = {}
    ride_details['rideId'] = str(api9_result[0])
    ride_details['created_by'] = api9_result[1]
    ride_details['timestamp'] = api9_result[2]
    ride_details['source'] = str(api9_result[3])
    ride_details['destination'] = str(api9_result[4])
    
    # Using API 9 to fetch username of all the users associated 
    # with the ride from the RIDERS table.
    request_data = {}
    request_data["columns"] = ["username"]
    request_data["table"] = "RIDERS"
    request_data["wheres"] = ["{} = {}".format("rideId", rideId)]

    api9_response_riders = requests.post(url = api9_url, json =  request_data)
    if api9_response_riders.status_code != 200:
        return Response(
        "Internal Server Error", 
        status = 500, 
        mimetype = 'application/json')
    riders = api9_response_riders.json()['query_result']
    ride_details['users'] = [rider[0] for rider in riders]

    return Response(
        json.dumps(ride_details),
        status = 200, 
        mimetype = 'application/json')

@app.route(constants.API6_URL + "/<rideId>", methods = ["POST"])
def join_existing_ride(rideId):
    """API 6.

    Join an existing ride."""

    request_json = request.get_json()        
    if "username" not in request_json.keys() or rideId == None:
        return Response("{}", status = 400, mimetype = 'application/json')

    username =  request_json["username"]
    
    # Use API 9 to ensure username exists. 
    api9_url = constants.API_URL + constants.API9_URL
    request_data = {}
    request_data["columns"] = ["username"]
    request_data["table"] = "USERS"
    request_data["wheres"] = ["{} = '{}'".format("username", username)]
    
    api9_response = requests.post(url = api9_url, json = request_data)
    if api9_response.status_code == 200:
        if len(api9_response.json()['query_result']) == 0:
            return Response(
                "Username does not exist", 
                status = 400, 
                mimetype = 'application/json')
    
    # Use API 9 to ensure the ride exists
    request_data = {}
    request_data["columns"] = ["rideId", "created_by", "timestamp"]
    request_data["table"] = "RIDES"
    request_data["wheres"] = ["{} = {}".format("rideId", rideId)]
    
    api9_response = requests.post(url = api9_url, json =  request_data)
    if api9_response.status_code == 200:
        if len(api9_response.json()['query_result']) == 0:
            return Response(
                "Ride does not exist", 
                status = 400, 
                mimetype = 'application/json')

        if api9_response.json()['query_result'][0][1] == username:
            return Response(
                    "{}", 
                    status = 400, 
                    mimetype = 'application/json')

    # Use API 8 to insert user to ride.
    api8_url = constants.API_URL + constants.API8_URL
    request_data = {}
    request_data["columns"] = ["username", "rideId"]
    request_data["operation"] = "INSERT"
    request_data["table"] = "RIDERS"
    request_data["values"] = [username, rideId]
    
    api8_response = requests.post(url = api8_url, json =  request_data)
    if(api8_response.status_code == 200):
        return Response("Entry added.", status = 200, mimetype = 'application/json')
    else:
        return Response("", status = 500, mimetype = 'application/json')

@app.route(constants.API7_URL + "/<rideId>", methods = ["DELETE"])
def remove_ride(rideId):
    """API 7

    Deleting a ride."""

    if rideId == None:
        return Response("{}", status = 400, mimetype = 'application/json')
    
    request_data = {}
    request_data["columns"] = ["rideId"]
    request_data["table"] = "RIDES"
    request_data["wheres"] = ["{} = {}".format("rideId", rideId)]
    
    api9_url = constants.API_URL + constants.API9_URL

    api9_response = requests.post(url = api9_url, json =  request_data)
    if api9_response.status_code == 200:
        if len(api9_response.json()['query_result']) == 0:
            return Response(
                "Ride does not exist", 
                status = 400, 
                mimetype = 'application/json')
    
    # Use API 8 to delete entry.
    api8_url = constants.API_URL + constants.API8_URL
    request_data = {}
    request_data["columns"] = ["rideId"]
    request_data["operation"] = "DELETE"
    request_data["table"] = "RIDES"
    request_data["values"] = [rideId]
    
    api8_response = requests.post(url = api8_url, json =  request_data)
    if(api8_response.status_code == 200):
        return Response("Entry Deleted.", status = 200, mimetype = 'application/json')
    else:
        return Response("", status = 500, mimetype = 'application/json')

@app.route(constants.API8_URL, methods = ["POST"])
def write_to_db():
    """API 8.

    Writing to database.
    Operation is either INSERT or DELETE or UPDATE."""

    try:	
        rideshare_db = mysql.connector.connect(
                        database = app.config['DATABASE'],
                        host = app.config['HOST'],
                        passwd = app.config['PASSWD'],
                        user = app.config['USER'])
        cursor = rideshare_db.cursor()	

    except:
        return Response("No connection", status = 500, mimetype = 'application/json')

    # Extracting parameters.
    request_json = request.get_json()
    if "columns" not in request_json.keys() or \
        "values" not in request_json.keys() or \
        "operation" not in request_json.keys() or \
        "table" not in request_json.keys() :
        return Response("{}".format(request), status = 400, mimetype = 'application/json')

    columns = request.get_json()["columns"]
    data = request.get_json()["values"]
    operation = request.get_json()["operation"].upper()
    table = request.get_json()["table"].upper()

    try:
        if operation == "INSERT":
            values = ','.join([
                "'{}'".format(value) if type(value) == str \
                    else str(value) for value in data])
            query = "INSERT INTO {} ({}) VALUES ({});".format(
                table, ', '.join(columns), values);
            cursor.execute(query)
            rideshare_db.commit()
            return Response("{}", status = 200, mimetype = 'application/json')

        elif operation == "DELETE":
            argument_list = [
                "{} = '{}'".format(str(column_name), str(column_value)) \
                    if type(column_value) == str \
                    else "{} = {}".format(str(column_name), str(column_value)) \
                    for column_name, column_value in zip(columns, data)]
           
            query_argument = ' and '.join(argument_list)
            query = "DELETE FROM {} WHERE BINARY {};".format(table, query_argument)
            cursor.execute(query)
            rideshare_db.commit()
            return Response("{}", status = 200, mimetype = 'application/json')

        else:
            return Response("{}", status = 400, mimetype = 'application/json')

    except Exception as e:
            return Response("{}".format(e), status = 400, mimetype = 'application/json')


@app.route(constants.API9_URL, methods = ["POST"])
def read_from_db():
    """API 9.

    Reading from database."""
    
    try:	
        rideshare_db = mysql.connector.connect(
                        database = app.config['DATABASE'],
                        host = app.config['HOST'],
                        passwd = app.config['PASSWD'],
                        user = app.config['USER'])
        cursor = rideshare_db.cursor()	

    except Exception as e:
        return Response("No connecto", status = 500, mimetype = 'application/json')

    # Extracting parameters.
    request_json = request.get_json()

    # Send "bad request" response if column names or table name missing from request.
    if "columns" not in request_json.keys() or "table" not in request_json.keys():
        return Response("{}", status = 400, mimetype = 'application/json')

    columns = request_json["columns"]
    table = request_json["table"].upper()
    wheres = None
    if "wheres" in request_json.keys():
        wheres = request_json["wheres"]

    try:
        column_list = ", ".join(columns)

        if wheres:
            where_list = " AND ".join(wheres)
            query = "SELECT {} FROM {} WHERE {};".format(column_list, table, where_list)
        else:
            query = "SELECT {} FROM {};".format(column_list, table)

        cursor.execute(query)
        query_set = cursor.fetchall()
        cursor.close()
        query_result = []
        for row in query_set:
            row = list(row)
            for i in range(len(row)):
                if type(row[i]) == bytearray:
                    row[i] = row[i].decode("utf-8")
            query_result.append(row)

        return Response(
            json.dumps({"query_result" : query_result}), 
            status = 200, 
            mimetype = 'application/json')

    except Exception as e:
        return Response("{}".format(e), status = 400, mimetype = 'application/json')


if __name__ == "__main__":
    app.run(host = "0.0.0.0", debug = True)
