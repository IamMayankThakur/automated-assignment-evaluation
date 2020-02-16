from flask import Flask,render_template,jsonify,request,abort
from random import seed
import datetime
import random
import pymysql
import string
import pandas as pd
import requests
import json


app=Flask(__name__)

#Database connection
connection = pymysql.connect(host="localhost", port=3306, user="root", passwd="", database="cloud")
cursor = connection.cursor()

#Read The CSV File
df = pd.read_csv("AreaNameEnum.csv")
locations = df.values.tolist()

# @app.route("/hello")
# def new_method():
#     print("hello i am form nginx")
#     return "", 200

# For adding User.
@app.route("/api/v1/users",methods=["PUT"])
def add_user():
    user_details = dict(request.get_json())
    payload = {"table":"User_Details","columns":["*"],\
        "where": "NULL"}
    req = requests.post("http://107.23.177.23/api/v1/db/read", json = {"query": payload})
    flag = verify_user(req.text, user_details["username"])
    if(flag == 1):
        return jsonify({}), 400

    if(check(str(user_details["password"]))):
        payload = {"insert":[str(user_details["username"]), str(user_details["password"]),str(random.randint(0, 9999999999))]\
            ,"columns":["User_Name","Password","User_Id"],"table":"User_Details"}
        req = requests.put("http://107.23.177.23/api/v1/db/write", json = {"query": payload})
        return jsonify({}), 201
    else:   
        return jsonify({}), 400


# For verifying user existence.
def verify_user(users,username):
    flag = 0;
    if(users == ""):
        return 2
    users = json.loads(users);
    # print("User is being verified",users)
    for i in users.keys():
        # print(users[i][0])
        if(users[i][0] == username):
            flag = 1;
    return flag


# For checking Whether a Password is hexadecimal or not
def check(value):  
    # print("Entered in check"+"".join(value))
    if(len(value) != 40):
        return False
    for letter in value:
        # print(letter)        
        # If anything other than hexdigit  
        # letter is present, then return  
        # False, else return True  
        if letter not in string.hexdigits:  
            return False
    return True


# For Deleting User.
@app.route("/api/v1/users/<username>", methods=["DELETE"])
def delete_user(username):
    #for deleting from Rides table first
    payload = {"table":"Rides","columns":["*"],\
        "where":"Created_by = '" + username} 
    req = requests.post("http://107.23.177.23/api/v1/db/read", json = {"query": payload}) 
    if(req.text != "") :
        result = json.loads(req.text)
        ride_ids = list()
        for i in result.keys():
            ride_ids.append(result[i][0]) 
        try:
            deleteSql = "DELETE FROM Rides WHERE Created_by = '" + str(username) + "';"
            cursor.execute(deleteSql)
            connection.commit()
            for i in ride_ids:      
                deleteSql = "DELETE FROM Ride_Shared WHERE Ride_Id = '" + i + "';"
                cursor.execute(deleteSql)
                connection.commit()
        except:
            return jsonify({}), 400
    else:
        #for deleting from Ride_Shared table first
        payload = {"table":"Ride_Shared","columns":["*"],\
                "where": "User_Name = '" + username}
        req = requests.post("http://107.23.177.23/api/v1/db/read", json = {"query": payload})  
        if(req.text != "") :
            try:
                deleteSql = "DELETE FROM Ride_Shared WHERE User_Name = '" + str(username) + "';"
                cursor.execute(deleteSql)
                connection.commit()
            except:
                return jsonify({}), 400

    #for deleting from User_Details
    payload = {"table":"User_Details","columns":["User_Name","Password"],\
        "where":"User_Name = '" + username}
    req = requests.post("http://107.23.177.23/api/v1/db/read", json = {"query": payload})
    flag = verify_user(req.text, username)
    if(flag == 0):
        return jsonify({}), 400
    if(req.status_code == 201):
        try:
            deleteSql = "DELETE FROM User_Details WHERE User_Name = '" + str(username) + "';"
            cursor.execute(deleteSql)
            connection.commit()
            return jsonify({}), 200
        except:
            return jsonify({}), 400
    elif(req.status_code == 401):
        return jsonify({}), 400
    else:       
        return jsonify({}), 405

	
