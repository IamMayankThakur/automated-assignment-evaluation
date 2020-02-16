from flask import Flask, render_template, jsonify, request, abort
import flask
import mysql.connector
import string
import csv
import pandas as pd
import json
import requests
import ast
import datetime

app = Flask(__name__)

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="Sarang99!",
    auth_plugin='mysql_native_password'
)
mycursor = mydb.cursor(buffered=True)
mycursor.execute("DROP DATABASE IF EXISTS a1")
mycursor.execute("CREATE DATABASE a1")
mycursor.execute("USE a1")
mycursor.execute("CREATE TABLE users (uname VARCHAR(255),pswd VARCHAR(40))")
mycursor.execute(
    "CREATE TABLE rides (ride_ID INT AUTO_INCREMENT,created_by VARCHAR(255),uname VARCHAR(255),timestamp VARCHAR(255),source INT,dest INT,PRIMARY KEY(ride_ID,uname))")
locations = []
df = pd.read_csv('area.csv')
# print("read csv")

# ------------------------------------------------1--------------------------------------------------
@app.route("/api/v1/users", methods=["PUT"])
def addUser():
    uname = request.get_json()["username"]
    pswd = request.get_json()["password"]
    users = []
    obj = {
        "columns": "uname,pswd",
        "where": "uname='"+uname+"'",
        "table": "users"
    }
    obj = json.dumps(obj)  # stringified json
    obj = json.loads(obj)  # content-type:application/json
    # send request to db api
    x = requests.post("http://127.0.0.1:5000/api/v1/db/read", json=obj)
    print(x.text)
    # Parse the text response (mycursor.fetchall() list) from read api to list
    users = ast.literal_eval(x.text)
    if(len(users) != 0):
        return abort(400)
    else:
        pswd = pswd.lower()
        if(len(pswd) != 40 or not all(c in string.hexdigits for c in pswd)):
            return abort(405)
        # JSONify request object so db api can understand
        obj = {
            "operation": "insert",
            "column": "(uname,pswd)",
            "insert": "['"+uname+"','"+pswd+"']",
            "table": "users"
        }
        obj = json.dumps(obj)  # stringified json
        obj = json.loads(obj)  # content-type:application/json
        # send request to db api
        x = requests.post("http://127.0.0.1:5000/api/v1/db/write", json=obj)
        return (jsonify({}), 201)


# ------------------------------------------------2--------------------------------------------------
@app.route("/api/v1/users/<username>", methods=["DELETE"])
def delUser(username):

    users = []

    obj = {
        "columns": "uname,pswd",
        "where": "uname='"+username+"'",
        "table": "users"
    }
    obj = json.dumps(obj)  # stringified json
    obj = json.loads(obj)  # content-type:application/json
    # send request to db api
    x = requests.post("http://127.0.0.1:5000/api/v1/db/read", json=obj)
    print(x.text)
    # Parse the text response (mycursor.fetchall() list) from read api to list
    users = ast.literal_eval(x.text)

    if(len(users) == 0):
        return abort(400)
    else:
        obj = {
            "operation": "delete",
            "column": "uname",
            "insert": "'"+username+"'",
            "table": "users"
        }
        obj = json.dumps(obj)  # stringified json
        obj = json.loads(obj)  # content-type:application/json
        # send request to db api
        x = requests.post("http://127.0.0.1:5000/api/v1/db/write", json=obj)
        mydb.commit()
        return ("{}", 200)


# ----------------------------------------------------3--------------------------------------------
@app.route("/api/v1/rides", methods=["POST"])
def addRide():
    print("API#3")
    uname = request.get_json()["created_by"]
    time = request.get_json()["timestamp"]
    source = request.get_json()["source"]
    dest = request.get_json()["destination"]
    if source == dest:
        return abort(405)
    if int(source) in df['Area No'] and int(dest) in df['Area No']:
        users = []

        obj = {
            "columns": "uname",
            "where": "uname='"+uname+"'",
            "table": "users"
        }
        obj = json.dumps(obj)  # stringified json
        obj = json.loads(obj)  # content-type:application/json
        # send request to db api
        x = requests.post("http://127.0.0.1:5000/api/v1/db/read", json=obj)
        # print(x.text)
        # Parse the text response (mycursor.fetchall() list) from read api to list
        users = ast.literal_eval(x.text)
        # users = []
        # query = "SELECT uname FROM users WHERE uname ='"+uname+"'"
        # mycursor.execute(query)
        # users = mycursor.fetchall()
        if(len(users) == 0):
            return abort(400)
        else:
            obj = {
                "operation": "insert",
                "column": "(created_by,uname,timestamp,source,dest)",
                "insert": "('"+uname+"','"+uname+"','"+time+"',"+source+","+dest+")",
                "table": "rides"
            }
            obj = json.dumps(obj)  # stringified json
            obj = json.loads(obj)  # content-type:application/json
            # send request to db api
            x = requests.post(
                "http://127.0.0.1:5000/api/v1/db/write", json=obj)
            mydb.commit()
            return ("{}", 201)
    else:
        return abort(400)


