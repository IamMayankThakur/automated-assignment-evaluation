from flask import Flask, render_template,jsonify,request,abort
import requests
from sqlalchemy import create_engine
import sqlalchemy
import re
import pandas as pd

app=Flask(__name__)

# database creation --- database name = assignment1.db, tables = users, rides
engine = create_engine("sqlite:///assignment1.db")
try:
    sql_command1 = "create table users (username text primary key, password text);"
    sql_command2 = "create table rides (rideid integer primary key autoincrement, created_by text, timestamp text, source text, destination text, users text, constraint fk_users foreign key (created_by) references users(username) on delete cascade);"
    with engine.connect() as con:
        con.execute(sql_command1)
        con.execute(sql_command2)
        con.execute("PRAGMA foreign_keys=on;")
except:
    pass
df = pd.read_csv("AreaNameEnum.csv")
l = list(df.itertuples(index=False, name=None))
area_list = {i[0]:i[1] for i in l}

@app.route("/api/test",methods=["GET"])
def test():
    return "Hello stranger!"

# api 1 --- adding a new unique user to the database
@app.route("/api/v1/users",methods=["PUT"])
def add_user():
    if request.method == 'PUT':
        req = request.get_json()
        if ("username" in req) and ("password" in req):
            username = req["username"]
            password = req["password"]
            # send request to api 9 to query database to check if username is present
            column_names="username"; table_names="users"; where_condition="exists (select * from users where username='"+username+"')"
            sql_query = {"column_names":column_names,"table_names":table_names,"where_condition":where_condition}
            response = requests.post(url="http://52.70.183.172/api/v1/db/read",json=sql_query).json()["row_list"]
            if len(response)==0: # if not present add user and send 201 (resource created)
                if (re.match("[a-fA-F0-9]{40}",password)) and (len(password)==40): # checking if password is 40 char hex hash
                    # adding user by sending request to api 8
                    sql_query={"method":"insert", "table_names":"users", "column_names":"username,password", "values_list": "'"+username+"'"+","+"'"+password+"'"}
                    response = requests.post(url="http://52.70.183.172/api/v1/db/write",json=sql_query)
                    return "",201
    else: # if request method is not "PUT", we send 405 (method not allowed)
        return "",405
    return "",400 # if password not compliant, user already exists, or any of required request parameters not present send 400 (bad request)
# decide if we need to check for request methods "GET" and "HEAD" and change the response code for it

# api 2 --- deleting an existing user from the database
@app.route('/api/v1/users/<username>' , methods = ['DELETE'])
def delete_user(username):
    if request.method == 'DELETE':
        # send request to api 9 to query database to check if username is present
        column_names="username"; table_names="users"; where_condition="exists (select * from users where username='"+username+"')"
        sql_query = {"column_names":column_names,"table_names":table_names,"where_condition":where_condition}
        response = requests.post(url="http://52.70.183.172/api/v1/db/read",json=sql_query).json()["row_list"]
        if len(response)==0: # if not present return 400 (bad request) as delete not possible
            return "",400 
        else: # else send request to api 8 to delete and return 200 (success)
            sql_query = {"method":"delete","table_names":"users","where_condition":"username='"+username+"'"}
            response = requests.post(url="http://52.70.183.172/api/v1/db/write",json=sql_query)
            sql_query = {"column_names":"rideid,users","table_names":"rides","where_condition":"1"}
            response = requests.post(url="http://52.70.183.172/api/v1/db/read",json=sql_query).json()["row_list"]
            if len(response)!=0:
                for i in response:
                    if i[1] is not None:
                        users = i[1].split(",")
                        rideid=str(i[0])
                        if username in users:
                            users.remove(username)
                            if len(users)==1:
                                pass
                            else:
                                res = ""
                                for x in users:
                                    res = res+x+","
                                users=res[:len(res)-1]
                            sql_query = {"method":"update","table_names":"rides","set_values":"users='"+users+"'","where_condition":"rideid="+rideid}
                            response = requests.post(url="http://52.70.183.172/api/v1/db/write", json=sql_query)
            return "",200
    else: # if request method is not "DELETE", we send 405 (method not allowed)
        return "",405

