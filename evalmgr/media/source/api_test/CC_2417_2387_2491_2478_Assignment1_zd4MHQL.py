from flask import Flask,render_template,jsonify,request,abort
import pymysql
import json
import requests
import string
import csv
import enum
app=Flask(__name__)
item = ()

connection = pymysql.connect(host="localhost",user="madhu",passwd="password",database="cloud" )
cursor = connection.cursor()

#1.Add user!
@app.route("/api/v1/users",methods=["PUT"])
def add_user():
    usname = request.get_json()['username']
    passw = request.get_json()['password']
    err_code = 400
    if len(str(passw)) != 40:
        return {},400
    for letter in passw: 
        if letter not in string.hexdigits: 
            return {},400
    payload = {"condition":usname,"condition1":passw,"module":"add_user"}
    response = requests.post('http://127.0.0.1:5000/api/v1/db/read', json= payload)
    if response.json() == 400 :
        return {},400
    elif response.json() == 201:
        response1 = requests.post('http://127.0.0.1:5000/api/v1/db/write', json= payload)
        print("response of write_data")
        print(response1.json())
        return {},201

#2.Delete User!
@app.route("/api/v1/users/<name>",methods=["DELETE"])
def delete_data(name):
    payload = {"condition":name,"module":"delete_data"}
    response = requests.post('http://127.0.0.1:5000/api/v1/db/read', json= payload)
    if response.json() == 400 :
        return {},400
    elif response.json() == 200:
        response1 = requests.post('http://127.0.0.1:5000/api/v1/db/write', json= payload)
        return {},200

#3.Create Ride!
@app.route("/api/v1/rides",methods=["POST"])
def create_ride():    
    user_name = request.get_json()['created_by']
    time = request.get_json()['timestamp']
    source = request.get_json()['source']
    destination = request.get_json()['destination']
    with open('AreaNameEnum.csv') as f:
          reader=csv.reader(f)
          Area_list=list(reader)
          cc=enum.Enum('cc', Area_list)
          count = 0
          count1 = 0
          for status in cc:
              if status.value == source or status.name == str(source):
                    count += 1
              elif status.value == destination or status.name == str(destination):
                    count1 +=1
    if count > 0 and count1 > 0 :
        payload = {"condition":user_name,"condition1":time,"condition2":source,"condition3":destination,"module":"create_ride"}
        response = requests.post('http://127.0.0.1:5000/api/v1/db/read', json= payload)
        print("payload")
        print(payload)
        print("received response from read_data")
        print(response.json()) 
        if response.json() == 400 :
            # print("400")
            return {},400
        elif response.json() == 200:
            # print("200")
            response1 = requests.post('http://127.0.0.1:5000/api/v1/db/write', json= payload)
            # print("response of write_data")
            print(response1.json())
            return {},200
    else:
        return "",400

#4.List of all Upcoming rides!
@app.route("/api/v1/rides",methods=["GET"])
def upcoming_ride():
    source = request.args.get('source')
    destination = request.args.get('destination')
    if len(source) == 0 and len(destination) == 0:
        return {},400
    payload = {"condition1":source,"condition2":destination,"module":"upcoming_ride"}
    response = requests.post('http://127.0.0.1:5000/api/v1/db/read',json=payload)
    # print(response.json())
    data = list(response.json())
    returnlist = []
    data1 = []
    # looping through the list of lists, taking one_list at a time 
    # making a dictionary and storing all the dictionaries in a separate
    # return_list
    for k in range(len(data)):
        print(k)
        one_list = data[k]
        data11 = {"rideId":one_list[0],"username":one_list[1],"timestamp":one_list[2]}
        returnlist.append(data11)
        print(returnlist)
    print("response data")
    print("total data")
    print(returnlist)
    return jsonify(returnlist)

#5.All the details of a given ride!
@app.route("/api/v1/rides/<rideid>",methods=["GET"])
def ride_details(rideid):
    print("ride id received by postman")
    print(rideid)
    payload = {"condition":rideid,"module":"ride_details"}
    response = requests.post('http://127.0.0.1:5000/api/v1/db/read',json = payload)
    print("response received from read_data")
    # print(response.json())
    # print(response)
    data = list(response.json())
    data1 = []
    ass_riders = []
    try: 
        ass_riders = data[1]
    except:IndexError 
    data1 = data[0]
    data11 = {"rideId":data1[0],"Created_by":data1[1],"users":ass_riders,"Timestamp":data1[2],"source":data1[3],"destination":data1[4]}
    print(data11)
    received =response.json()
    return data11

