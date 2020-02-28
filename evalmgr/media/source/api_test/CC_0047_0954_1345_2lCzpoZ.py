import flask
from flask import *
from flask import Flask
from flaskext.mysql import MySQL
import json
import requests
import re
import csv
import datetime

mysql = MySQL()
app = Flask(__name__)

app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'pranav'
app.config['MYSQL_DATABASE_DB'] = 'ride'
app.config['MYSQL_DATABASE_SOCKET'] = None
mysql.init_app(app)
conn = mysql.connect()
cur = conn.cursor()

with open('AreaNameEnum.csv', mode='r') as infile:
    reader = csv.reader(infile)
    mydict = {rows[0]:rows[1] for rows in reader}

# Starting In Order to Code The API

#API No.1 Add username and password
@app.route('/api/v1/users', methods = ["PUT"])
def add_user():
    """
    201: Created 
    400: Bad Request
    405: Method Not Allowed
    500: Internal Server Error
    """
    
    username = flask.request.json["username"]
    password = flask.request.json["password"]
    read_data={"table":"users","columns":"username","type":"","where":"username="+username}
    read_api_end = "http://127.0.0.1:5000/api/v1/db/read"
    r=requests.post(url = read_api_end, json = read_data)
    resp = r.text
    resp=json.loads(resp)
    print(resp,type(resp),resp != [])
    if resp != []:  #user already exists
        return '',400
    if not re.match("^[a-fA-F0-9]{40}$",password): #Password Not Hashed
        return '',400 
    api_end = "http://127.0.0.1:5000/api/v1/db/write"
    data = {"insert":[username,password],"columns":["username","password"],"table":"users","type":"create"}
    try:
        r=requests.post(url = api_end, json = data)
        if (r.text == "success"):
            return jsonify({}),201
        else:
            return '',500
    except:
        return '',500

#API No.2 Delete an existing user
@app.route('/api/v1/users/<username>', methods = ["DELETE"])
def delete_user(username):
    """
    200 : OK 
    400 : Bad Request
    405 : Method Not Allowed
    """
    #print("Username to delete: ",username)
    read_data={"table":"users","columns":"username","where":"username="+username}
    read_api_end = "http://127.0.0.1:5000/api/v1/db/read"
    r=requests.post(url = read_api_end, json = read_data)
    resp = r.text
    resp=json.loads(resp)
    print(resp)
    if resp != []:
        write_data = "http://127.0.0.1:5000/api/v1/db/write"
        data = {"insert":username,"columns":"username","table":"users","type":"delete"}
        try:
            r=requests.post(url = write_data, json = data)
            #cur.execute("DELETE FROM users WHERE username = %s",username)
            #conn.commit()
            if (r.text == "success"):
                return jsonify({}),200 #User deleted Successfully
            else:
                return '',500
        except:
            return '',500
    return '',204 #User Not Present

#API No. 3 Create a New Ride
@app.route('/api/v1/rides', methods = ["POST"])
def create_ride():
    """
    201: Created
    400: Bad Request
    405: Method Not Allowed
    """
    created = flask.request.json["created_by"]
    read_data={"table":"users","columns":"username","where":"username="+created,"type":""}
    read_api_end = "http://127.0.0.1:5000/api/v1/db/read"
    r=requests.post(url = read_api_end, json = read_data)
    resp = r.text
    resp=json.loads(resp)
    if resp == []:
        return '',400
    timestamp = flask.request.json["timestamp"]
    source = flask.request.json["source"]
    destination = flask.request.json["destination"]
    source = mydict[source]
    destination = mydict[destination]
    
    write_data = "http://127.0.0.1:5000/api/v1/db/write"
    data = {"insert":[created,source,destination,timestamp],"columns":["created_by","source","destination","timestamp"],"table":"ride_info","type":"create"}
    try:
        r=requests.post(url = write_data, json = data)
        if (r.text == "success"):
            return jsonify({}),201
        else:
            return '',500
    except:
        return '',500

#API No. 4 List all upcoming Rides Given Src and Destn
@app.route('/api/v1/rides' ,methods = ["GET"])