# -------------------------------------------4-------------------------------------------------------
@app.route("/api/v1/rides", methods=["GET"])
def upcRides():
    print("API#4")
    source = flask.request.args.get('source')
    destination = flask.request.args.get('destination')
    time = 
    print(source, destination, type(destination))
    if(int(source) in df['Area No'] and int(destination) in df['Area No']):
        obj = {
            "columns": "ride_ID,created_by,timestamp,source,dest",
            "where": "source="+source+",dest="+destination,
            "table": "rides"
        }
        obj = json.dumps(obj)  # stringified json
        obj = json.loads(obj)  # content-type:application/json
        # send request to db api
        x = requests.post("http://127.0.0.1:5000/api/v1/db/read", json=obj)
        print(x.text)
        # return(x.text)
        # print(x.text)
        rideDetails = ast.literal_eval(x.text)
        res=[]
        for ride in rideDetails:
            date_time_obj = datetime.datetime.strptime(ride[2], '%D-%m-%Y %H:%M:%S.%f')
            if(date_time_obj<datetime.datetime.now()):
                continue
            obj = {
                "columns": "uname",
                "where": "uname= '"+ride[1]+"'",
                "table": "users"
            }
            # query = 'SELECT uname FROM users WHERE uname="'+ride[1]+'"'
            obj = json.dumps(obj)  # stringified json
            obj = json.loads(obj)
            x = requests.post("http://127.0.0.1:5000/api/v1/db/read", json=obj)
            users = ast.literal_eval(x.text)
            if(len(users) == 0):
                return abort(400)
            r = {
                "rideId":ride[0],
                "username": ride[1],
                "timestamp":ride[2]
            }
            #ride = json.dumps(r)
            #ride = json.loads(ride)
            res.append(r)  
        return (jsonify(res), 200)
    return abort(405)

# ---------------------------------------------------5---------------------------------------------------
# Get ride details given the rideID
@app.route("/api/v1/rides/<rideId>", methods=["GET"])
def rideDetails(rideId):
    obj = {
        "columns": "ride_ID,created_by,uname,timestamp,source,dest",
        "where": "ride_ID = "+rideId,
        "table": "rides"
    }
    obj = json.dumps(obj)  # stringified json
    obj = json.loads(obj)
    x = requests.post("http://127.0.0.1:5000/api/v1/db/read", json=obj)
    rideDetails = ast.literal_eval(x.text)
    # query = "SELECT * FROM rides WHERE ride_ID='"+rideId+"'"
    # mycursor.execute(query)
    # rideDetails = mycursor.fetchall()
    if(len(rideDetails) == 0):
        return abort(400)
    res=[]
    for ride in rideDetails:
        res.append(ride[2])
    ride = {
        "ride_Id":rideDetails[0][0],
        "created_by": rideDetails[0][1],
        "users": res,
        "timestamp":rideDetails[0][3],
        "source": rideDetails[0][4],
        "destination":rideDetails[0][5]
    }
    ride = json.dumps(ride)
    ride = json.loads(ride)
    return (str(ride), 200)

# ---------------------------------------------------6---------------------------------------------------
# Join rides
@app.route("/api/v1/rides/<rideId>", methods=["POST"])
def joinRide(rideId):
    uname = request.get_json()["username"]
    obj = {
        "columns": "uname",
        "where": "uname= '"+uname+"'",
        "table": "users"
    }
    # query = 'SELECT uname FROM users WHERE uname="'+ride[1]+'"'
    obj = json.dumps(obj)  # stringified json
    obj = json.loads(obj)
    x = requests.post("http://127.0.0.1:5000/api/v1/db/read", json=obj)
    users = ast.literal_eval(x.text)

    # query = "SELECT uname FROM users WHERE uname ='"+uname+"'"
    # mycursor.execute(query)
    # users = mycursor.fetchall()
    if(len(users) == 0):
        return abort(400)

    obj = {
        "columns": "uname,timestamp,source,dest",
        "where": "ride_ID= "+rideId,
        "table": "rides",
        "distinct": 1
    }
    obj = json.dumps(obj)  # stringified json
    obj = json.loads(obj)
    x = requests.post("http://127.0.0.1:5000/api/v1/db/read", json=obj)
    users1 = ast.literal_eval(x.text)
    # q1 = "SELECT * FROM rides WHERE ride_ID ='"+rideId+"'"
    # mycursor.execute(q1)
    # users1 = mycursor.fetchall()
    if(len(users1) == 0):
        return abort(405)
    users1 = users1[0]
    # print("-------------\n", users1, len(users1))
    obj = {
        "operation": "insert",
        "column": "(ride_ID,created_by,uname,timestamp,source,dest)",
        "insert": "("+str(rideId)+",'"+users1[0]+"','"+uname+"','"+str(users1[1])+"',"+str(users1[2])+","+str(users1[3])+")",
        "table": "rides"
    }
    obj = json.dumps(obj)  # stringified json
    obj = json.loads(obj)  # content-type:application/json
    # send request to db api
    x = requests.post("http://127.0.0.1:5000/api/v1/db/write", json=obj)
    mydb.commit()
    # sql = "INSERT INTO rides(ride_ID,uname,timestamp,source,dest) VALUES ('" + str(
    #     users1[0])+"','" + uname+"','"+users1[2]+"','"+str(users1[3])+"','"+str(users1[4])+"')"
    # mycursor.execute(sql)
    return ("{}", 200)

