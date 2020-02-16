from flask import Flask, request
from flask_restful import Resource, Api, abort
from flask_sqlalchemy import SQLAlchemy
from requests import put,get,post,delete
from constants import AreaEnum
import datetime
import sqlalchemy
import re

app = Flask(__name__)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://ubuntu@localhost/rideshare' #connect to database rideshare
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def setupenv(db):
	db.engine.execute("drop table if exists UserRide,Ride,User;")
	user_query = "create table User(id integer not null auto_increment, username text not null, password char(40), userhash varchar(64) as (SHA2(username,256)) stored unique, primary key(id));"
	ride_query = "create table Ride(RideID INT AUTO_INCREMENT, CREATED_BY INT, TIMESTAMP datetime NOT NULL, SOURCE INT, DEST INT, PRIMARY KEY(RIDEID), FOREIGN KEY(CREATED_BY) REFERENCES User(id) on delete cascade);"
	user_ride_query = "create table UserRide(RideID INT, UserID INT, Primary KEY(RideID,UserID), FOREIGN KEY(RideId) REFERENCES Ride(RideID) on delete cascade, FOREIGN KEY(UserID) REFERENCES User(id) on delete cascade);"
	db.engine.execute(user_query)
	db.engine.execute(ride_query)
	db.engine.execute(user_ride_query)

#using enum: AreaEnum(locality_id).name

#reversing date and time to fit mysql format
def format_time(timestamp):
    try:
        timestamp = datetime.datetime.strptime(timestamp,'%d-%m-%Y:%S-%M-%H')
    except ValueError:
        return -1
    return timestamp.strftime('%Y-%m-%d %H-%M-%S')

class DatabaseRead(Resource):
    def post(self):
       table = request.json['table name']
       column = request.json['column name']
       if(type(column)==list):
           column = ','.join(column)
       where = request.json['where']
       query = "select "+column+" from "+table+" where "+where+";"
       result = db.engine.execute(query)
       res = []
       for row in result:
           res.append(dict(row))
       if(len(res)==0):
           return {},204
       for row in res:  #every row in result
           for key,value in row.items():  #every item in the dictionary
              if(type(value)==datetime.datetime):
                  row[key] = row[key].strftime('%d-%m-%Y:%S-%M-%H')
       return {"result":res}

class DatabaseWrite(Resource):
    def post(self):
        querytype = 'insert'
        try:
            values = request.json['insert']
            for i in range(len(values)):
                if(type(values[i])==int):
                    values[i] = "'" + str(values[i]) + "'"
                else:
                    values[i] = "'" + values[i] + "'"
            values = ','.join(values)
            column = request.json['column name']
            column = ','.join(column)
        except:
            querytype='delete'
            condition = request.json['condition']
        table = request.json['table name']
        if(querytype=='insert'):
            query = "insert into "+table+"("+column+") values("+values+");"
        else:
            query = "delete from "+table+" where "+condition+";"
        try:
            result = db.engine.execute(query)
            if(result.rowcount==0):
                abort(400)
        except sqlalchemy.exc.IntegrityError:
            abort(400)
        return {}

class User(Resource):
    def put(self):
        pat = "([0-9a-fA-F]){40}"
        try:
            username = request.json['username']
            if(username==''):
                abort(400)
            password = request.json['password']
        except TypeError:
            abort(500)
        if(len(password)!=40 or re.search(pat,password)==None): #check if valid password
           abort(400, message="Enter a password 40 characters long containing only hexadecimal characters")
        jsonwrite = {'insert':[username,password],'column name':['username','password'],'table name':'User'}
        x = post('http://localhost/api/v1/db/write',json=jsonwrite)
        if(not(x.ok)): #error
            abort(x.status_code)
        return {},201

    def delete(self,username):
        jsonwrite = {'table name':'User','condition':"username='"+username+"'"}
        x = post('http://localhost/api/v1/db/write',json=jsonwrite)
        if(not(x.ok)):
           abort(x.status_code)
        return {}

    def post(self):
       abort(405)

    def get(self):
        abort(405)

