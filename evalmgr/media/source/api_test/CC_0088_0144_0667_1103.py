import json, requests, collections
from datetime import datetime
from flask import Flask, request, jsonify
from models import db, Ride, User
from requests.models import Response
import pandas as pd


def clearData():
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        db.session.execute(table.delete())
    db.session.commit()


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/rideshare'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    clearData()
    db.create_all()   


df = pd.read_csv("AreaNameEnum.csv")
noRows = df.shape[0]


# 1: Add User
@app.route('/api/v1/users', methods = ["PUT"])
def addUser():
    '''
    Add User based on data from PUT request.
    '''
    result = dict()
    if request.method == 'PUT':
        data = request.get_json()
        rurl = "http://127.0.0.1:5000/api/v1/db/read"
        readObjToPass = {"username": data["username"], "table":"User", "caller":"addUser"}
        res = requests.post(rurl, json = readObjToPass)
        if res.status_code == 200:
            wurl = "http://127.0.0.1:5000/api/v1/db/write"
            writeObjToPass = {"username": data["username"], "password": data["password"], "table":"User", "caller":"addUser"}
            resp = requests.post(wurl, json = writeObjToPass)
            return jsonify(result), resp.status_code
        return jsonify(result), res.status_code
    else:
        return jsonify(result), 405


# 2: Remove User
@app.route('/api/v1/users/<username>', methods = ["DELETE"])
def removeUser(username):
    '''
    Remove a user with specified `username`.
    '''
    result = dict()
    if request.method == 'DELETE':
        rurl = "http://127.0.0.1:5000/api/v1/db/read"
        readObjToPass = {"username":username, "table":"User", "caller":"removeUser"}
        res = requests.post(rurl, json = readObjToPass)
        if res.status_code == 200:
            wurl = "http://127.0.0.1:5000/api/v1/db/write"
            writeObjToPass = {"username": username, "table":"User", "caller":"removeUser"}
            resp = requests.post(wurl, json = writeObjToPass)
            return jsonify(result), resp.status_code
        else:
            return jsonify(result), res.status_code
    else:
        return jsonify(result), 405


# 3: Create New Ride
@app.route('/api/v1/rides', methods = ["POST"])
def createRide():
    '''
    Create a new ride, deriving data from POST request.
    '''
    result = dict()
    if request.method == 'POST':
        data = request.get_json()
        rurl = "http://127.0.0.1:5000/api/v1/db/read"
        readObjToPass = {"username": data["created_by"], "table":"User", "caller":"createRide"}
        res = requests.post(rurl, json = readObjToPass)
        if res.status_code == 200:
            wurl = "http://127.0.0.1:5000/api/v1/db/write"
            writeObjToPass = {"created_by": data["created_by"],"timestamp":data["timestamp"],
                    "source":data["source"],"destination":data["destination"],"table":"Ride","caller":"createRide"}
            resp = requests.post(wurl, json = writeObjToPass)
            return jsonify(result), resp.status_code
        else:
            return jsonify(result), res.status_code
    else:
        return jsonify(result), 405
    

# 4: List Upcoming Rides
@app.route('/api/v1/rides', methods = ["GET"])
def listUpcomingRides():
    '''
        Prints all the rides based on the source and destination specified.
    '''
    result = dict()
    if request.method == 'GET':
        source = request.args['source']
        destination = request.args['destination']
        if source and destination:
            rurl = "http://127.0.0.1:5000/api/v1/db/read"
            readObjToPass = {"source":source, "destination":destination, "table":"Ride", "caller":"listUpcomingRides"}
            resp = requests.post(rurl, json = readObjToPass)
            if resp.text:
                result = json.loads(resp.text)
            return jsonify(result), resp.status_code
        else:
            return jsonify(result), 400
    else:
        return jsonify(result), 405

    
# 5: List Ride Details
@app.route('/api/v1/rides/<rideId>', methods = ["GET"])
def listRideDetails(rideId):
    '''
    List Ride details based on `rideId`.
    '''
    result = dict()
    if request.method == 'GET':
        rurl = "http://127.0.0.1:5000/api/v1/db/read"
        readObjToPass = {"rideId":rideId, "table":"Ride", "caller":"listRideDetails"}
        resp = requests.post(rurl, json = readObjToPass)
        if resp.text:
            result = json.loads(resp.text)
        return jsonify(result), resp.status_code
    else:
        return jsonify(result), 405