# ----------------------------------------------------7----------------------------------------------
# Delete by rideId
@app.route("/api/v1/rides/<rideId>", methods=["DELETE"])
def delRide(rideId):
    obj = {
        "columns": "uname,timestamp,source,dest",
        "where": "ride_ID= "+str(rideId),
        "table": "rides"
    }
    obj = json.dumps(obj)  # stringified json
    obj = json.loads(obj)
    x = requests.post("http://127.0.0.1:5000/api/v1/db/read", json=obj)
    users = ast.literal_eval(x.text)
    # query = 'SELECT rideId FROM rides WHERE ride_ID ="'+rideId+'"'
    # # val = (username)
    # mycursor.execute(query)
    # users = mycursor.fetchall()
    print(users)
    if(len(users) == 0):
        return abort(405)
    else:
        obj = {
            "operation": "delete",
            "column": "ride_ID",
            "insert": rideId,
            "table": "rides"
        }
        obj = json.dumps(obj)  # stringified json
        obj = json.loads(obj)  # content-type:application/json
        # send request to db api
        x = requests.post("http://127.0.0.1:5000/api/v1/db/write", json=obj)
        mydb.commit()
        # query = 'DELETE FROM rides WHERE ride_ID="'+rideId+'"'
        # # val = (username)
        # mycursor.execute(query)
        # mydb.commit()
        return ("{}", 200)


# -------------------------------------------------8-------------------------------------------------
# Write into a DB
@app.route("/api/v1/db/write", methods=["POST"])
def insert():
    op = request.get_json()["operation"]
    column = request.get_json()["column"]
    insert = request.get_json()["insert"]
    table = request.get_json()["table"]
    query = ''
    if(op == "insert"):
        query += 'INSERT INTO ' + table+' '+column+' VALUES ('
        insert = insert[1:len(insert)-1]
        insert = insert.split(",")
        # insert = list(map(lambda x:str(x),insert))
        for i in range(len(insert)):
            if(i != 0):
                query += ","
            query += insert[i]
        query += ")"

    else:
        query += 'DELETE FROM '+table+' WHERE ('
        column = column.split(",")
        insert = insert.split(",")
        if(len(column) != len(insert)):
            abort(400)
        for i in range(len(column)):
            if(i != 0):
                query += 'AND'
            query += column[i]+'='+insert[i]
        query += ")"
    print(query)
    mycursor.execute(query)
    return ("{}", 200)

# -------------------------------------------------9-------------------------------------------------
# Read into a DB
@app.route("/api/v1/db/read", methods=["POST"])
def read():
    print("------API#9------")
    query = 'SELECT '
    columns = request.get_json()["columns"]
    where = request.get_json()["where"]
    table = request.get_json()["table"]
    try:
        distinct = request.get_json()["distinct"]
        query+='DISTINCT '
    except:
        distinct = '0'
    '''
    Made the read a little more flexible with respect to where conditions and select * condition
    '''
    if len(columns) != 1:
        for col in columns.split(','):
            query += col+','
        query = query[0:-1]
    else:
        query = 'SELECT '+columns
    if where != '':
        query = query+' FROM '+table+' WHERE ('
        where = where.split(",")
        for i in range(len(where)):
            if(i != 0):
                query += ' AND '
            query += where[i]
        query += ")"
    else:
        query = query+' FROM '+table
    print(query)
    mycursor.execute(query)
    s = mycursor.fetchall()
    print(str(s))
    # Return a string of mycursor.fetchall() that the calling api can parse into a list easily
    return (str(s), 200)


if __name__ == '__main__':
    app.debug = True
    app.run()
    mydb.close()