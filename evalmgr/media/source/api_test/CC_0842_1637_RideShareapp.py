import json
from flask import Flask
from flask_pymongo import PyMongo
from flask_restful import Resource, Api
from flask import request,jsonify
import os
from werkzeug.security import generate_password_hash,check_password_hash
import datetime
import csv
from webfunctions import ProcessData
import requests
from logging import FileHandler,WARNING


app = Flask(__name__)
app.secret_key="secretkey"
app.config['ENV']='development'
app.config['DEBUG']=True
app.config['TESTING']=True
app.config['MONGO_URI'] = 'mongodb://prakruthi:pakku123@cluster0-shard-00-00-lh5wa.mongodb.net:27017,cluster0-shard-00-01-lh5wa.mongodb.net:27017,cluster0-shard-00-02-lh5wa.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority'
api=Api(app)
mongo = PyMongo(app)

file_handler = FileHandler('errorlog.txt')
file_handler.setLevel(WARNING)
app.logger.addHandler(file_handler)


#Ride Sharing APP

# class JSONEncoder(json.JSONEncoder):
#     def default(self, o):
#         if isinstance(o, ObjectId):
#             return str(o)
#         return json.JSONEncoder.default(self, o)

class User(Resource):
#Add user
    def put(self):
        _json = request.json
        user =_json['user']
        _password=_json['password']

        myquery = { 'user': user }
        users=[]
        for doc in mongo.db.users.find(myquery):
        # append each document's ID to the list
            users.append([doc['_id']])
        print('users are ',users);

        if(len(users)==0):
            if user and _password and request.method =='PUT':
               _hashed_password = generate_password_hash(_password)
               id = mongo.db.users.insert({'user':user,'password':_hashed_password})
               resp = jsonify("User added successfully")
               resp.status_code=201
               return resp
            else:
               message ={
               'status':400,
               'message':'User addition not possible'
                }
               resp = jsonify(message)
               resp.status_code=400
               return resp
        else:
            message ={
            'status':400,
            'message':'User already exists'
             }
            resp = jsonify(message)
            resp.status_code=400
            return resp
#Delete user   
    def delete(self , name):
        myquery = { 'user':name }
        user=''
        
        for doc in mongo.db.users.find(myquery):
        # append each document's ID to the list
            user = [doc['_id']]

        if (len(user) >0):
            result = mongo.db.users.delete_one(myquery)
            print('result value is ' , result)
            message ={
            'status':201,
            'message':'User deleted successfully'
            }


            resp = jsonify(message)
            resp.status_code=201
            return resp
        else:
            message ={
            'status':400,
            'message':'User doesnt exist'
            }
            resp = jsonify(message)
            resp.status_code=400
            return resp        


#get all the user details
    def get(self):
        # append each document's ID to the list    
        documents = mongo.db.users.find()
        response = []

        for document in documents:
           document['_id'] = str(document['_id'])
           response.append(document)

        if(len(response)==0):
             message ={
            'status':204,
            'message':'No Users are present'
             }
             resp = jsonify(message)
             resp.status_code=204
             return resp
        else:
            outputDoc = []
            for document in response:
                    docID = document['_id']
                    docName = document['user']
                    outputDoc.append({'userID':docID,'UserName':docName},)
            return outputDoc
             


