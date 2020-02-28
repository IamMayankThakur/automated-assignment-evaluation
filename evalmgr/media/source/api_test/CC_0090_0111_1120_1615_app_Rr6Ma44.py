import flask
import pymongo
import requests
import ast
import re
import random
import json
from json import dumps
import csv
from enum import Enum
import datetime

app = flask.Flask(__name__)
account = {}
location = list()
#ride_id=0
#loading the locations into an array called location
with open('AreaNameEnum.csv') as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        next(reader)
        for row in reader:
                location.append(int(row[0]))
#coonecting to mongodb s
myclient = pymongo.MongoClient('mongodb://localhost:27017/')

#creating the database called mydatabase
mydb = myclient['mydatabase']


# we have made 3 collections....
#1. customers: it stores the username and password
#2.rides: it stores the entire ride detail
#3.users_rides:stores the ride id and the new users that are joining an existing ride.
#1 add user
@app.route("/api/v1/users", methods=["PUT"])
def add_user():
        mycol = mydb["customers"]
        username = flask.request.get_json()["username"]
        password = flask.request.get_json()["password"]
        if(mycol.find({"username":username}).count()> 0):
                code = 400
        else:
                read_url = "http://52.3.9.127/api/v1/db/read"
                write_url = "http://52.3.9.127/api/v1/db/write"
                d = {}
                d["table"] = "customers"
                d["column"] = ["username"]
                d["data"] = [username]
                l = requests.post(url =read_url, json = d)
                l = ast.literal_eval(l.text)
                if(len(l)==2):
                        if(re.search(("^[a-fA-F0-9]{40}$"), password)):
                                mydict = dict()
                                mydict["table"] = "customers"
                                mydict["column"] = ["username", "password"]
                                mydict["data"] = [username, password]
                                l1 = requests.post(url =write_url, json = mydict)
                                code = 201
                        else:
                                code = 400
        return flask.Response("{}", status=code)


#2 delete user
@app.route("/api/v1/users/<name>", methods=["DELETE"])
def remove_user(name):
        #print("hello")
        mycol=mydb["customers"]
        if(mycol.find({"username":name}).count() == 0):
                code = 400
        else:
                mycol.delete_one( {"username":name})
                code = 200
        return flask.Response("{}", status=code)

#3 create ride
@app.route("/api/v1/rides", methods=["POST"])
def createRide():
        ride_id=1
        mycol = mydb["customers"]
        mycol1=mydb["rides"]
        d=dict()
        d["table"]="rides"
        timestamp = flask.request.get_json()["timestamp"]
        created_by = flask.request.get_json()["created_by"]
        source = int(flask.request.get_json()["source"])
        destination = int(flask.request.get_json()["destination"])
        write_url = "http://52.3.9.127/api/v1/db/write"
        if(mycol.find({"username":created_by}).count()== 0):
               # print("Username does not exist!")
                code = 400
        else:
                while (1):
                        ride_id=ride_id+1
                        if(mycol1.find({"rideId":ride_id}).count()==0):#if ride_id dosent exist then break and add in the rides table
                                break
                d["column"] = ["rideId", "timestamp", "created_by", "source", "destination"]
                d["data"] = [ride_id, timestamp, created_by, source, destination]
                l1 = requests.post(url = write_url, json = d)
                code = 201
        return flask.Response("{}", status=code)

#4 list all upcoming rides for a given source and destnation
@app.route("/api/v1/rides", methods=["GET"])