# 6: Join Existing Ride
@app.route('/api/v1/rides/<rideId>', methods = ["POST"])
def joinRide(rideId):
    result = dict()
    if request.method == 'POST':
        data = request.get_json()
        rurl = "http://127.0.0.1:5000/api/v1/db/read"
        readObjToPass = {"username": data["username"], "rideId":rideId, "table":"Ride", "caller":"joinRide"}
        res = requests.post(rurl, json = readObjToPass) 
        if res.status_code == 200:
            wurl = "http://127.0.0.1:5000/api/v1/db/write"
            writeObjToPass = {"username": data["username"], "rideId":rideId, "table":"Ride", "caller":"joinRide"}
            resp = requests.post(wurl,json = writeObjToPass)
            return jsonify(result), resp.status_code
        else:
            return jsonify(result), res.status_code
    else:
        return jsonify(result), 405


# 7: Delete a Ride from Database  
@app.route('/api/v1/rides/<rideId>', methods = ["DELETE"])
def deleteRide(rideId):
    result = dict()
    if request.method == "DELETE":
        rurl = "http://127.0.0.1:5000/api/v1/db/read"
        readObjToPass = {"rideId":rideId, "table":"Ride", "caller":"deleteRide"}
        res = requests.post(rurl, json = readObjToPass) 
        if res.status_code == 200:
            wurl = "http://127.0.0.1:5000/api/v1/db/write"
            writeObjToPass = {"rideId": rideId, "table":"Ride", "caller":"deleteRide"}
            resp = requests.post(wurl,json = writeObjToPass)
            return jsonify(result), resp.status_code
        return jsonify(result), res.status_code
    else:
        return jsonify(result), 405


# 8: Write to Database
@app.route('/api/v1/db/write', methods = ["POST"])
def writetoDB():
    data = request.get_json()
    if data["table"] == "User":
        # Add a new User
        if data["caller"] == "addUser":
            responseToReturn = Response()
            if checkHash(data["password"]):
                newUser = User(username = data["username"], password = data["password"])
                db.session.add(newUser)
                db.session.commit()
                responseToReturn.status_code = 201
            else:
                responseToReturn.status_code = 400
            return (responseToReturn.text, responseToReturn.status_code, responseToReturn.headers.items())
        # Remove an existing User     
        elif data["caller"] == "removeUser":
            User.query.filter_by(username = data["username"]).delete()
            Ride.query.filter_by(created_by = data["username"]).delete()
            db.session.commit()
            responseToReturn = Response()
            responseToReturn.status_code = 200
            return (responseToReturn.text, responseToReturn.status_code, responseToReturn.headers.items())

    elif data["table"] == "Ride":
        # Add a new Ride
        if data["caller"] == "createRide":
            source = int(data["source"])
            dest = int(data["destination"])
            responseToReturn = Response()
            if source in range(1, noRows + 1) and dest in range(1, noRows + 1):
                newRide = Ride(created_by = data["created_by"], username = "", timestamp = data["timestamp"],
                        source = source, destination = dest)
                db.session.add(newRide)
                db.session.commit()
                responseToReturn.status_code = 201
            else:
                responseToReturn.status_code = 400
            return (responseToReturn.text, responseToReturn.status_code, responseToReturn.headers.items())

        elif data["caller"] == "joinRide":
            rideExists = Ride.query.filter_by(ride_id = data["rideId"]).first()
            if rideExists.username:
                rideExists.username += ", " + data["username"]
            else:
                rideExists.username += data["username"]
            db.session.commit()
            responseToReturn = Response()
            responseToReturn.status_code = 200
            return (responseToReturn.text, responseToReturn.status_code, responseToReturn.headers.items())

        elif data["caller"] == "deleteRide":
            Ride.query.filter_by(ride_id = data["rideId"]).delete()
            db.session.commit()
            responseToReturn = Response()
            responseToReturn.status_code = 200
            return (responseToReturn.text, responseToReturn.status_code, responseToReturn.headers.items())