class Ride(Resource):
    def post(self):
        try:
            created_by = request.json['created_by']
            timestamp = request.json['timestamp']
            source = int(request.json['source'])
            dest = int(request.json['destination'])
        except TypeError:
            abort(400)
        if(source==dest):
            abort(400,message="Same Source and Destination")
        try:
            AreaEnum(source)  #checking if given source and dest exist
            AreaEnum(dest)
        except ValueError:
            abort(400,message="Invalid Source or Destination")
        timestamp = format_time(timestamp)
        if(timestamp==-1):
            abort(400,message="Bad Timestamp")
        jsonread = {"table name":"User","column name":"id","where":"username='"+created_by+"'"}
        result = post('http://localhost/api/v1/db/read',json=jsonread)
        if(result.status_code>200): #error -> either 400 or 204
           abort(400)  #if 204 is returned, then username does not exist, therefore 400
        resultjson = result.json()
        userid = str(resultjson['result'][0]['id'])
        jsonwrite = {'insert':[userid,timestamp,source,dest],'column name':['created_by','timestamp','source','dest'],'table name':'Ride'} #inserting into Ride
        x = post('http://localhost/api/v1/db/write',json=jsonwrite)
        if(not(x.ok)): #error
            abort(x.status_code)

        jsonread = {'table name':"Ride",'column name':'rideid','where':"created_by='"+userid+"' order by rideid desc"} #order by rideid desc, get latest ride
        result = post('http://localhost/api/v1/db/read',json=jsonread)
        resultjson = result.json()
        rideid = resultjson['result'][0]['rideid']
        jsonwrite = {'insert':[rideid,userid],'column name':['rideid','userid'],'table name':'UserRide'} #inserting into UserRide
        x = post('http://localhost/api/v1/db/write',json=jsonwrite)

        return {},201

    def get(self):
        source = request.args['source']
        destination = request.args['destination']
        if(source==destination):
            abort(400,message="Same Source and Destination")
        try:
            AreaEnum(int(source))  #checking if given source and dest exist
            AreaEnum(int(destination))
        except ValueError:
            abort(400,message="Invalid Source or Destination")
        jsonread = {"table name":"Ride","column name":["rideid","created_by","timestamp"],"where":"source="+source+" and dest="+destination+" and now() < timestamp"}
        result = post('http://localhost/api/v1/db/read',json=jsonread)
        if(result.status_code>200): #error -> either 400 or 204
            return {},result.status_code
        returnjson = []
        resultjson = result.json() #dictionary with key 'result' holding a list of dictionaries
        for row in resultjson['result']: #iterate over each list
            ride = {}
            for key,value in row.items(): #iterate over dictionary
                if(key=='created_by'): #call db read to get username of created_by
                    jsonread={'table name':'User',"column name":"username","where":"id="+str(value)}
                    x = post('http://localhost/api/v1/db/read',json=jsonread)
                    x = x.json()['result'][0]['username']
                    ride['username'] = x
                elif(key=='rideid'):
                    ride['rideId']=value
                else:
                    ride[key] = value
            returnjson.append(ride)
        return returnjson

    def delete(self):
        abort(405)

    def put(self):
        abort(405)

class RideDetails(Resource):
    def get(self,ride_id):
        jsonread = {"table name":"Ride","column name":["created_by","timestamp","source","dest"],"where":"RideID='"+ride_id+"'"}
        result = post('http://localhost/api/v1/db/read',json=jsonread)
        if(result.status_code>200):
             abort(400)
        resultjson = result.json()
        timestamp = resultjson['result'][0]['timestamp']
        source = resultjson['result'][0]['source']
        destination = resultjson['result'][0]['dest']
        userid = str(resultjson['result'][0]['created_by'])

        jsonread = {"table name":"UserRide","column name":"UserID","where":"RideID='"+ride_id+"'"}
        result_2 = post('http://localhost/api/v1/db/read',json=jsonread)
        if(result_2.status_code>200):
             abort(400)
        resultjson_2 = result_2.json()
        userid_list = []
        for row in resultjson_2['result']: #iterate over each list
            userid_list.append(str(row['UserID'])) #add all rider_ids to dictionary
        x = " or id=".join(userid_list)

        jsonread = {"table name":"User","column name":"username","where":"id="+x}
        result_3 = post('http://localhost/api/v1/db/read',json=jsonread)
        resultjson_3 = result_3.json()
        if(result_3.status_code>200):
             abort(400)
        resultjson_3 = result_3.json()
        username_list = []
        for row in resultjson_3['result']: #iterate over each list
            username_list.append(row['username']) #add all rider_ids to dictionary

        jsonread = {"table name":"User","column name":"username","where":"id="+userid}
        result_3 = post('http://localhost/api/v1/db/read',json=jsonread)
        resultjson_3 = result_3.json()
        if(result_3.status_code>200):
             abort(400)
        resultjson_3 = result_3.json()
        created_by = resultjson_3['result'][0]['username']
        username_list.remove(created_by)

        returnjson = {"rideId":ride_id,"created_by":created_by,"users":username_list,"timestamp":timestamp,"source":source,"destination":destination}
        return returnjson

    def post(self,ride_id):
        try:
            username = request.json['username']
        except TypeError:
            abort(400)
        jsonread = {"table name":"User","column name":"id","where":"username='"+username+"'"}
        result = post('http://localhost/api/v1/db/read',json=jsonread)
        if(result.status_code>200): #error -> either 400 or 204
           abort(400)  #if 204 is returned, then username does not exist, therefore 400
        resultjson = result.json()
        userid = str(resultjson['result'][0]['id'])

        jsonwrite = {'insert':[ride_id,userid],'column name':['rideid','userid'],'table name':'UserRide'} #inserting into UserRide
        x = post('http://localhost/api/v1/db/write',json=jsonwrite)
        if(not(x.ok)):
            abort(x.status_code)
        return {}

    def delete(self,ride_id):
        jsonwrite = {'table name':'Ride','condition':"RideID='"+ride_id+"'"}
        result = post('http://localhost/api/v1/db/write',json=jsonwrite)
        if(not(result.ok)):
            abort(result.status_code)
        return {}

    def put(self,ride_id):
        abort(405)

api.add_resource(DatabaseRead, '/api/v1/db/read')
api.add_resource(DatabaseWrite, '/api/v1/db/write')
api.add_resource(User,'/api/v1/users','/api/v1/users/<string:username>')
api.add_resource(Ride,'/api/v1/rides')
api.add_resource(RideDetails,'/api/v1/rides/<string:ride_id>')

if __name__ == "__main__":
    setupenv(db)
    app.run(host='0.0.0.0',debug=True)
