from gevent import monkey
monkey.patch_all()
from gevent.pywsgi import WSGIServer
import os
import json
import user_requests
import database

from flask import Flask
from flask import request, abort
from flask_sqlalchemy import SQLAlchemy
from flask import Response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy_session import flask_scoped_session
from werkzeug.exceptions import BadRequest
from werkzeug.exceptions import NotFound
from werkzeug.exceptions import InternalServerError
from werkzeug.exceptions import MethodNotAllowed
import traceback
import requests as r

port = 8000
app = Flask(__name__)

localhost_url = "http://127.0.0.1:%d" %(port)

@app.before_request
def before_request():
    if request.method == 'PUT' or request.method == 'POST':
        if not request.is_json:
            raise BadRequest('Content-Type unrecognized')

@app.route("/api/v1/users", methods={'PUT'})
def add_user():
    body = request.json
    ## this step is to validate
    user_request = user_requests.CreateUserRequests(body)
    body['action'] = 'get_user'
    response = r.post("%s/api/v1/db/read" % (localhost_url), json = body)

    print (response.text)

    if response.status_code == 200:
        raise BadRequest("user %s already exists" % (user_request.getUsername()))

    body['action'] = 'add_user'

    response = r.post("%s/api/v1/db/write" % (localhost_url), json = body)

    print (response.text)

    if response.status_code != 201:
        raise BadRequest("some error occurred")

    return Response(None, status=201, mimetype='application/json')


@app.route("/api/v1/users/<username>", methods={'DELETE'})
def delete_user(username):
    body = {}
    body['action'] = 'get_user'
    body['username'] = username
    response = r.post("%s/api/v1/db/read" % (localhost_url), json = body)

    if response.status_code != 200:
        raise BadRequest('user %s not found' % (username))

    body['action'] = 'delete_user'

    response = r.post("%s/api/v1/db/write" % (localhost_url), json = body)

    if response.status_code != 201:
        raise BadRequest("some error occurred")

    return Response(None, status=200, mimetype='application/json')


@app.route("/api/v1/rides", methods={'POST'})
def add_ride():
    body = {}
    body['action'] = 'get_user'
    body['username'] = request.json['created_by']
    response = r.post("%s/api/v1/db/read" % (localhost_url), json = body)

    if response.status_code != 200:
        raise BadRequest('user %s not found' % (username))

    body = request.json
    body['action'] = 'add_ride'
    ride_request = user_requests.CreateRideRequests(body)

    response = r.post("%s/api/v1/db/write" % (localhost_url), json = body)

    if response.status_code != 201:
        print (response.text)
        raise BadRequest("some error occurred")

    return Response(response.text, status=201, mimetype='application/json')


@app.route("/api/v1/rides", methods={'GET'})
def list_upcoming_ride():
    source = ""
    destination = ""
    try:
        source = user_requests.CreateRideRequests.validateSource(
            request.args.get("source"))
        destination = user_requests.CreateRideRequests.validateDestination(
            request.args.get("destination"))
    except Exception as ex:
        raise BadRequest("request arguments source, destination are mandatory")

    body = {
        "action": "list_upcoming_ride",
        "source": source,
        "destination": destination
    }

    response = r.post("%s/api/v1/db/read" % (localhost_url), json = body)
    print(type(response.text))
    if(response.text=='[]'):
    	return Response(response.text,status=204,mimetype='application/json')
    if response.status_code != 200:
        raise BadRequest("some error occurred")
    
    return Response(response.text, status=200, mimetype='application/json')


@app.route("/api/v1/rides/<int:rideId>", methods={'GET'})
def get_ride(rideId):
    body = {
        "action": "get_ride",
        "rideId": rideId
    }

    response = r.post("%s/api/v1/db/read" % (localhost_url), json = body)

    if response.status_code != 200:
        raise BadRequest("some error occurred")
    
    return Response(response.text, status=200, mimetype='application/json')


@app.route("/api/v1/rides/<int:rideId>", methods={'POST'})
def join_ride(rideId):
    if 'username' not in request.json:
        raise BadRequest("username is mandatory in request")

    body = request.json
    body["action"] = "join_ride"
    body["rideId"] = rideId
    response = r.post("%s/api/v1/db/write" % (localhost_url), json = body)

    if response.status_code != 201:
        raise BadRequest("some error occurred")
    
    return Response(None, status=200, mimetype='application/json')


@app.route("/api/v1/rides/<int:rideId>", methods={'DELETE'})
def delete_ride(rideId):
    body = {}
    body["action"] = "delete_ride"
    body["rideId"] = rideId
    response = r.post("%s/api/v1/db/write" % (localhost_url), json = body)

    if response.status_code != 201:
        raise BadRequest("some error occurred")
    
    return Response(None, status=200, mimetype='application/json')

