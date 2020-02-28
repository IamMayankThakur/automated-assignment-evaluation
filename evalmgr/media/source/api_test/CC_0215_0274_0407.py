from flask import Flask, render_template, jsonify, request, Response, abort
import mysql.connector
import requests
import csv
import datetime
app = Flask(__name__)

def createMeta():
    mydb = connect_to_db()
    mycursor = mydb.cursor(buffered=True)
    return mydb, mycursor

def passwordvalidate(passwd):

    if len(passwd) != 40:
        return 1

    checklist = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', ' F', 'a', 'b', 'c', 'd', 'e', 'f']

    for c in passwd:
        # print(c)
        if c not in checklist:
            return 1
    return 0


def ispresent(src):

    d = {}
    with open('AreaNameEnum.csv') as file:
        data = csv.reader(file)
        count = 0
        for row in data:
            if count == 0:
                count = count + 1
            else:
                count = count + 1
                d[row[0]] = row[1]
                # print(row)
    for keys in d.keys():
        if keys == src:
            return 1
    return 0


def istime_upcoming(timestamp):
    if datetime.datetime.strptime(timestamp, '%d-%m-%Y:%S-%M-%H') > datetime.datetime.now():
        return 1
    else:
        return 0


def valid_syntax(timestamp):
    try:
        datetime.datetime.strptime(timestamp, '%d-%m-%Y:%S-%M-%H')
        return 1
    except ValueError:
        return 0


def valid_timestamp(timestamp):

    if valid_syntax(timestamp):
        dt = timestamp.split(":")
        # print(dt)
        d = dt[0].split("-")
        t = dt[1].split("-")
        # print(d[0])
        # print(t)
        # print(len(d[0]))
        if (len(d[0]) == 2) and (len(d[1]) == 2) and (len(d[2]) == 4):
            if (len(t[0]) == 2) and (len(t[1]) == 2) and (len(t[2]) == 2):
                try:
                    datetime.datetime.strptime(timestamp, '%d-%m-%Y:%S-%M-%H')
                    return 1
                except ValueError:
                    return 0
            else:
                return 0
        else:
            return 0
    else:
        return 0


@app.route('/api/v1/users', methods=['PUT'])
def add_user():
    print("entered the add user api")
    # flag = 0

    data = request.get_json(force=True)
    name = data["username"]
    password = data["password"]

    # print(name, password)

    r = request.url_root + 'api/v1/db/read'
    w = request.url_root + 'api/v1/db/write'

    # print(r,w)

    readj = {
        'table': 'user',
        'opn': 'select',
        'where': 'Name=' + "'" + name + "'",
        'columns': ''
    }
    writej = {
        'table': 'user',
        'opn': 'insert',
        'name': name,
        'password': password,
        'columns': ''
    }

    readres = requests.post(r, json=readj)
    print(readres)
    print(readres.status_code)

    if readres.status_code == 200:
        return Response("Name Already Exists", 400)
        # raise ValueError("Name already exists")

    if passwordvalidate(password):
        return Response("Password is Invalid", 400)
        # raise ValueError("Password is Invalid")

    elif readres.status_code == 204:
        writeres = requests.post(w, json=writej)
        print(writeres)
        return jsonify({}), 201

    else:
        return jsonify({}), 400
        # raise ValueError("Bad Request")

    # if res.status_code == 400:
    #     abort(400)
    #
    # elif res.status_code == 405:
    #     abort(400, description="Invalid Username")
    #
    # elif res.status_code == 201:
    #     abort(201)
    #
    # elif res.status_code == 500:
    #     abort(500)
    #
    # elif passwordvalidate(password):
    #     abort(400)

    # else:


