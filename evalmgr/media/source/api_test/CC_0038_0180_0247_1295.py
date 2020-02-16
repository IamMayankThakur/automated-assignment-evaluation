import re
import os
import ast
import requests
import json
import csv
import collections
from flask_api import status
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from flask import Flask, jsonify, request, abort,redirect, url_for, session, Response

app = Flask(__name__)
app.config['SECRET_KEY'] = "Ride Share api"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rideshare.db'

location = collections.defaultdict(str)
with open('AreaNameEnum.csv', 'r') as fin:
    dictr = csv.DictReader(fin)
    for line in dictr:
        location[int(line['Area No'])] = line['Area Name']

session_options = {'autocommit':False, 'autoflush':False}
db = SQLAlchemy(app)

SHA1 = re.compile(r'\b[a-fA-F0-9]{40}\b')
ddformat = re.compile(r'\d{2}-\d{2}-\d{4}:\d{2}-\d{2}-\d{2}')
headers = {'Content-Type': 'application/json', 'Accept':'application/json'}
writeURL = 'http://127.0.0.1:5000/api/v1/db/write'
readURL = 'http://127.0.0.1:5000/api/v1/db/read'
METHODS = ['GET', 'PUT', 'POST', 'DELETE', 'PATCH', 'COPY', 'HEAD', 'OPTIONS', 'LINK'
                , 'UNLINK', 'PURGE', 'LOCK', 'UNLOCK', 'PROPFIND', 'VIEW']

class Users(db.Model):
    __tablename__ = 'users'
    username = db.Column('username', db.String(100), primary_key=True)
    password = db.Column('password', db.String(40), nullable=False)
    rides_created_by = db.relationship('Rides', cascade="all, delete", backref = 'creator')
    def __init__(self, username, password):
        self.username = username
        self.password = password


class Rides(db.Model):
    __tablename__ = "rides"
    ride_id = db.Column('ride_id', db.Integer, primary_key=True)
    created_by = db.Column('created_by', db.String(100), db.ForeignKey('users.username'))
    timestamp = db.Column('timestamp', db.String(100), nullable=False)
    source = db.Column('source', db.Integer, nullable=False)
    destination = db.Column('destination', db.Integer, nullable=False)
    joined_users = db.Column('joined_users',db.String(1000),nullable=False)

    def __init__(self, created_by, timestamp, source, destination,joined_users):
        self.created_by = created_by
        self.timestamp = timestamp
        self.source = source
        self.destination = destination
        self.joined_users=joined_users

db.create_all()

# 1.ADD USER (Done)
@app.route('/api/v1/users' , methods = ['PUT'])
def AddUser():
    if(request.method=='PUT'):
        req = request.get_json()
        try:
            if(not(re.match(SHA1, req['password']))):
                raise ValueError
        except ValueError:
            return Response(status=400)
        adduser = {"table" : "Users", "insert" : req }
        response = (requests.post(writeURL, data = json.dumps(adduser), headers = headers))
        response = response.json()
        #print("wkejfiewjpfwogjwg",response)
        return Response(status=response['status_code'])
    return Response(status=405)

# 2.REMOVE USER (Done)
@app.route('/api/v1/users/<uname>', methods = ['DELETE'])
def RemoveUser(uname):
    if request.method=='DELETE':
        checkuser = {'table':'Users', 'method':'existence', 'where': uname}
        Exists = (requests.post(readURL, data = json.dumps(checkuser), headers = headers)).json()
        if(Exists['Exists']):
            removeuser = {"table" : "Users" , "delete" : uname}
            response = (requests.post(writeURL, data = json.dumps(removeuser), headers = headers)).json()
            return Response(status=response['status_code'])
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

# 3.Add Ride (Done)
@app.route('/api/v1/rides',methods = ['POST'])
def AddRide():
    if(request.method=='POST'):
        req = request.get_json()
        uname = req['created_by']
        checkuser = {'table':'Users', 'method':'existence', 'where': uname}
        Exists = (requests.post(readURL, data = json.dumps(checkuser), headers = headers)).json()
        currtime = datetime.now().strftime('%d-%m-%Y:%S-%M-%H')
        if(Exists['Exists'] and (ddformat.match(req['timestamp']) is not None) and (currtime < req['timestamp'])):
            addride = {"table" : "Ride" , "insert": req}
            response = (requests.post(writeURL, data = json.dumps(addride), headers = headers)).json()
            return Response(status=response['status_code'])
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


# 4.Fetch Rides (Done)
@app.route('/api/v1/rides',methods = ['GET'])
def FetchRides():
    if(request.method=='GET'):
        source = int(request.args.get('source'))
        destination = int(request.args.get('destination'))
        if(source == None or destination == None or not(source in location) or not(destination in location)):
            return Response(status=status.HTTP_204_NO_CONTENT)
        currtime = datetime.now().strftime('%d-%m-%Y:%S-%M-%H')
        queryride = {'table': 'Rides', 'method':'query', "columns" : ['timestamp', 'source', 'destination']
                       , "where" : [currtime, source, destination]}
        response = (requests.post(readURL, data = json.dumps(queryride), headers = headers)).json()
        if(len(response['Result'])>0):
            return jsonify(response['Result'])
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