def db_create_ride(json):
    if "created_by" not in json:
        raise BadRequest("created_by user not passed")
    if "source" not in json:
        raise BadRequest("source not passed")
    if "destination" not in json:
        raise BadRequest("destination not passed")
    if "timestamp" not in json:
        raise BadRequest("timestamp not passed")

    timestamp = user_requests.CreateRideRequests.validateTimestamp(json["timestamp"])

    ride = database.Ride(created_by=json["created_by"], source=json["source"], destination = json["destination"], timestamp = timestamp)
    ride.store()

    database.RideUsers(rideId=ride.rideId, username=json["created_by"]).store()
    return ride.rideId

def db_delete_ride(json):
    if "rideId" not in json:
        raise BadRequest("rideId not passed")
    database.Ride.getByRideId(json["rideId"]).delete()

def db_join_ride(json):
    if "rideId" not in json:
        raise BadRequest("rideId not passed")
    if "username" not in json:
        raise BadRequest("username not passed")

    ride = database.Ride.getByRideId(json["rideId"])
    if ride is not None:
        database.RideUsers(
            username=json["username"], rideId=json["rideId"]).store()
    else:
        raise BadRequest("rideId %d not found" % json["rideId"])

def db_get_ride(json):
    if "rideId" not in json:
        raise BadRequest("rideId not passed")

    ride = database.Ride.getByRideId(json["rideId"])
    if ride is not None:
        users = list()
        for ride_user in database.RideUsers.getByRideId(ride.rideId):
            users.append(ride_user.username)
    response = {"rideId": ride.rideId, "username": users,
                "timestamp": ride.timestamp.strftime("%d-%m-%Y:%S-%M-%H"), "source": ride.source, "destination": ride.destination}
    return response

def db_list_ride(json):
    if "source" not in json:
        raise BadRequest("source not passed")
    if "destination" not in json:
        raise BadRequest("destination not passed")
    
    rides = database.Ride.listUpcomingRides(json["source"], json["destination"])
    response = list()
    if rides is not None and len(rides) > 0:
        for ride in rides:
            users = list()
            for ride_user in database.RideUsers.getByRideId(ride.rideId):
                users.append(ride_user.username)
            response.append({"rideId": ride.rideId, "username": users,
                                "timestamp": ride.timestamp.strftime("%d-%m-%Y:%S-%M-%H")})
    return response

def db_add_user(json):
    if "username" not in json:
        raise BadRequest("username not passed")
    if "password" not in json:
        raise BadRequest("password not passed")

    database.User(username = json["username"], password = json["password"]).store()

def db_get_user(json):
    user = database.User.getByUsername(json["username"])
    if user is None:
        raise BadRequest("user not found")
    return {"username": user.username, "password": user.password}

def db_delete_user(json):
    if "username" not in json:
        raise BadRequest("username not passed")
    database.User.getByUsername(json["username"]).delete()

@app.route("/api/v1/db/write", methods={'POST'})
def write_to_db():
    body = request.get_json()
    if "action" not in body:
        raise BadRequest("action not passed")

    action = body["action"]
    try:
        if action == "add_user":
            db_add_user(body)
            return Response(None, status=201, mimetype='application/json')

        elif action == "delete_user":
            db_delete_user(body)
            return Response(None, status=201, mimetype='application/json')

        elif action == "add_ride":
            rideId = db_create_ride(body)
            return Response(json.dumps({"rideId": rideId}), status=201, mimetype='application/json')
        
        elif action == "delete_ride":
            db_delete_ride(body)
            return Response(None, status=201, mimetype='application/json')
        
        elif action == "join_ride":
            db_join_ride(body)
            return Response(None, status=201, mimetype='application/json')
        else:
            raise BadRequest("unrecognized action %s" % (action))
    except BadRequest as ex:
        raise
    except Exception as ex:
        print(ex)
        raise BadRequest("invalid request")



@app.route("/api/v1/db/read", methods={'POST'})
def read_from_db():
    body = request.get_json()
    if "action" not in body:
        raise BadRequest("action not passed")
    
    action = body["action"]
    
    if action == "list_upcoming_ride":
        return Response(json.dumps(db_list_ride(body)), status=200, mimetype='application/json')
    elif action == "get_ride":
        return Response(json.dumps(db_get_ride(body)), status=200, mimetype='application/json')
    elif action == "get_user":
        return Response(json.dumps(db_get_user(body)), status=200, mimetype='application/json')
    else:
        raise BadRequest("unrecognized action %s" % (action))
    


@app.route("/")
def unsupported_path():
    raise MethodNotAllowed()


if __name__ == "__main__":
    project_dir = os.path.dirname(os.path.abspath(__file__))
    database_file = "sqlite:///{}".format(
        os.path.join(project_dir, "rideshare.db"))

    # initialize database
    engine = create_engine(database_file, echo=True)
    database.Base.metadata.create_all(engine, checkfirst=True)
    session_factory = sessionmaker(autoflush=True,bind=engine)

    session = flask_scoped_session(session_factory, app)

    # app.run(host='0.0.0.0', port=port,debug=True)
    http_server = WSGIServer(('', 8000), app)
    http_server.serve_forever()