#6.Joining Existing Ride!
@app.route("/api/v1/rides/<rideid>",methods=["POST"])
def join_ride(rideid):
    user_name = request.get_json()['username']
    payload = {"condition1":rideid,"condition2":user_name,"module":"join_ride"}
    response = requests.post('http://127.0.0.1:5000/api/v1/db/read', json= payload)
    if response.json() == 405 :
        return {},response.json()
    elif response.json() == 200:
        response = requests.post('http://127.0.0.1:5000/api/v1/db/write',json= payload)
        return {},response.json()    
    
#7.Delete a Ride!
@app.route("/api/v1/rides/<rideid>",methods=["DELETE"])
def delete_ride(rideid):
    print("below rideid received by postman")
    print(rideid)
    payload = {"condition":rideid,"module":"delete_ride"}
    print("Below is the payload")
    print(payload)
    response = requests.post('http://127.0.0.1:5000/api/v1/db/read', json= payload)
    print("Response of read_data")
    print(response.json())
    if response.json() == 405:
        return {},response.json()
    else:
        response = requests.post('http://127.0.0.1:5000/api/v1/db/write', json=payload)
        print("Response of write_data")
        print(response.json())
        if response.json() == 405:
            return {},response.json()
        elif response.json() == 200:
            return {},200

#8.Write Data!
@app.route("/api/v1/db/write",methods=["POST"])
def write_data():
    received_data = request.get_json()
    mylist = []

    if received_data["module"] == "add_user":
        for keys,values in received_data.items():
            mylist.append(values)
        condition1 = mylist[0]
        condition2 = mylist[1]
        query = """INSERT INTO users(username,password)VALUES (%s, %s)"""
        recordTuple = (condition1,condition2)
        cursor.execute(query,recordTuple)
        result = cursor.fetchall()
        connection.commit()
        if len(result) == 0:
            return jsonify(201)
        else:
            return jsonify(400)
        
    if received_data["module"] == "delete_data":
        for keys,values in received_data.items():
            mylist.append(values)
        condition = mylist[0]
        query = """DELETE FROM users WHERE username =%s"""
        recordTuple = (condition)
        cursor.execute(query,recordTuple)
        result = cursor.fetchall()
        connection.commit()
        if cursor.rowcount == 0:
            return jsonify(400)
        else:
            return jsonify(200)

    if received_data["module"] == "join_ride":
        for keys,values in received_data.items():
            mylist.append(values)
        condition1 =  mylist[0]
        condition2 =  mylist[1]
        query = """INSERT INTO associated_riders(rideid,name)VALUES(%s, %s)"""
        recordTuple = (condition1,condition2)
        cursor.execute(query,recordTuple)
        result = cursor.fetchall()
        connection.commit()
        if len(result) == 0:
            return jsonify(200)
        else:
            return jsonify(405)

    if received_data["module"] == "delete_ride":
        for keys,values in received_data.items():
            mylist.append(values)   
        print("Received by write_data from delete_ride")
        condition =  mylist[0]
        print(condition)
        query = """DELETE FROM ride WHERE rideid = %s"""
        cursor.execute(query, condition)
        result = cursor.fetchall()
        connection.commit()
        if cursor.rowcount == 0:
            return jsonify(405)
        else:
            return jsonify(200) 
 
    if received_data["module"] == "create_ride":
        for keys,values in received_data.items():
            mylist.append(values)
        condition1 = mylist[0]
        condition2 = mylist[1]
        condition3 = int(mylist[2])
        condition4 = int(mylist[3])
        print("In write from create_ride")
        print(condition2)
        query = """INSERT INTO ride(username,time,source,destination)VALUES(%s, %s, %s, %s)"""
        recordTuple = (condition1,condition2,condition3,condition4)
        cursor.execute(query,recordTuple)
        result = cursor.fetchall()
        connection.commit()
        if cursor.rowcount == 0:
            return jsonify(400)
        else:
            return jsonify(200)
    