class CreateRide(Resource):
#creating a ride using post method    
    def post(self):
        _json = request.json
        user =_json['created_by']
        source = _json['source']
        destination=_json['destination']
        RideID_Date = _json['timestamp']

        date_format="%d-%m-%Y:%S-%M-%H"
        print('here')

        isValidDate=True
        try:
            date_obj =datetime.datetime.strptime(RideID_Date, date_format)
            print(date_obj)
        except ValueError:
            isValidDate=False
        
        riderIDUniq=1
        if(isValidDate):
            for rideIDData in mongo.db.Rides.find({}, {'rideID':1, '_id':0}):

                if(rideIDData['rideID'] >= riderIDUniq):
                    riderIDUniq = rideIDData['rideID']+1

            print('RideID_Date',RideID_Date)
            

            myquery = { 'user':user }
            userid=''
            for doc in mongo.db.users.find(myquery):
                userid = [doc['_id']]
            print('user id is ',userid)
            if (len(userid) >0):
                _id=mongo.db.Rides.insert_one({'username':user,'datetime':RideID_Date,'source':source,'destination':destination,'commuters':user,'rideID':riderIDUniq})
                resp = jsonify("Ride added successfully")
                resp.status_code=201
                return resp
            else:
                message ={
                'status':400,
                'message':'User doesnt exist , so cannot create a ride'
                }
                resp = jsonify(message)
                resp.status_code=400
                return resp
        else:
            resp = jsonify("Invalid Date Format")
            resp.status_code=400
            return resp


#displaying ride details for a specific source and destination specified in the URL query strings
    def get(self):
        arg1 = request.args['source']
        arg2 = request.args['destination']
        rideresponse = []
        
        if(len(arg1)==0 or len(arg2)==0):
            message ={
            'status':400,
            'message':'both source and destination must have a value for ride details to be displayed'
            }
            resp = jsonify(message)
            resp.status_code=400
            return resp
        else:
            with open('static/AreaNameEnum.csv', mode='r') as infile:
                reader = csv.reader(infile)
                with open('static/AreaNameEnum_new.csv', mode='w') as outfile:
                    writer = csv.writer(outfile)
                    mydict = {rows[0]:rows[1] for rows in reader}

            current_source = mydict[arg1]
            current_destination = mydict[arg2]

            print('source is ', current_source)
            print('destination is ', current_destination)

            myquery = { 'source':current_source,'destination':current_destination }
            documents = mongo.db.Rides.find(myquery)
            for document in documents:
                now = datetime.datetime.now()
                datetime_current = now.strftime("%d-%m-%Y:%S-%M-%H")
                if(document['datetime']>datetime_current):
                    document['_id'] = str(document['_id'])
                    rideresponse.append(document)

        print('response is ', rideresponse)
        if(len(rideresponse)==0):
            message ={
            'status':204,
            'message':'No Upcoming Rides found for the given source and destination'
            }
            resp = jsonify(message)
            resp.status_code=204
            return resp
        else:
            outputDoc = []
            for document in rideresponse:
                    docID = document['_id']
                    docName = document['username']
                    docTime = document['datetime']
                    docRideID = document['rideID']
                    outputDoc.append({'rideID':docRideID,'UserName':docName,'TimeStamp':docTime},)
            return outputDoc


   