@app.route('/api/v1/users/<username>', methods=['DELETE'])
def delete_user(username):
    print("entered the delete user api")

    r = request.url_root + 'api/v1/db/read'
    w = request.url_root + 'api/v1/db/write'

    readj = {
        'table': 'user',
        'opn': 'select',
        'where': 'Name=' + "'" + username + "'",
    }
    read1j = {
        'table': 'joinride',
        'opn': 'select',
        'where': 'Name=' + "'" + username + "'",
    }
    read2j = {
        'table': 'ride',
        'opn': 'select',
        'where': 'Name=' + "'" + username + "'",
    }
    writej = {
        'table': 'user',
        'opn': 'delete',
        'where': 'Name=' + "'" + username + "'",
    }
    write1j = {
        'table': 'joinride',
        'opn': 'delete',
        'where': 'Name=' + "'" + username + "'",

    }
    # write2j = {
    #     'table': 'ride',
    #     'opn': 'delete',
    #     'where': 'Name=' + "'" + username + "'",
    # }

    readres = requests.post(r, json=readj)
    print(readres)

    if readres.status_code == 200:
        read1res = requests.post(r, json=read1j)
        read2res = requests.post(r, json=read2j)
        if read2res.status_code == 200:
            return Response("Ride was created by the user", 400)
            # raise ValueError("User created a ride")
        else:
            # writeres = requests.post(w, json=writej)
            # print(writeres)
            if read1res.status_code == 200:
                write1res = requests.post(w, json=write1j)
                writeres = requests.post(w, json=writej)
                # write2res = requests.post(w, json=write2j)
                print(writeres)
                print(write1res)
                # print(write2res)
                return jsonify({}), 200
            else:
                writeres = requests.post(w, json=writej)
                # write2res = requests.post(w, json=write2j)
                print(writeres)
                # print(write2res)
                return jsonify({}), 200
    elif readres.status_code == 204:
        return Response("User does not Exists", 400)
        # raise ValueError("User does not exist")
    else:
        return jsonify({}), 400
        # raise ValueError("Bad Request")


@app.route('/api/v1/rides', methods=['POST'])
def ride_user():
    print("entered the ride user api")

    data = request.get_json(force=True)
    name = data["created_by"]
    timestamp = data["timestamp"]
    src = data["source"]
    dst = data["destination"]

    r = request.url_root + 'api/v1/db/read'
    w = request.url_root + 'api/v1/db/write'

    readj = {
        'table': 'user',
        'opn': 'select',
        'where': 'name=' + "'" + name + "'",
        'columns': ''
    }
    writej = {
        'table': 'ride',
        'opn': 'insert',
        'name': name,
        # 'where': 'DestA=' + "'" + src + "' " + "& DestB=" + "'" + dest + "'",
        'src': src,
        'dst': dst,
        'timestamp': timestamp,
        'columns': ''
    }

    readres = requests.post(r, json=readj)
    print(readres)
    print(readres.status_code)
    if readres.status_code == 200:
        if src != dst:
            if ispresent(src) and ispresent(dst):
                if valid_timestamp(timestamp):
                    writeres = requests.post(w, json=writej)
                    print(writeres)
                    return jsonify({}), 201
                else:
                    return Response("Invalid Timestamp", 400)
            else:
                return Response("Source or Destination is not present", 400)
                # raise ValueError("Source or Destination is not present")
        else:
            return Response("Source and Destination is same", 400)
    else:
        return Response("User does not Exists", 400)
        # raise ValueError("User does not exist")


@app.route('/api/v1/rides', methods=['GET'])
def upcoming_rides():
    source = request.args.get('source')
    destination = request.args.get('destination')

    if ispresent(source) and ispresent(destination):
        print("entered the upcoming ride api")
        r = request.url_root + 'api/v1/db/read'
        readj = {
            'table': 'ride',
            'opn': 'select',
            'where': "DestA=" + "'" + source + "' AND " + "DestB=" + "'" + destination + "'",
            'columns': ''
        }

        readres = requests.post(r, json=readj)
        print(readres.status_code)

        # l_readres = len(list(readres.json()))

        # print(readres.json())
        # print(l_readres)

        if readres.status_code == 200:
            data_readres = readres.json()
            res = []
            for arr in data_readres:
                # print(arr[0])
                if istime_upcoming(arr[4]):
                    d = {}
                    d["rideId"] = arr[0]
                    d["username"] = arr[1]
                    d["timestamp"] = arr[4]
                    res.append(d)
            if len(res) == 0:
                return jsonify({}), 204
                # raise ValueError("No upcoming rides")
            elif source == destination:
                return jsonify({}), 204
            else:
                return jsonify(res)
        else:
            # return Response("No such source and destination exists in the database", 400)
            # raise ValueError("No such source and destination exists in the database")
            return jsonify({}), 204
    else:
        return jsonify({}), 204
        # return Response("Source or Destination is invalid", 400)


