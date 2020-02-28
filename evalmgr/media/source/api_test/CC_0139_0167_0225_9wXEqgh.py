from flask_restful import Resource
from flask import request 
import requests
from flask import jsonify,abort
import re
import pandas
import csv


class Ride(Resource):
    def post(self):
        new = {
        "created_by":request.json['created_by'],
        "timestamp" : request.json['timestamp'],#create new ride
        "source" :request.json['source'],
        "destination" : request.json['destination']
        }
        length = len(new['timestamp'])
        print(length)
        if length == 19:
            reg = r'[012345]|([012][0-9])|(3[01])-([0]{0,1}[1-9]|1[012])-\d\d\d\d:[0-5][0-9]-[0-5][0-9]-[012]{0,1}[0-9]'
            m = re.search(reg,new['timestamp'])
            print(m)
            if m:
                timestamp=new["timestamp"]
            else:
                abort(401)
        else:
            abort(401)
        writeRequestBody = {
        "table": 'ride',
        "columns": ["created_by","timestamp","source","destination"],
        "insert": [new["created_by"],new["timestamp"],new["source"],new["destination"]]
        }
        readRequestBody = {
        "table": "profile",
        "columns": ["username"],
        "where":"username="+new["created_by"]
        }
        r=requests.post('http://0.0.0.0/api/v1/read',json=readRequestBody,timeout=2)
        if(r.status_code==200):
            try:
                q=requests.post('http://0.0.0.0/api/v1/write',json=writeRequestBody,timeout=(3.05, 27))
                print(q.status_code)
                if(q.status_code==200):
                    return {}, 200
                else:
                    return {"status":"server error"}, 500
            except Exception as error:
                print(error)
                return {"status":"error"}, 500
        return {"status":"unsuccesful user doesn't exist"}, 401
class GetRide(Resource):
    def get(self):
        source = request.args.get('source',None)
        destination = request.args.get('destination',None)
        getRequestBody = {"table": "ride",
        "columns": ["id","created_by","timestamp"],
        "where":"source="+str(source)+ "AND destination="+str(destination)
        }
        with open('1.csv', mode='r') as infile:
            reader = csv.reader(infile)
            mydict = {rows[0]:rows[1] for rows in reader}
        if(mydict[source]and mydict[destination]):
            print(mydict[source])
            print(mydict[destination])
            r=requests.post('http://0.0.0.0/api/v1/read',json=getRequestBody,timeout=2)
            if(r.status_code==200):
                return r.json(),200
            else:
                return {"unsucc":"unsucc"},401
        else:
            return{"unsucc":"unsucc"},404
        #how to get data from read api call
        #printing read call data
class RideDetails(Resource):
    def get(self,rideId):
        getRequestBody = {
        "table": "ride",
        "columns": ["id","created_by","timestamp","source","destination","users"],
        "where":"id="+str(rideId)
        }
        readRequestBody = {
        "table": "ride",
        "columns": ["id"],
        "where":"id="+str(rideId)
        }
        r=requests.post('http://0.0.0.0/api/v1/read',json=readRequestBody,timeout=2)
        if(r.status_code==200):
            q=requests.post('http://0.0.0.0/api/v1/read',json=getRequestBody,timeout=2)
            if(q.status_code==200):
                return q.json(),200
            else:
                return{"unsucc":"unsucc"},500
        else:
            return{"status":"unsuc"},404
class joinRide(Resource):
    def post(self,rideId):
        new = {
        "username":request.json['username'], 
        }
        writeRequestBody = {
        "table": "ride",
        "column": new["username"],
        "where":"id="+str(rideId)
        }
        readRequestBody = {
        "table": "ride",
        "columns": ["id"],
        "where":"id="+str(rideId)
        }
        read2RequestBody = {
        "table": "profile",
        "columns": ["username"],
        "where":"username="+new["username"]
        }
        r=requests.post('http://0.0.0.0/api/v1/read',json=readRequestBody,timeout=2)
        print(r.json())
        s=requests.post('http://0.0.0.0/api/v1/read',json=read2RequestBody,timeout=2)
        print(s.json())
        if(r.status_code==200 and s.status_code==200):
            q=requests.post('http://0.0.0.0/api/v1/writeC',json=writeRequestBody,timeout=2)
            if(q.status_code==200):
                return{}
            else:
                return{"unsucc":"unsucc"},500
        else:
            return{"status":"unsuc"},404
class DeleteRide(Resource):
    def delete(self,rideId):
        deleteRequestBody = {
        "table": 'ride',
        "where":"id="+str(rideId)
        }
        readRequestBody = {
        "table": "ride",
        "columns": ["id"],
        "where":"id="+str(rideId)
        }
        r=requests.post('http://0.0.0.0/api/v1/read',json=readRequestBody,timeout=2)
        if(r.status_code==200):
            r=requests.post('http://0.0.0.0/api/v1/delete',json=deleteRequestBody,timeout=2)
            return{"status":"succesful"},200
        else:
            abort(400)
from flask_restful import Resource
from flask import request 
import requests
from flask import jsonify,abort
import re

class User(Resource):
    def put(self):
        new = {
        "username":request.json['username'],#create new ride
        "password" : request.json['password'],
        
        }
        length = len(new['password'])
        if length == 40:
            reg = r'[0-9a-fA-F]+'
            m = re.search(reg,new['password'])
            if m:
                password_fit=new["password"]
        else:
            abort(400)
        
        writeRequestBody = {
        "table": 'profile',
        "columns": ["username","password"],
        "insert": [new["username"],password_fit]
        }
        try:
            r=requests.post('http://0.0.0.0/api/v1/write',json=writeRequestBody,timeout=(3.05, 27))
            if(r.status_code==200):
                return {}, 201
            else:
                return {"status":"server error"}, 400
        except Exception as error:
            print(error)
            return {"status":"error"}, 500


class Del(Resource):
    def delete(self,username):
        deleteRequestBody = {
        "table": 'profile',
        "where":"username="+username
        }
        
        readRequestBody = {
        "table": "profile",
        "columns": ["username"],
        "where":"username="+username
        }
        r=requests.post('http://0.0.0.0/api/v1/read',json=readRequestBody,timeout=2)
        if(r.status_code==200):
        #condition to check username must exist but not part of rides
            s=requests.post('http://0.0.0.0/api/v1/delete',json=deleteRequestBody,timeout=2)
            return {},200
        else:
            return{"status":"not succesful"} ,400
        