# Creating New Ride
@app.route("/api/v1/rides", methods=["POST"])
def new_ride():
    # {"ride":{"created_by":"Aishu","timestamp":"02-02-2020:00-02-12","source":"Hebbala","destination":"Horamavu"}}
    rideid = 0
    ride_info = dict(request.get_json())
    # print("@@@@@===========> ",ride_info)
    # return ride_info, 200
    ride_info['timestamp'], rideid = format(str(ride_info['timestamp']).split(":"))
    print(int(ride_info["source"]) == int(ride_info["destination"]))
    print(int(ride_info["source"]) <= 1 or int(ride_info["source"]) >= 198)
    print(int(ride_info["destination"]) <= 1 or int(ride_info["destination"]) >= 198)
    
    if(int(ride_info["source"]) == int(ride_info["destination"])):
        return jsonify({}), 400
    
    elif(int(ride_info["source"]) <= 1 or int(ride_info["source"]) >= 198):
        return jsonify({}), 400

    elif(int(ride_info["destination"]) <= 1 or int(ride_info["destination"]) >= 198):
        return jsonify({}), 400


    #Adding new ride to DB
    payload = {"insert":[rideid, str(ride_info["created_by"]),str(ride_info["source"]),\
        str(ride_info["destination"]),ride_info["timestamp"]],"columns":["Ride_Id",\
            "Created_by","Source","Destination","Time_Stamp"],"table":"Rides"}
    req = requests.put("http://107.23.177.23/api/v1/db/write", json = {"query": payload})

    if(req.status_code == 201):
        return jsonify({}), 201
    else:
        return jsonify({}), 400


#Listing All Upcoming Rides
@app.route("/api/v1/rides", methods=["GET"])
def list_all_rides():
    try:
        arguments = request.args
    except:
        return jsonify({}), 400
    loc_validate = 0
    valid_user = list()
    src = ""
    dest = ""
    for i in locations:
        if(i[0] == int(arguments['source'])):
            loc_validate += 1
            src = str(i[0])
        if(i[0] == int(arguments['destination'])):
            loc_validate += 1
            dest = str(i[0])

    if(loc_validate == 2):
        payload = {"table":"Rides","columns":["*"],\
        "where": "Source='" + src + "' AND " + "Destination='" + dest}
        # print(payload)
        req = requests.post("http://107.23.177.23/api/v1/db/read", json = {"query": payload})
        if(req.text == ""):
            return jsonify({}), 204

        result = json.loads(req.text)

        # Compare current Date and time    
        now = datetime.datetime.now()
        for i in result.keys():
            check_time = str(result[i][4]).split(" ")
            date = list(check_time[0].split("-"))
            time = list(check_time[1].split("-"))
            # datetime(year, month, day, hour, minute, second, microsecond)
            x = datetime.datetime(date[0], date[1], date[2],time[0], time[1], time[2])
            if(x < now):
                wordFreqDic.pop(i)
                
        for i in result.keys():
            payload = {"table":"User_Details","columns":["*"],\
                "where":"User_Name = '" + result[i][1]}
            req = requests.post("http://107.23.177.23/api/v1/db/read", json = {"query": payload})
            if(req.status_code == 201):
                valid_user.append(i)
            else:
                return jsonify({}),400
        valid_ride = list()

        for i in valid_user:
            temp = dict()
            # print(result[i][4])
            result[i][4], dummy = format(str(result[i][4]).split(" "))
            # print(result[i][4])
            temp["rideId"] = result[i][0]
            temp["username"] = result[i][1]
            temp["timestamp"] = result[i][4]
            valid_ride.append(temp)
        # print(valid_ride)
        return jsonify(valid_ride), 200
    else:
        return jsonify({}), 400


#List Details of a Particular ID.
@app.route("/api/v1/rides/<rideId>", methods=["GET"])
def ride_details(rideId):
    try:
        payload = {"table":"Rides","columns":["*"],\
            "where": "Ride_Id = '" + str(rideId)}
        req = requests.post("http://107.23.177.23/api/v1/db/read", json = {"query": payload})
        if(req.text == ""):
            return jsonify({}), 204
        result1 = json.loads(req.text)
        payload = {"table":"Ride_Shared","columns":["*"],\
            "where": "Ride_Id = '" + str(rideId)}
        req = requests.post("http://107.23.177.23/api/v1/db/read", json = {"query": payload})
        # print(result1)
        ride_info = dict() 
        temp = list()
        result2 = dict()
        if(req.text != ""):
            result2 = json.loads(req.text)
            for i in result2.keys():
                temp.append(result2[i][1])
        
        index = list(result1.keys())
        index = str(index[0])
        ride_info["rideId"] = result1[index][0] 
        ride_info["created_by"] = result1[index][1]
        ride_info["users"] = temp;
        result1[index][4], dummy = format(str(result1[index][4]).split(" "))
        ride_info["timestamp"] = result1[index][4]
        ride_info["source"] = result1[index][2]
        ride_info["destination"] = result1[index][3]
        return jsonify(ride_info), 200
    except:
        return jsonify({}),405



