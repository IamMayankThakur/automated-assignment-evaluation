from flask import Flask, request,abort 
import sqlite3
import json
import requests
import csv
import datetime

area = {}
with open('AreaNameEnum.csv', mode='r') as infile:
    reader = csv.reader(infile)
    area = {rows[0]:rows[1] for rows in reader}


def isSHA1(s):
    if len(s) != 40:return False
    try:i = int(s, 16)
    except ValueError:return False
    return True

def getDate(s):
    try:
        x = datetime.datetime.strptime(s,"%d-%m-%Y:%S-%M-%H")
        return x
    except ValueError:
        return False

app=Flask(__name__)

# 1
@app.route('/api/v1/users',methods=["PUT"]) #returns 405 if any other method is used
def add_user():
    req=request.get_json()
    fields = {"username","password"}
    if not(fields.issubset(req)):return {},400
    if isSHA1(req["password"])==False:
        return {},400 # Bad Request
    body = {"table":"users","column":"'username','password'","insert":"'{}','{}'".format(req["username"],req["password"])}
    x = requests.post('http://127.0.0.1:5000/api/v1/db/write', json=body)
    if(x.text=="True"):return {},201
    else:return {},400


# 2
@app.route('/api/v1/users/<user_name>',methods=["DELETE"])
def rem_user(user_name):
    body1 = {"table":"users","column":"*","where":"username = '{}'".format(user_name)}
    body2 = {"table":"users","delete":"username = '{}'".format(user_name)}
    x = requests.post('http://127.0.0.1:5000/api/v1/db/read', json=body1)
    if(x.text=="[]"):return {},400
    x = requests.post('http://127.0.0.1:5000/api/v1/db/write', json=body2)
    if(x.text=="True"):return {},200
    else:return {},400
#3
@app.route('/api/v1/rides', methods=["POST"])
def create_new_ride():
    req=request.get_json()
    fields = {"created_by","timestamp","source"}
    if not(fields.issubset(req)):return {},400
    if req["source"] not in area or req["destination"] not in area: return {},400
    d = getDate(req["timestamp"])
    if(d==False or d<datetime.datetime.now()): return {},400
    body = {"table":"ride","column":"created_by,timestamp,source,destination","insert":"'{}','{}',{},{}".format(req["created_by"],req["timestamp"],req["source"],req["destination"])}
    x = requests.post('http://127.0.0.1:5000/api/v1/db/write', json=body)
    if(x.text=="True"):return {},201
    else: return {},400

#4
@app.route('/api/v1/rides', methods=["GET"])
def list_all_rides():
    if ('source' not in request.args) or ('destination' not in request.args):return {},400
    source=request.args.get('source')
    destination=request.args.get('destination')
    if source not in area or destination not in area:return {},400
    data={"table":"ride","column":"ride_id,created_by,timestamp","where":"source={} AND destination={}".format(source,destination)}
    r=requests.post("http://127.0.0.1:5000/api/v1/db/read",json=data)
    rl = json.loads(r.text)
    body = list()
    if(len(rl)==0):return {},204
    flag = True
    for row in rl:
        if(getDate(row[2])>datetime.datetime.now()):
            flag = False
            d = {}
            d["rideId"]=row[0]
            d["username"]=row[1]
            d["timestamp"]=row[2]
            body.append(d)
    if flag:return {},204
    return json.dumps(body),200

#5
@app.route('/api/v1/rides/<ride_id>',methods=["GET"])
def list_details(ride_id):
    data={"table":"ride","column":"created_by,timestamp,source,destination","where":"ride_id={}".format(ride_id)}
    r=requests.post("http://127.0.0.1:5000/api/v1/db/read",json=data)
    s=json.loads(r.text)
    #If the ride_id does not exist
    if(len(s)==0):return {},204
    s=s[0]
    body ={}
    body["rideId"]=ride_id
    body["created_by"]=s[0]
    data={"table":"ride_pool","column":"username","where":"ride_id={}".format(ride_id)}
    r=requests.post("http://127.0.0.1:5000/api/v1/db/read",json=data)
    s1=json.loads(r.text)
    l1=[row[0] for row in s1]
    body["users"] = l1
    body["timestamp"]=s[1]
    body["source"]=s[2]
    body["destination"]=s[3]
    return json.dumps(body),200

#6
@app.route('/api/v1/rides/<ride_id>',methods=['POST'])
def join_ride(ride_id):
    req=request.get_json()
    fields = {"username"}
    if not(fields.issubset(req)):return {},400
    data={"table":"ride_pool","column":"*","where":"ride_id={} AND username='{}'".format(ride_id,req["username"])}
    r=requests.post("http://127.0.0.1:5000/api/v1/db/read",json=data)
    if(len(json.loads(r.text))!=0):return {},204
    data={"table":"ride_pool","insert":"'{}','{}'".format(req["username"],ride_id),"column":"username,ride_id"}
    r=requests.post("http://127.0.0.1:5000/api/v1/db/write",json=data)
    if(r.text=="True"):return {},201
    else: return {},400 #or 204

#7
@app.route('/api/v1/rides/<ride_id>',methods=["DELETE"])
def rem_ride(ride_id):
    body1 = {"table":"ride","column":"*","where":"ride_id = {}".format(ride_id)}
    body2 = {"table":"ride","delete":"ride_id = {}".format(ride_id)}
    x = requests.post('http://127.0.0.1:5000/api/v1/db/read', json=body1)
    if(x.text=="[]"):return {},400
    x = requests.post('http://127.0.0.1:5000/api/v1/db/write', json=body2)
    if(x.text=="True"):return {},200
    else:return {},400

#8
@app.route('/api/v1/db/write', methods=["POST"])
def write():
    req = request.get_json()
    if('insert' in req):
        query = "INSERT INTO {}({}) VALUES({})".format(req["table"],req["column"],req["insert"])
    if('delete' in req):
        query = "DELETE FROM {} WHERE {}".format(req['table'],req['delete'])
    with sqlite3.connect("rideshare.db") as conn:
        conn.execute("PRAGMA foreign_keys = 1")
        c = conn.cursor()
        c.execute(query)
        conn.commit()
        return "True"
    return "False"

#9
@app.route('/api/v1/db/read', methods=["POST"])
def read():
    req = request.get_json()
    where = req["where"]
    columns = req["column"]
    table = req["table"]
    with sqlite3.connect("rideshare.db") as conn:
        conn.execute("PRAGMA foreign_keys = 1")
        c = conn.cursor()
        query = "SELECT {} FROM {} WHERE {}".format(columns,table,where)
        c.execute(query)
        x = c.fetchall()
        return json.dumps(x)

@app.errorhandler(405)
def method_not_allowed(e):
    return {},405