# api 3 --- creating a ride for the user
# api 4 --- list all rides between given source and destination
@app.route('/api/v1/rides' , methods = ["POST","GET"])
def create_ride():
    if request.method == 'POST':
        req=request.get_json()
        if ("created_by" in req) and ("timestamp" in req) and ("source" in req) and ("destination" in req):
            username=req["created_by"]
            timestamp=req["timestamp"]
            source=req["source"]
            destination=req["destination"]
            sql_query = {"column_names":"username","table_names":"users","where_condition":"exists (select * from users where username='"+username+"')"}
            response = requests.post(url="http://52.70.183.172/api/v1/db/read",json=sql_query).json()["row_list"]
            if len(response)!=0: # if user exists, we attempt to create a ride for user
                if (source in area_list) and (destination in area_list) and (re.match(r"([0-2][0-9]|[3][0-1])\-([0][0-9]|[1][0-2])\-([0-9]{4}:[0-5][0-9])\-([0-5][0-9])\-([0-1][0-9]|[2][0-3])",timestamp)): 
                    # if valid source destination and timestamp, create ride and return 201 (resource created)
                    sql_query = {"method":"insert","table_names":"rides","column_names":"created_by,timestamp,source,destination", "values_list":"'"+username+"'"+','+"'"+timestamp+"'"+','+"'"+str(source)+"'"+','+"'"+str(destination)+"'"}
                    response = requests.post(url="http://52.70.183.172/api/v1/db/write",json=sql_query)
                    return "",201
    elif request.method == 'GET':
        try:
            source=int(request.args.get("source"))
            destination=int(request.args.get("destination"))
        except:
            return "",400
        if (source in area_list) and (destination in area_list) and (source!=destination):
            sql_query = {"column_names":"*","table_names":"rides","where_condition":"source='"+str(source)+"' and destination='"+str(destination)+"'"}
            response = requests.post(url="http://52.70.183.172/api/v1/db/read", json=sql_query).json()["row_list"]
            if len(response)==0: # if there are no rides from source to destination we respond with 204 (success,no content)
                return "",204 
            else: # if there are rides from source to destination we respond with 200 (success) and all the rides as response
                result = []
                for i in response:
                    result.append({"rideId":i[0],"username":i[1],"timestamp":i[2]})
                return jsonify(result),200
    else: # if request method is not POST, we send 405 (method not allowed)
        return "",405
    return "",400 # if username does not exist or any of the required request parameters are missing, we send 400 (bad request)

# api 5 --- display all the details of given ride id
# api 6 --- add users to an existing ride with id = ride id
# api 7 --- delete a ride given the ride id
@app.route('/api/v1/rides/<rideId>' , methods=["GET","POST","DELETE"])
def ride_details_update_cancel(rideId):
    if request.method == "GET": # if method is get we display ride details corresponding to the ride id if it exists
        sql_query = {"column_names":"rideid","table_names":"rides","where_condition":"exists (select * from rides where rideid="+rideId+")"}
        response = requests.post(url="http://52.70.183.172/api/v1/db/read", json=sql_query).json()["row_list"]
        if len(response)==0: # if not present return 400 (bad request)
            return "",400
        else: # query the ride details using api 8 then send the results and 200 (success)
            sql_query = {"column_names":"*","table_names":"rides","where_condition":"rideid="+rideId}
            response = requests.post(url="http://52.70.183.172/api/v1/db/read", json=sql_query).json()["row_list"][0]
            if response[5] is not None:
                result = {"rideId" :response[0], "Created_by":response[1], "users":"["+str(response[5])+"]", "Timestamp":response[2], "source":response[3],"destination":response[4]}
            else:
                result = {"rideId" :response[0], "Created_by":response[1], "users":"[]", "Timestamp":response[2], "source":response[3],"destination":response[4]}
            return jsonify(result),200 
    elif request.method == "POST":
        sql_query = {"column_names":"rideid","table_names":"rides","where_condition":"exists (select * from rides where rideid="+rideId+")"}
        response = requests.post(url="http://52.70.183.172/api/v1/db/read", json=sql_query).json()["row_list"]
        if len(response)==0: # if rideid not present return 400 (bad request)
            return "",400
        else:
            req = request.get_json()
            if "username" in req:
                username=req["username"]
                # send request to api 9 to query database to check if username is present
                column_names="username"; table_names="users"; where_condition="exists (select * from users where username='"+username+"')"
                sql_query = {"column_names":column_names,"table_names":table_names,"where_condition":where_condition}
                response = requests.post(url="http://52.70.183.172/api/v1/db/read",json=sql_query).json()["row_list"]
                if len(response)==0: # if username not present send 400 (bad request)
                    return "",400
                else:
                    sql_query = {"column_names":"*","table_names":"rides","where_condition":"rideid="+rideId}
                    response = requests.post(url="http://52.70.183.172/api/v1/db/read", json=sql_query).json()["row_list"][0]
                    users = response[5] ; created_by = response[1]
                    if ((users is not None) and (username in users.split(","))) or (username == created_by):
                        return "",400 # send 400 (bad request) as user is already in the ride
                    if (users is None):
                        sql_query = {"method":"update","table_names":"rides","set_values":"users='"+username+"'","where_condition":"rideid="+rideId}
                    else:
                        sql_query = {"method":"update","table_names":"rides","set_values":"users='"+users+","+username+"'","where_condition":"rideid="+rideId}
                    response = requests.post(url="http://52.70.183.172/api/v1/db/write", json=sql_query)
                    return "",200 #return 200 as we successfully send write request to api 8 to update the ride
            else:
                return "",400 # return 400 (bad request) because required parameters not present in request body
    elif request.method == "DELETE": 
        # send request to api 9 to query database to check if rideid is present
        sql_query = {"column_names":"rideid","table_names":"rides","where_condition":"exists (select * from rides where rideid="+rideId+")"}
        response = requests.post(url="http://52.70.183.172/api/v1/db/read", json=sql_query).json()["row_list"]
        if len(response)==0: # if not present return 400 (bad request) as delete not possible
            return "",400
        else: # else send request to api 8 to delete and return 200 (success)
            sql_query = {"method":"delete","table_names":"rides","where_condition":"rideid="+rideId}
            response = requests.post(url="http://52.70.183.172/api/v1/db/write",json=sql_query)
            return "",200
    else: # if request method is not "DELETE", we send 405 (method not allowed)
        return "",405