# 5.List Rides (Done)
@app.route('/api/v1/rides/<rideId>',methods=['GET'])
def listrides(rideId):
    if(request.method=='GET'):
        checkride = {'table':'Rides', 'method':'existence', 'where': int(rideId)}
        Exists = (requests.post(readURL, data = json.dumps(checkride), headers = headers)).json()
        if(Exists['Exists']):
            getride={'table':'Rides', 'method': 'list_details','where': int(rideId)}
            response = (requests.post(readURL, data = json.dumps(getride), headers = headers)).json()
            return jsonify(response['Result'][0])
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


# 6.Join an existing ride (Done)
@app.route('/api/v1/rides/<rideId>',methods=['POST'])
def joinride(rideId):
    if(request.method=='POST'):
        req = request.get_json()
        checkuser = {'table':'Users', 'method':'existence', 'where': req['username']}
        Existuser = (requests.post(readURL, data = json.dumps(checkuser), headers = headers)).json()
        checkride = {'table':'Rides', 'method':'existence', 'where': int(rideId)}
        Existride = (requests.post(readURL, data = json.dumps(checkride), headers = headers)).json()
        if(Existuser['Exists'] and Existride['Exists']):
            joinride={'table':'Rides', 'method':'join','where': [req['username'], int(rideId)]}
            response = (requests.post(writeURL, data = json.dumps(joinride), headers = headers)).json()
            return Response(status=response['status_code'])
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


# 7.Delete Ride (Done)
@app.route('/api/v1/rides/<rideId>', methods = ['DELETE'])
def DeleteRide(rideId):
    if request.method=='DELETE':
        checkride = {'table':'Rides', 'method':'existence', 'where': int(rideId)}
        Exists = (requests.post(readURL, data = json.dumps(checkride), headers = headers)).json()
        if(Exists['Exists']):
            delride = {"table" : "Rides" , "delete" : rideId}
            response = (requests.post(writeURL, data = json.dumps(delride), headers = headers)).json()
            return Response(status=response['status_code'])
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


#8. DB Write
@app.route('/api/v1/db/write', methods = ['POST'])
def DBWrite():
    if(request.method == 'POST'):
        Request = (request.get_data()).decode()
        Request = ast.literal_eval(Request)
        if('insert' in Request):
            try:
                if(Request['table'] == 'Users'):
                    obj = Users(Request['insert']['username'], Request['insert']['password'])
                elif(Request['table'] == 'Ride'):
                    obj= Rides(created_by=Request['insert']['created_by'], timestamp=Request['insert']['timestamp']
                    , source=int(Request['insert']['source']), destination=int(Request['insert']['destination']) , joined_users='')
                db.session.add(obj)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                return {'status_code': 400}
            return {'status_code': 201}
        elif('delete' in Request):
            if(Request['table'] == 'Users'):
                db.session.query(Users).filter_by(username = Request['delete']).delete()
                db.session.query(Rides).filter_by(created_by = Request['delete']).delete()
            if(Request['table'] == 'Rides'):
                db.session.query(Rides).filter_by(ride_id = Request['delete']).delete()
            db.session.commit()
            return {'status_code': 200}
        elif(Request['table']=='Rides' and Request['method']=='join'):
            quer_res = db.session.query(Rides).filter_by(ride_id = Request['where'][1]).all()
            if((Request['where'][0] not in quer_res[0].joined_users) and (Request['where'][0] not in quer_res[0].created_by)):
                newusersadded = quer_res[0].joined_users+"$#"+Request['where'][0]
                db.session.query(Rides).filter_by(ride_id=Request['where'][1]).update(dict(joined_users=newusersadded))
                db.session.commit()
                return {'status_code': 200}
            return {'status_code':400}
    return {'status_code': 405}

#9. DB Read
@app.route('/api/v1/db/read', methods = ['POST'])
def DBRead():
    if(request.method=='POST'):
        Request = (request.get_data()).decode()
        Request = ast.literal_eval(Request)
        if(Request['table']=='Rides'):
            if(Request['method']=='query'):
                quer_res = db.session.query(Rides).filter_by(source = Request['where'][1]).filter_by(destination = Request['where'][2]).all()
                response_all = []
                for row in quer_res:
                    rowd = {}
                    if row.timestamp > Request['where'][0]:
                        rowd['rideId'] = row.ride_id
                        rowd['username'] = row.created_by
                        rowd['timestamp'] = row.timestamp
                        response_all.append(rowd)
                response = {"Result" : response_all}

            if(Request['method']=='list_details'):
                quer_res = db.session.query(Rides).filter_by(ride_id=Request['where'])
                response_all = []
                for row in quer_res:
                    rowd = {}
                    rowd['rideId'] = row.ride_id
                    rowd['Created_by'] = row.created_by
                    rowd['users']=((row.joined_users).split('$#'))[1:]
                    rowd['Timestamp'] = row.timestamp
                    rowd['source']=row.source
                    rowd['destination']=row.destination
                    response_all.append(rowd)
                response = {"Result" : response_all}

            if(Request['method']=='existence'):
                quer_res = db.session.query(Rides).filter_by(ride_id = Request['where'])
                if(quer_res.scalar() is None):
                    response = {"Exists": 0}
                else:
                    response = {"Exists": 1}

        if(Request['table']=='Users'):
            if(Request['method']=='existence'):
                quer_res = db.session.query(Users).filter_by(username = Request['where'])
                if(quer_res.scalar() is None):
                    response = {"Exists": 0}
                else:
                    response = {"Exists": 1}
        return response
    return {'status_code': 405}
if(__name__ == '__main__'):
    app.run()