@app.route('/api/v1/rides/<rideId>', methods=['GET'])
def list_rides(rideId):
    print("entered the list rides api")

    r = request.url_root + 'api/v1/db/read'

    readj = {
        'table': 'ride',
        'opn': 'select',
        'where': 'Ride_ID=' + "'" + rideId + "'"
    }

    read1j = {
        'table': 'joinride',
        'opn': 'select',
        'where': 'Ride_ID=' + "'" + rideId + "'"
    }

    readres = requests.post(r, json=readj)

    if readres.status_code == 200:
        print(readres.json())
        readres_j = readres.json()
        d = {}
        d["rideId"] = readres_j[0][0]
        d["created_by"] = readres_j[0][1]
        d["timestamp"] = readres_j[0][4]
        d["source"] = readres_j[0][2]
        d["destination"] = readres_j[0][3]
        d["users"] = []
        read1res = requests.post(r, json=read1j)
        # print(read1res_j)
        if read1res.status_code == 200:
            read1res_j = read1res.json()
            for un in read1res_j:
                d["users"].append(un[1])
        return jsonify(d)
    else:
        return Response("Ride does not exist", 400)
        # raise ValueError("Ride does not exist")


@app.route('/api/v1/rides/<rideId>', methods=['POST'])
def join_ride(rideId):
    print("entered the join ride api")

    data = request.get_json(force=True)
    name = data["username"]

    r = request.url_root + 'api/v1/db/read'
    w = request.url_root + 'api/v1/db/write'

    readj = {
        'table': 'ride',
        'opn': 'select',
        'where': "Ride_ID=" + "'" + rideId + "'"
    }
    read1j = {
        'table': 'user',
        'opn': 'select',
        'where': 'name=' + "'" + name + "'"
    }
    read2j = {
        'table': 'joinride',
        'opn': 'select',
        'where': 'name=' + "'" + name + "' AND Ride_ID=" + "'" + rideId + "'"
    }
    read3j = {
        'table': 'ride',
        'opn': 'select',
        'where': 'Name=' + "'" + name + "' AND Ride_ID=" + "'" + rideId + "'"
    }
    writej = {
        'table': 'joinride',
        'opn': 'insert',
        'name': name,
        'rideId': rideId
    }

    readres = requests.post(r, json=readj)
    read1res = requests.post(r, json=read1j)
    read2res = requests.post(r, json=read2j)
    read3res = requests.post(r, json=read3j)

    print(readres)
    print(read1res)

    if readres.status_code == 200:
        if read3res.status_code == 204:
            if read1res.status_code == 200:
                if read2res.status_code == 204:
                    writeres = requests.post(w, json=writej)
                    print(writeres.status_code)
                else:
                    return Response("User has already joined the ride", 400)
                    # raise ValueError("Username and ride already exists in join table")
            else:
                return Response("Username does not exist", 400)
                # return jsonify({}), 400
                # raise ValueError("Username does not exist")
        else:
            return Response("User created the ride", 400)
            # raise ValueError("User created the ride")
    else:
        return Response("Ride does not exist", 400)
        # return jsonify({}), 400
        # raise ValueError("Ride does not exist")

    return jsonify({})


@app.route('/api/v1/rides/<rideId>', methods=['DELETE'])
def delete_ride(rideId):
    print("entered the delete ride api")

    r = request.url_root + 'api/v1/db/read'
    w = request.url_root + 'api/v1/db/write'

    readj = {
        'table': 'ride',
        'opn': 'select',
        'where': 'Ride_ID=' + "'" + rideId + "'"
    }

    read1j = {
        'table': 'joinride',
        'opn': 'select',
        'where': 'Ride_ID=' + "'" + rideId + "'"
    }

    writej = {
        'table': 'ride',
        'opn': 'delete',
        'where': 'Ride_ID=' + "'" + rideId + "'"
    }

    write1j = {
        'table': 'joinride',
        'opn': 'delete',
        'where': 'Ride_ID=' + "'" + rideId + "'"
    }

    readres = requests.post(r, json=readj)

    if readres.status_code == 200:
        read1res = requests.post(r, json=read1j)
        if read1res.status_code == 200:
            write1res = requests.post(w, json=write1j)
            writeres = requests.post(w, json=writej)
            print(writeres)
            print(write1res)
        else:
            writeres = requests.post(w, json=writej)
            print(writeres)
        return jsonify({})
    else:
        return Response("Ride does not exist", 400)
        # return jsonify({}), 400
        # raise ValueError("Ride does not exist")


def connect_to_db():
    mydb_connect = mysql.connector.connect(
        host='localhost',
        # port= 5555,
        user='root',
        password='root@123',
        database='rideshare'
    )
    return mydb_connect


def create_database():
    mycursor.execute("CREATE DATABASE rideshare")