# ​api 8 --- writing to database
@app.route("/api/v1/db/write",methods=["POST"])
def dbwrite():
    if request.method == 'POST':
        req = request.get_json()
        if "method" in req:
            method = req["method"]
            if method == "insert": # if method is insert and all required parameters present, insert and return 200 (success)
                if ("table_names" in req) and ("column_names" in req) and ("values_list" in req):
                    sql_command = "insert into "+req["table_names"]+" ("+req["column_names"]+") values ("+req["values_list"]+");"
                    with engine.connect() as con:
                        con.execute(sql_command)
                    return "",200
            elif method == "delete": # if method is delete and all required parameters present, delete and return 200 (success)
                if ("table_names" in req) and ("where_condition" in req):
                    sql_command = "delete from "+req["table_names"]+" where "+req["where_condition"]+";"
                    with engine.connect() as con:
                        con.execute("PRAGMA foreign_keys=on;")
                        con.execute(sql_command)
                    return "",200
            elif method == "update": # if method is update and all required parameters present, update and return 200 (success)
                if ("table_names" in req) and ("where_condition" in req) and ("set_values" in req):
                    sql_command = "update "+req["table_names"]+" set "+req["set_values"]+" where "+req["where_condition"]+";"
                    with engine.connect() as con:
                        con.execute(sql_command)
                    return "",200
    else: # if request method is not POST, we send 405 (method not allowed)
        return "",405 
    return "",400 # if any of the required request parameters are missing, we send 400 (bad request)

# api 9 --- reading from database
@app.route("/api/v1/db/read", methods=["POST"])
def dbread():
    if request.method == 'POST':
        req = request.get_json()
        y=[]
        if ("column_names" in req) and ("table_names" in req) and ("where_condition" in req): 
            # execute the required read, and return results as response along with 200 (success)
            sql_command = "select "+req["column_names"]+" from "+req["table_names"]+" where "+req["where_condition"]+";"
            with engine.connect() as con:
                x = con.execute(sql_command)
                for ln in x:
                    y.append(list(ln))
            return jsonify({"row_list":y}),200
    else: # if request method is not POST, we send 405 (method not allowed)
        return jsonify("hello"),405
    return jsonify("hello"),400 # if any of the required request parameters are missing, we send 400 (bad request)

if __name__ == '__main__':
    app.debug = True
    app.run()