def list_rides():
    """
    200 : OK
    400 : Bad Request
    405 : Method Not Allowed
    """
    #print("request method is : ",flask.request.method)
    source = flask.request.args.get("source")
    destination = flask.request.args.get("destination")
    if (int(source) not in range(1,200) or int(destination) not in range(1,200)):
        return '',400
    source = mydict[source]
    destination = mydict[destination]
    d = datetime.datetime.now()
    # initial = str(d).split(" ")
    # date_init = initial[0].split("-")
    # time_init = initial[1].split(":")
    # date = date_init[2] + "-" + date_init[1] + "-" + date_init[0]
    # time = time_init[2] + ":" + time_init[1] + ":" + time_init[0]
    # stamp = date + ";" + time
    read_data = {"table":"ride_info","type":"read","columns":"ride_id,created_by,timestamp","where":"source="+'\''+source+'\''+" and destination="+'\''+destination+'\''}
    read_api_end = "http://127.0.0.1:5000/api/v1/db/read"
    r=requests.post(url = read_api_end, json = read_data)
    resp = r.text
    #print(resp)
    resp=json.loads(resp)
    if resp == []:
        return '',204
    reply = []
    print(resp)
    now = datetime.datetime.today()
    for i in resp:
        #print(i[2])
        temp_d = {}
        temp_d["rideId"]=i[0]
        temp_d["username"]=i[1]
        temp_d["timestamp"]=i[2]
        stamp = datetime.datetime.strptime(temp_d["timestamp"], '%d-%m-%Y:%S-%M-%H')
        #stamp = str(stamp).split(" ")[0]+":"+str(stamp).split(" ")[1].replace(":", "-")
        #print("stamp",stamp)
        #print("i", i[2])
        #print("now", now)
        if (stamp > now):
            reply.append(temp_d)
    #print(reply)
    return jsonify(reply),200

#API No.5 List Ride Details Given Ride ID

@app.route('/api/v1/rides/<rideId>',methods = ["GET"])
def ride_details(rideId):
    """
    200 : OK
    204 : No Content
    405 : Method Not Allowed
    """
    read_data = {"table":"ride_info","columns":"*","where":int(rideId),"type":"read"}
    read_api_end = "http://127.0.0.1:5000/api/v1/db/read"
    r=requests.post(url = read_api_end, json = read_data)
    resp = r.text
    resp=json.loads(resp)
    if resp == []:
       return '',400
    resp_list = resp[0]
    user_list = json.loads(resp_list[5])
    resp_dict = {}
    resp_dict["users"] = user_list
    resp_dict["rideId"] = resp_list[0]
    resp_dict["created_by"] = resp_list[1]
    resp_dict["timestamp"] = resp_list[4]
    resp_dict["source"] = resp_list[2]
    resp_dict["destination"] = resp_list[3]
    return jsonify(resp_dict),200

#API No.6 To Join a Ride

@app.route('/api/v1/rides/<rideId>', methods = ["POST"])
def join_ride(rideId):
    """
    200 : OK
    400 : Bad Request
    405 : Method Not Allowed
    """
    username = flask.request.json["username"]
    read_data={"table":"users","columns":"username","where":"username="+username}
    read_api_end = "http://127.0.0.1:5000/api/v1/db/read"
    r = requests.post(url = read_api_end, json = read_data)
    resp1 = r.text
    resp1 = json.loads(resp1)
    #print(resp)
    if resp1 == []:
        return '',400
    read_data = {"table":"ride_info","columns":"*","where":int(rideId),"type":""}
    read_api_end = "http://127.0.0.1:5000/api/v1/db/read"
    r = requests.post(url = read_api_end, json = read_data)
    resp2 = r.text
    resp2 = json.loads(resp2)
    if resp2 == []:
       return '',400
    resp_list = resp2[0]
    user_list = json.loads(resp_list[5])
    user_list.append(username)
    user_list = json.dumps(user_list)
    #print(user_list,type(user_list))
    #print(resp)
    data = {"insert":user_list,"columns":"riders","table":"ride_info","type":"update","where":rideId}
    write_data = "http://127.0.0.1:5000/api/v1/db/write"
    try:
        r=requests.post(url = write_data, json = data)
        if (r.text == "success"):
            return jsonify({}),200
        else:
            return '',500
    except:
        return '',500
#API No. 7   Delete a Ride