def create_tables():
    mycursor.execute("CREATE TABLE user (Name VARCHAR(255) PRIMARY KEY, Password VARCHAR(255))")
    # mycursor.execute("CREATE TABLE ride (Ride_ID INT PRIMARY KEY AUTO_INCREMENT, "
    #                  "Name  VARCHAR(255), "
    #                  "DestA VARCHAR(255), "
    #                  "DestB VARCHAR(255), "
    #                  "Timestamp VARCHAR(255))")
    # mycursor.execute("CREATE TABLE joinride (ID INT PRIMARY KEY AUTO_INCREMENT, "
    #                  "Name VARCHAR(255), Ride_ID INT, "
    #                  "FOREIGN KEY (Name) REFERENCES user(Name), FOREIGN KEY (Ride_ID) REFERENCES ride(Ride_ID))")


@app.route('/api/v1/db/read', methods=['POST'])
def read_db():
    mydb, mycursor = createMeta()

    print("entered read api")

    req = request.get_json()

    # json = { 'table': 'user',
    #          'operation': 'select',
    #          'method': 'POST',
    #          'columns':,
    #          'where':
    # }

    table = req['table']
    opn = req['opn']
    where = req['where']

    # to select from table in database

    # print(table, opn)
    # if opn == "select":
    #     sql = "SELECT * FROM " + table + ";"
    #     # val = (table,)
    #     mycursor.execute(sql)
    #     # myresult = mycursor.fetchall()
    #     # print(myresult)
    #     # for x in myresult:
    #     #     print(x)
    #     return jsonify({})

    # to select from table where in database

    if table == 'user':
        if opn == 'select':
            if where:
                sql = "SELECT * FROM " + table + " WHERE " + where + ";"
                mycursor.execute(sql)
                myresult = mycursor.fetchall()
                # print(myresult)
                # for x in myresult:
                #     print(x)
                if len(myresult) != 0:
                    return jsonify({}), 200
                else:
                    return jsonify({}), 204
    else:
        if opn == 'select' and where:
            sql = "SELECT * FROM " + table + " WHERE " + where + ";"
            mycursor.execute(sql)
            myresult = mycursor.fetchall()
            # print(myresult)
            if len(myresult) != 0:
                return jsonify(myresult), 200
            else:
                return jsonify({}), 204
    return 1


@app.route('/api/v1/db/write', methods=['POST'])
def write_db():
    mydb, mycursor = createMeta()
    print("entered write api")

    req = request.get_json()
    table = req['table']
    opn = req['opn']
    # print(table, opn, name)

    if table == 'user':
        if opn == 'insert':
            name = req['name']
            password = req['password']
            sql = """INSERT INTO user (Name, Password) VALUES (%s, %s);"""
            val = (name, password)
            mycursor.execute(sql, val)
            mydb.commit()
            # print("1 record inserted, ID:", mycursor.lastrowid)
            return jsonify({})
        elif opn == 'delete':
            where = req['where']
            sql = "DELETE FROM " + table + " WHERE " + where + ";"
            mycursor.execute(sql)
            mydb.commit()
            if mycursor.rowcount != 0:
                return jsonify({}), 200
            else:
                return jsonify({}), 400
            # print(mycursor.rowcount, "record(s) deleted")

    elif table == 'ride':
        if opn == 'insert':
            name = req['name']
            src = req['src']
            dst = req['dst']
            timestamp = req['timestamp']
            sql = """INSERT INTO ride (Name, DestA, DestB, Timestamp) VALUES (%s, %s, %s, %s)"""
            val = (name, src, dst, timestamp)
            mycursor.execute(sql, val)
            mydb.commit()
            return jsonify({}), 200
        else:
            where = req['where']
            sql = "DELETE FROM " + table + " WHERE " + where + ";"
            mycursor.execute(sql)
            mydb.commit()
            if mycursor.rowcount != 0:
                return jsonify({}), 200
            else:
                return jsonify({}), 400

    else:
        if opn == 'insert':
            name = req['name']
            rideId = req['rideId']
            sql = """INSERT INTO joinride (Name, Ride_ID) VALUES (%s, %s)"""
            val = (name, rideId)
            mycursor.execute(sql, val)
            mydb.commit()
            return jsonify({}), 200
        else:
            where = req['where']
            sql = "DELETE FROM " + table + " WHERE " + where + ";"
            mycursor.execute(sql)
            mydb.commit()
            if mycursor.rowcount != 0:
                return jsonify({}), 200
            else:
                return jsonify({}), 400

    return 1


if __name__ == '__main__':

    #global mydb
    #global mycursor

    #mydb = connect_to_db()
    #mycursor = mydb.cursor(buffered=True)

    # create_database()
    # create_tables()
    # mycursor.execute("SHOW TABLES")

    app.run(host="0.0.0.0",debug=True)