# 9: Read from database
@app.route('/api/v1/db/read', methods = ["POST"])
def readfromDB():
    data = request.get_json()
    if data["table"] == "User":
        checkUserSet = {"removeUser", "createRide"}
        if data["caller"] in checkUserSet:
            userExists = User.query.filter_by(username = data["username"]).all()
            responseToReturn = Response()
            if userExists:
                responseToReturn.status_code = 200
            else:
                responseToReturn.status_code = 400
            return (responseToReturn.text, responseToReturn.status_code, responseToReturn.headers.items())
        
        elif data["caller"] == "addUser":
            userExists = User.query.filter_by(username = data["username"]).all()
            responseToReturn = Response()
            if userExists:
                responseToReturn.status_code = 400
            else:
                responseToReturn.status_code = 200
            return (responseToReturn.text, responseToReturn.status_code, responseToReturn.headers.items())
        
    elif data["table"] == "Ride":
        if data["caller"] == "listUpcomingRides":
            rides = Ride.query.all()
            returnObj = []
            for ride in rides:
                if ride.source == data["source"] and ride.destination == data["destination"]:
                    if timeAhead(ride.timestamp):
                        newObj = {"rideId":ride.ride_id, "username":ride.created_by, "timestamp":ride.timestamp}
                        returnObj.append(newObj)
            responseToReturn = Response()
            if not returnObj:
                responseToReturn.status_code = 204
            else:
                responseToReturn.status_code = 200
            return (jsonify(returnObj), responseToReturn.status_code, responseToReturn.headers.items())
        
        elif data["caller"] == "listRideDetails":
            rides = Ride.query.all()
            userArray = []
            dictToReturn = dict()
            responseToReturn = Response()
            rideNotFound = True
            for ride in rides:
                if ride.ride_id == int(data["rideId"]):
                    rideNotFound = False
                    userArray = ride.username.split(", ")
                    if userArray[0] == "":
                        userArray.clear()
                    responseToReturn.status_code = 200
                    keyValues = [("rideId", ride.ride_id), ("created_by", ride.created_by),
                    ("users", userArray), ("timestamp", ride.timestamp), ("source", ride.source),
                    ("destination", ride.destination)]
                    dictToReturn = collections.OrderedDict(keyValues)
                    break
            if rideNotFound:
                responseToReturn.status_code = 204
            return (jsonify(dictToReturn), responseToReturn.status_code, responseToReturn.headers.items())

        elif data["caller"] == "deleteRide":
            rideExists = Ride.query.filter_by(ride_id = data["rideId"]).all()
            responseToReturn = Response()
            if rideExists:
                responseToReturn.status_code = 200
            else:
                responseToReturn.status_code = 400
            return (responseToReturn.text, responseToReturn.status_code, responseToReturn.headers.items())

        elif data["caller"] == "joinRide":
            userExists = User.query.filter_by(username = data["username"]).all()
            rideExists = Ride.query.filter_by(ride_id = data["rideId"]).all()
            responseToReturn = Response()
            if userExists and rideExists:
                responseToReturn.status_code = 200
            else:
                responseToReturn.status_code = 400
            return (responseToReturn.text, responseToReturn.status_code, responseToReturn.headers.items())


def checkHash(password):
    if len(password) == 40:
        password = password.lower()
        charSet = {"a", "b", "c", "d", "e", "f"}
        numSet = {'1','2','3','4','5','6','7','8','9','0'}
        for char in password:
            if char not in charSet and char not in numSet:
                return False
        return True
    return False


def timeAhead(timestamp):
    currTimeStamp = datetime.now().isoformat(' ', 'seconds')
    currTimeStamp = datetime.strptime(currTimeStamp, "%Y-%m-%d %H:%M:%S")
    convertedTimeStamp = datetime.strptime(timestamp, "%d-%m-%Y:%S-%M-%H")
    if currTimeStamp < convertedTimeStamp:
        return True
    return False


if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0')