@app.route('/api/v1/rides/<rideId>' , methods = ["DELETE"])
def delete_ride(rideId):
    """
    200 : OK 
    400 : Bad Request
    405 : Method Not Allowed
    """
    read_data={"insert":"","table":"ride_info","columns":"","where":"ride_id="+rideId, "type":"delete"}
    read_api_end = "http://127.0.0.1:5000/api/v1/db/read"
    r=requests.post(url = read_api_end, json = read_data)
    resp = r.text
    resp=json.loads(resp)
    #print(resp)
    if resp == []:
        return '',400
    write_data = "http://127.0.0.1:5000/api/v1/db/write"
    data = {"insert":rideId,"table":"ride_info","columns":"","where":"ride_id="+rideId,"type":"delete"}
    try:
        r=requests.post(url = write_data, json = data)
        if (r.text == "success"):
            return jsonify({}),200
        else:
            return '',500
    except:
        return '',500

#API No. 8 Write to the DB

@app.route('/api/v1/db/write', methods = ["POST"])
def write_to_db():
    if (flask.request.method == "POST"):
        insert = flask.request.json["insert"]
        columns = flask.request.json["columns"]
        table = flask.request.json["table"]
        if (table == "users" and flask.request.json["type"] == "create"):
            cur.execute("INSERT INTO "+table+" ("+columns[0]+","+columns[1]+" )"+ " values (%s, %s)", (insert[0], insert[1]))
            conn.commit()
            #mysql.connection.close()
            return "success"

        elif (table == "users" and flask.request.json["type"] == "delete"):
            #print("DELETE FROM users WHERE username="+insert)
            cur.execute("DELETE FROM users WHERE username="+'\''+insert+'\'')
            conn.commit()
            return "success"

        elif (table == "ride_info" and flask.request.json["type"] == "update"):
            cur.execute("UPDATE ride_info SET riders="+'\''+insert+'\''+" WHERE ride_id="+str(flask.request.json["where"]))
            # conn.commit()
            #print("UPDATE ride_info SET riders="+'\''+insert+'\''+" WHERE ride_id="+str(flask.request.json["where"]))
            conn.commit()
            return "success"

        elif (table == "ride_info" and flask.request.json["type"] == "delete"):
            #print("DELETE FROM ride_info WHERE ride_id="+insert)
            cur.execute("DELETE FROM ride_info WHERE ride_id="+insert)
            conn.commit()
            return "success"

        elif (table == "ride_info" and flask.request.json["type"] == "create"):
            #print("type of columns ",type(columns),columns)
            #print("type of insert ",type(insert),insert)
            l=[]
            #l.append(insert[0])
            l=json.dumps(l)
            cur.execute("INSERT INTO "+table+" ("+columns[0]+","+columns[1]+","+columns[2]+","+columns[3]+",riders)"+ " values (%s, %s, %s, %s, %s)", (insert[0], insert[1], insert[2], insert[3],l))
            conn.commit()
            return "success"

    else:
        abort(405)

#API No.9   Read from the DB

@app.route('/api/v1/db/read', methods = ["POST"])
def read_to_db():
    #print(flask.request.json)
    table = flask.request.json["table"]
    columns = flask.request.json["columns"]
    where = flask.request.json["where"]
    if table == "users" or (table == "ride_info" and flask.request.json["type"] == "delete"):
        #For API No 2 and 7
        where = where.split("=")
        #print(where)
        cur.execute("SELECT * FROM "+table+" where "+where[0]+"= %s", (where[1]))
        conn.commit()
        data = cur.fetchall()
        #print("type of data is ",type(data),"and data is ",data[0][0])
        return jsonify(data)

    elif table == "ride_info" and columns == '*':
        #For API NO.5
        # print("SELECT * FROM ride_info where ride_id="+str(where))
        cur.execute("SELECT * FROM ride_info where ride_id="+str(where))
        conn.commit()
        data = cur.fetchall()
        return jsonify(data)

    elif table == "ride_info":
        #print("select ride_id,created_by,timestamp from ride_info where "+where)
        cur.execute("select ride_id,created_by,timestamp from ride_info where "+where)
        conn.commit()
        data = cur.fetchall()
        return jsonify(data)

if __name__ == '__main__':
    app.run(debug = True)