def list_upcoming_rides():
        source =int( request.args.get('source')
        destination = request.args.get('destination')
        #source = int(flask.request.get_json()["source"])
        #destination = int(flask.request.get_json()["destination"])
        mycol = mydb["rides"]
        if (source not in locations) or (destination not in locations) or (source == destination):
                return flask.Response("{}", status=400)
        current = datetime.datetime.now()
        #x=list(mycol.find({"source":source,"destination":destination},{"rideId":1,"username":1,"timestamp":1}));
        x=list(mycol.find({"source":source,"destination":destination}));
        #keylist=["rideId","username","timestamp"]
        l=[]
        for i in x:
                #y=list(filter(lambda d:(d in keylist),x))
                j={}
                j["rideId"]=i["rideId"]
                j["username"]=i["created_by"]
                time = datetime.datetime.strptime(i["timestamp"],"%d-%m-%Y:%S-%M-%H")
                current = datetime.datetime.now()
                if time >= current:
                        j["timestamp"]=i["timestamp"]
                        l.append(j)
                else:
                        continue
        if len(l)==0:
                code = 204
        else:   
                code=200
        return flask.Response(json.dumps(l),status=code,mimetype="application/json")

#5 list all the details of a given ride
@app.route("/api/v1/rides/<ride_id>", methods=["GET"])
def details_ride(ride_id):
        ride_id=int(ride_id)
        mycol=mydb["rides"]
        user_ride=mydb["users_rides"]
        if(mycol.find({"rideId":ride_id}).count() == 0):
                code = 405
                print("Ride doesn't exist")
        else:
                y=list(user_ride.find({"rideId":ride_id}))
                x=list(mycol.find({"rideId":ride_id}))
        k=[]
        for i in y:
                k.append(i["username"])
                
        l=[]
        for i in x:
                #y=list(filter(lambda d:(d in keylist),x))
                j={}
                j["rideId"]=i["rideId"]
                j["Created_by"]=i["created_by"]
                j["users"]=k
                j["timestamp"]=i["timestamp"]
                j["source"]=i["source"]
                j["destination"]=i["destination"]
                
                        
                l.append(j)
        if len(l)==0:
                code = 204
        else:
                code=200
        return flask.Response(json.dumps(l),status=code,mimetype="application/json")

#6 joining an existing ride
@app.route("/api/v1/rides/<ride_id>",methods=["POST"])
def joining_ride(ride_id):
        ride_id=int(ride_id)
        mycol=mydb["rides"]
        mycol1=mydb["customers"]
        username = flask.request.get_json()["username"]
        if((mycol.find({"rideId":ride_id}).count() == 0) or (mycol1.find({"username":username}).count==0)):
                code = 405
               # print("Ride doesn't exist")     
                return flask.Response("{}", status=code)
        else:
                read_url = "http://52.3.9.127/api/v1/db/read"
                write_url = "http://52.3.9.127/api/v1/db/write"
                d = {}
                d["table"] = "users_rides"
                d["column"] = ["rideId","username"]
                d["data"] = [ride_id,username]
                l1 = requests.post(url =write_url, json =d)
                code=200
                return flask.Response("{}", status=code)
                

#7 delete a ride
@app.route("/api/v1/rides/<ride_id>",methods=["DELETE"])
def delete_ride(ride_id):
        ride_id=int(ride_id)
        mycol=mydb["rides"]
        if(mycol.find({"rideId":ride_id}).count() == 0):
                code = 400
        else:
                mycol.delete_one( {"rideId":ride_id})
                code = 200
        return flask.Response("{}", status=code)


#8 read database
@app.route("/api/v1/db/read", methods=["POST"])
def read_db():
        table = flask.request.get_json()["table"]
        columns = flask.request.get_json()["column"]
        where = flask.request.get_json()["data"]
        mycol = mydb[table]
        mydict = dict()
        for i in range(len(where)):
                mydict[columns[i]] = where[i]
        x = mycol.find(mydict, {'_id':False})
        l = list()
        for i in x:
                print(i)
                l.append(i)
        return flask.jsonify(str(l))

#9 write database
@app.route("/api/v1/db/write", methods=["POST"])
def write_db():
        table = flask.request.get_json()["table"]
        column = flask.request.get_json()["column"]
        data = flask.request.get_json()["data"]
        mycol = mydb[table]
        mydict = dict()
        for i in range(len(data)):
                mydict[column[i]] = data[i]
        x = mycol.insert_one(mydict)
        print("Inserted, id: ", x.inserted_id)
                return flask.jsonify({})


if __name__ == "__main__":
        app.debug=True
        app.run(debug=True,host='0.0.0.0')

        