class ModifyRide(Resource):
    def get(self,rideid):
        myquery = {'rideID':rideid}
        tempRide=''
        response=[]

        for doc in mongo.db.Rides.find(myquery):
            tempRide = [doc['_id']]
            response.append(doc)
        print('output',tempRide)
        if (len(tempRide) >0):
            outputDoc = []
            for eachRide in response:
                    RidecreatedName = eachRide['username']
                    Rideusers=eachRide['commuters']
                    rideTimestamp=eachRide['datetime']
                    rideSource=eachRide['source']
                    rideDestination=eachRide['destination']
                    rideID = eachRide['rideID']
                    outputDoc.append({'rideID':rideID,'created_By':RidecreatedName ,'Users':Rideusers,'TimeStamp':rideTimestamp,'Source':rideSource,'Destination':rideDestination},)
            return outputDoc
        else:
            message ={
            'status':400,
            'message':'Ride doesnt exist'
            }
            resp = jsonify(message)
            resp.status_code=400
            return resp

    def post(self,rideid):
        ridequery = {'rideID':rideid}
        tempRide=''
        response=[]

        _json = request.json
        user =_json['username']

        userquery = { 'user':user }
        userid=''
        for doc in mongo.db.users.find(userquery):
            userid = [doc['_id']]
       

        for doc in mongo.db.Rides.find(ridequery):
            tempRide = [doc['_id']]
            response.append(doc)

        if (len(userid) >0):
            if(len(tempRide)>0):
                users = user
                for eachride in response:
                    users = users+ ',' +eachride['commuters']
                    print('commuters new field',users)
                    mongo.db.Rides.update({'rideID':rideid},
                        {'$set': {'commuters': users}})
                resp = jsonify('Ride updated successfully!')
                resp.status_code = 201
                return resp
            else:
                message ={
                'status':400,
                'message':'Ride doesnt exist'
                }
                resp = jsonify(message)
                resp.status_code=400
                return resp
        else:
            message ={
            'status':400,
            'message':'cannot update the Ride , invalid user'
            }
            resp = jsonify(message)
            resp.status_code=400
            return resp


    def delete(self,rideid):
        myquery = {'rideID':rideid}
        currentRide=''

        for doc in mongo.db.Rides.find(myquery):
            currentRide = [doc['_id']]
        
        if (len(currentRide) >0):
            result = mongo.db.Rides.delete_one(myquery)
            print('result value is ' , result)
            message ={
            'status':201,
            'message':'Ride deleted successfully'
            }
            resp = jsonify(message)
            resp.status_code=201
            return resp
        else:
            message ={
            'status':400,
            'message':'Ride doesnt exist'
            }
            resp = jsonify(message)
            resp.status_code=400
            return resp


class DBRead(Resource):
    def post(self):
        _json = request.json
        table_Name =_json['table']
        Columns = _json['columns']
        where_Clause =_json['where']

        query_statment='mongo.db.'+table_Name+'.find({\''+Columns+'\':\''+where_Clause+'\'''})'
        documents = eval(query_statment)
        response = []

        for document in documents:
           document['_id'] = str(document['_id'])
           response.append(document)

        if(len(response)==0):
             message ={
            'status':204,
            'message':'No records found in the DB '
             }
             resp = jsonify(message)
             resp.status_code=204
             return resp
        else:
             return json.dumps(response ,sort_keys=True, indent=2)


class DBWrite(Resource):
    def post(self):
        _json = request.json
        table_Name =_json['table']
        operation_type =_json['typeofoperation']
        Columns = _json['column']
        insert_data =_json['insertdata']


        if(operation_type=='insert'):
            insert_query1 = ProcessData(insert_data)
            print('insert query is',insert_query1)
            query_statment='mongo.db.'+table_Name+'.'+operation_type+'('+insert_query1+')'
            print('query statment is ',query_statment)
            eval(query_statment)
            resp = jsonify("Record inserted successfully")
            resp.status_code=201
            return resp
        
        if(operation_type=='update'):
            update_clause=ProcessData(Columns)
            update_statment='mongo.db.'+table_Name+'.'+operation_type+'('+update_clause+',{'+'\'$set''\''+':'+ProcessData(insert_data)+'})'
            print('update statment is',update_statment)
            eval(update_statment)
            resp = jsonify("Record is updated successfully")
            resp.status_code=201
            return resp

        if(operation_type=='delete'):
            delete_clause=ProcessData(Columns)
            delete_statement='mongo.db.'+table_Name+'.remove('+delete_clause+')'
            print('delete statment is',delete_statement)
            eval(delete_statement)
            resp = jsonify("Record is deleted successfully")
            resp.status_code=201
            return resp         
        
        
#routing info

api.add_resource(User,'/api/v1/users','/api/v1/users/<string:name>','/api/v1/users/display')
api.add_resource(CreateRide,'/api/v1/rides',)
api.add_resource(ModifyRide,'/api/v1/rides/<int:rideid>')
api.add_resource(DBRead,'/api/v1/db/read')
api.add_resource(DBWrite,'/api/v1/db/write')


if __name__ == '__main__':
    app.run(debug=True)