#9.Read Data!
@app.route("/api/v1/db/read",methods=["POST"])
def read_data():
    received_data = request.get_json()
    mylist = []

    if received_data["module"] == "add_user":
        for keys,values in received_data.items():
                mylist.append(values)
        condition = mylist[0]
        query = """SELECT username,password FROM users WHERE  username = %s"""
        cursor.execute(query,condition)
        result = cursor.fetchall()
        if len(result) == 0:
                return jsonify(201)
        else:
                return jsonify(400)
        
    if received_data["module"] == "delete_data":
        for keys,values in received_data.items():
            mylist.append(values)
        condition = mylist[0]
        query = """SELECT username FROM users WHERE username =%s"""
        recordTuple = (condition)
        cursor.execute(query,recordTuple)
        result = cursor.fetchall()
        connection.commit()
        if cursor.rowcount == 0:
                return jsonify(400)
        else:
                return jsonify(200)

    if received_data["module"] == "upcoming_ride":
        for keys,values in received_data.items():
            mylist.append(values)
        condition1 = mylist[0]
        condition2 = mylist[1]
        print(type(mylist[0]))
        query = """ SELECT rideid,username,time FROM ride WHERE source = %s AND destination = %s AND time >= CURRENT_TIME();"""
        recordTuple = (condition1,condition2)
        cursor.execute(query, recordTuple)
        result = cursor.fetchall()
        # print("total data")
        # print(result)
        connection.commit()
        if len(result) == 0:
            # 400 is bad request!
                return jsonify(400)
        else:
                return jsonify(result)

    if received_data["module"] == "join_ride":
        # r = json.dumps(received_data)
        for keys,values in received_data.items():
            mylist.append(values)
        condition1 = mylist[0]
        condition2 = mylist[1]
        print("in read_data received from join_ride")
        print(condition1)
        print(condition2)
        query = """SELECT rideid FROM ride WHERE rideid =%s"""
        cursor.execute(query,condition1)
        result = cursor.fetchall()
        connection.commit()
        query1 = """SELECT username FROM users WHERE username =%s""" 
        cursor.execute(query1,condition2)
        result1 = cursor.fetchall()
        connection.commit()
        print("below is the length of ride table's output")
        print(len(result))
        print("below is the length of users table's output")
        print(len(result1))
        if len(result) == 0 or len(result1) == 0:
            # 405 is method not allowed!
            return jsonify(405)   
        else:
            return jsonify(200)
        
    if received_data["module"] == "delete_ride":
        for keys,values in received_data.items():
            mylist.append(values)
        print("Received by read_data from delete_ride")
        condition =  mylist[0]
        print(condition)
        query = """SELECT rideid FROM ride WHERE rideid = %s"""
        cursor.execute(query,condition)
        result = cursor.fetchall()
        connection.commit()
        if cursor.rowcount != 0:
                return jsonify(200)
        else:
                return jsonify(405)
    
    if received_data["module"] == "ride_details":
        for keys,values in received_data.items():
            mylist.append(values)
        print("received by read_data from ride_details")
        condition = mylist[0]
        print(condition)
        query1 = """SELECT rideid,username,time, source, destination FROM ride WHERE rideid = %s"""
        recordTuple = (condition)
        cursor.execute(query1,recordTuple)
        result = cursor.fetchall()
        print(result)
        data = list(result)
        print(data)
        data1 = list(data[0])
        print("type of data")
        print(data1[-1])
        print(type(data1[-1]))
        query2 = """SELECT name FROM associated_riders WHERE rideid = %s"""
        recordTuple = (condition)
        cursor.execute(query2,recordTuple)
        result2 = cursor.fetchall()
        # print(result)
        result = result + result2
        connection.commit()
        print("after query execution in read data")
        if len(result) == 0:
            return {},405
        else:
            return jsonify(result)

    if received_data["module"] == "create_ride":
        for keys,values in received_data.items():
            mylist.append(values)
        condition1 = mylist[0]
        print("in read_data from create_ride")
        print(condition1)
        query = """SELECT username FROM users WHERE username =%s"""
        recordTuple = (condition1)
        cursor.execute(query,recordTuple)
        result = cursor.fetchall()
        print(result)
        connection.commit()
        if len(result) == 0:
            return jsonify(400)
        else:
            return jsonify(200)
        
        
if __name__=='__main__':
	app.debug=True
	app.run(host='0.0.0.0')

connection.commit()
connection.close()