#Join An existing ride.
@app.route("/api/v1/rides/<rideId>", methods=["POST"])
def join_ride(rideId):
    #Structure {"user":{"username":"Aishwarya"}}
    join_user = dict(request.get_json())
    payload = {"table":"Rides","columns":["*"],\
        "where":"Ride_Id = '" + str(rideId)}
    req = requests.post("http://107.23.177.23/api/v1/db/read", json = {"query": payload})

    result = json.loads(req.text)
    for i in result.keys():
        if (str(join_user["userName"]) == str(result[i][1])):
            return jsonify({}), 400;
    if(req.text != ""):
        payload = {"table":"User_Details","columns":["*"],\
        "where":"User_Name = '" + str(join_user["username"])}
        req = requests.post("http://107.23.177.23/api/v1/db/read", json = {"query": payload})
        if(req.status_code == 201):
            payload = {"insert": [str(rideId),str(join_user["username"])],\
                    "columns":["Ride_Id","User_Name"],"table":"Ride_Shared"}
            req = requests.put("http://107.23.177.23/api/v1/db/write", json = {"query": payload})
            if(req.status_code == 201):
                return jsonify({}), 200
            else:
                return jsonify({}), 400
        else:
            return jsonify({}), 400
    else:
        return jsonify({}), 204
            

#Delete a Ride.
@app.route("/api/v1/rides/<rideId>", methods=["DELETE"])
def delete_ride(rideId):
    try:
        payload = {"table":"Ride_Shared","columns":["*"],\
            "where": "Ride_Id = '" + str(rideId)}
        req = requests.post("http://107.23.177.23/api/v1/db/read", json = {"query": payload})
        # print(payload)
        if(req.text != ""):
            deleteSql = "DELETE FROM Ride_Shared WHERE Ride_Id = '" + str(rideId) + "';"
            cursor.execute(deleteSql)
            print(deleteSql)
            connection.commit()

        payload = {"table":"Rides","columns":["*"],\
        "where":"Ride_Id = '" + str(rideId)}
        req = requests.post("http://107.23.177.23/api/v1/db/read", json = {"query": payload})
        if(req.status_code in [400,401]):
            return jsonify({}), 400
        else:
            try:
                deleteSql = "DELETE FROM Rides WHERE Ride_Id = '" + str(rideId) + "';"
                cursor.execute(deleteSql)
                connection.commit()
                return jsonify({}), 200
            except:
                return jsonify({}), 400
    except:
        return jsonify({}), 400
        


# Format the Date and Time in Required Format    
def format(date_and_time):
    # print(date_and_time)
    # date_and_time = list(date_and_time.split(":"))
    date = list(date_and_time[0].split("-"))
    time = list(date_and_time[1].split("-"))
    if(len(time) == 1):
        time = list(date_and_time[1].split(":"))
    date_and_time = ""

    for i in range(len(date)-1,-1,-1): #Making Time and Date in Format
        date_and_time = date_and_time + str(date[i]) + "-"
    date_and_time = date_and_time[0:len(date_and_time)-1] + ":"
    for i in range(len(time)-1,-1,-1):
        date_and_time = date_and_time + str(time[i]) + "-"
    date_and_time = date_and_time[0:len(date_and_time)-1]

    return date_and_time, random.randint(0, 9999999999)


# Write to DB
@app.route("/api/v1/db/write", methods=["PUT"])
def db_write():
    # print("I am in Write DB")
    req = request.get_json()["query"]
    query = "INSERT INTO " + req["table"] + " ("
    for i in req["columns"]:
        query = query + i + ","
    query = query[0:len(query)-1] + ") VALUES("
    for i in req["insert"]:
        query = query + "'" + str(i) + "',"
    query = query[0:len(query)-1] + ");"
    try:
        print(query) 
        cursor.execute(query)
        connection.commit()
        return jsonify({"noerror":query}), 201
    except Exception as ex:
        print(ex.args)
        return jsonify({"error":query}), 400


# Read to DB
@app.route("/api/v1/db/read", methods=["POST"])
def db_read():
    req = request.get_json()["query"]
    if(req["where"] == "NULL"):
        query = "SELECT * FROM " + req["table"] + " ;"
    else:
        query = "SELECT * FROM " + req["table"] +" WHERE " + req["where"] + "';"
    try: 
        print(query)
        cursor.execute(query)
        rows = cursor.fetchall()
        data = dict()
        index = 1
        for r in rows:
            temp = list()
            for i in r:
                temp.append(str(i))
            data[index] = temp
            index += 1
        
        if (len(rows) != 0):
            return jsonify(data), 201
        else:
            return "", 401
    except:
        return "", 400



if __name__ == '__main__':

    app.debug = True
    app.run()
    