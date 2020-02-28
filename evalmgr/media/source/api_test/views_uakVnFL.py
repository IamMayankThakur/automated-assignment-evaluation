import datetime
import json
import re
import time

import psycopg2
import requests
from flask import Flask, Response, jsonify, request
from psycopg2 import sql

# Fill in this
POSTGRES_USER = "postgres"
POSTGRES_PASSWD = "password"

app = Flask(__name__)

# Custom error handling functions
@app.errorhandler(405)
def method_not_allowed(error):
    return Response(status=405)


# Functions implementing API routes

# Add user
@app.route('/api/v1/users', methods=['PUT'])
def add_user():
    req_data = request.get_json()
    uname = req_data.get("username")
    passwd = req_data.get("password")

    # Check for valid username and password fields
    if uname == "" or passwd == "":
        return Response(status=400)
    else:
        regex = re.compile(r'^[a-fA-F0-9]{40}$')
        # Check for valid SHA1 hash
        if regex.match(passwd):
            r = requests.post(
                "http://52.44.97.53/api/v1/db/write",
                json={
                    "insert": {
                        "uname": uname,
                        "passwd": passwd
                    },
                    "table": "users"
                })

            return Response(status=r.status_code)
        else:
            return Response(status=400)

# Remove user
@app.route('/api/v1/users/<uname>', methods=['DELETE'])
def del_user(uname):

    r1 = requests.post(
        "http://52.44.97.53/api/v1/db/read",
        json={
            "delete": 0,
            "table": "users",
            "columns": ["uname"],
            "where": ["uname='{}'".format(uname)]
        })

    if(r1.json().get("count") == 0):
        return Response(status=r1.json().get("status"))
    else:
        r2 = requests.post(
            "http://52.44.97.53/api/v1/db/read",
            json={
                "delete": 1,
                "table": "users",
                "columns": ["uname"],
                "where": ["uname='{}'".format(uname)]
            }
        )

        return Response(status=r2.status_code)

# Create a new ride
# List all upcoming rides for a given source and destination
@app.route('/api/v1/rides', methods=['POST', 'GET'])
def create_ride():
    if request.method == 'POST':
        req_data = request.get_json()

        uname = req_data.get("created_by")
        ts = req_data.get("timestamp")
        src = req_data.get("source")
        dest = req_data.get("destination")

        if uname == "" or ts == "" or src == "" or dest == "":
            return Response(status=400)
        else:

            # Check for valid timestamp format or else return status code 400
            try:
                ts = str(datetime.datetime.strptime(
                    ts, "%d-%m-%Y:%S-%M-%H"))
            except Exception:
                return Response(status=400)

            src = int(src)
            dest = int(dest)

            if src == dest:
                return Response(status=400)

            r = requests.post(
                "http://52.44.97.53/api/v1/db/write",
                json={
                    "insert": {
                        "uname": uname,
                        "rtime": ts,
                        "source": src,
                        "dest": dest
                    },
                    "table": "rides"
                })

            if (r.status_code == 400):
                return Response(status=400)
            else:
                uname_ = "'{}'".format(uname)
                rtime_ = "'{}'".format(ts)
                source_ = "'{}'".format(src)
                dest_ = "'{}'".format(dest)

                r = requests.post(
                    "http://52.44.97.53/api/v1/db/read",
                    json={
                        "delete": 0,
                        "table": "rides",
                        "columns": ["id"],
                        "where": ["uname=" + uname_ +
                                  " AND rtime=" + rtime_ +
                                  " AND source=" + source_ +
                                  " AND dest=" + dest_]
                    })

                newRideId = int(r.json().get("id")[0])

                r = requests.post(
                    "http://52.44.97.53/api/v1/db/write",
                    json={
                        "insert": {
                            "ride_id": newRideId,
                            "uname": uname
                        },
                        "table": "ride_users"
                    })

                return Response(status=201)
    elif request.method == 'GET':
        src = request.args.get("source")
        dest = request.args.get("destination")

        if src == "" or dest == "":
            return Response(status=400)
        else:

            dt_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            dt_now_str = "'{}'".format(dt_now)

            r = requests.post(
                "http://52.44.97.53/api/v1/db/read",
                json={
                    "delete": 0,
                    "table": "rides",
                    "columns": ["id", "uname", "rtime"],
                    "where": ["source=" + src + " AND dest=" + dest + " AND rtime>" + dt_now_str]
                })

            result = []
            resp = r.json()

            if type(resp.get("id")) == type([]):
                num_records = len(resp.get("id"))
                for i in range(num_records):
                    temp = dict()
                    temp["rideId"] = resp.get("id")[i]
                    temp["username"] = resp.get("uname")[i]
                    temp["timestamp"] = datetime.datetime.strptime(
                        resp.get("rtime")[i], '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y:%S-%M-%H')
                    result.append(temp)

            if result:
                return str(result)
            else:
                return Response(status=204)
    else:
        return Response(status=405)


# List all the details of a given ride
# Join an existing ride
# Delete a ride
@app.route('/api/v1/rides/<rideid>', methods=['GET', 'POST', 'DELETE'])
def manipulate_ride(rideid):
    count = 0

    rideID = "'{}'".format(str(rideid))

    r = requests.post(
        "http://52.44.97.53/api/v1/db/read",
        json={
            "delete": 0,
            "table": "rides",
            "columns": ["id"],
            "where": ["id=" + rideID]
        })

    count = int(r.json().get("count"))

    if count == 0:
        return Response(status=405)
    else:
        if request.method == 'GET':
            r1 = requests.post(
                "http://52.44.97.53/api/v1/db/read",
                json={
                    "delete": 0,
                    "table": "rides",
                    "columns": ["uname", "rtime", "source", "dest"],
                    "where": ["id=" + rideID]
                })

            r2 = requests.post(
                "http://52.44.97.53/api/v1/db/read",
                json={
                    "delete": 0,
                    "table": "ride_users",
                    "columns": ["uname"],
                    "where": ["ride_id=" + rideID]
                })

            created_user = r1.json().get("uname")
            ts = r1.json().get("rtime")
            src = r1.json().get("source")
            dst = r1.json().get("dest")

            ts = datetime.datetime.strptime(
                r1.json().get("rtime")[0], '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y:%S-%M-%H')

            all_users = r2.json().get("uname")

            usernames = []

            for i in all_users[1:]:
                usernames.append(i)

            Response(status=201)
            return jsonify(
                rideId=rideid,
                created_by=created_user[0],
                users=usernames,
                timestamp=ts,
                source=str(src[0]),
                destination=str(dst[0])
            )

        elif request.method == 'POST':
            req_data = request.get_json()
            uname = req_data.get("username")

            r2 = requests.post(
                "http://52.44.97.53/api/v1/db/write",
                json={
                    "insert": {
                        "ride_id": rideid,
                        "uname": uname
                    },
                    "table": "ride_users"
                })

            return Response(status=r2.status_code)

        elif request.method == 'DELETE':
            # Delete an existing ride
            # Deleting from ride_users done by the database
            r2 = requests.post(
                "http://52.44.97.53/api/v1/db/read",
                json={
                    "delete": 1,
                    "table": "rides",
                    "columns": [""],
                    "where": ["id=" + rideID]
                })

            return Response(status=r2.status_code)

# Write to db
@app.route('/api/v1/db/write', methods=['POST'])
def write_db():
    """
        POST request data format -
        {
            "insert" : {
                "col_name":value
                .
                .
                .
            },
            "table" : "<table_name>"
        }
    """
    req_data = request.get_json()

    table = req_data.get("table")

    insert = req_data.get("insert")
    columnNames = insert.keys()
    columnValues = insert.values()

    insertColumns = ""
    insertValues = ""

    for i in columnNames:
        insertColumns += i + ","

    for i in columnValues:
        insertValues += "'{}'".format(str(i)) + ","

    insertColumns = insertColumns[0:-1]
    insertValues = insertValues[0:-1]

    try:
        connection = psycopg2.connect(user=POSTGRES_USER,
                                      password=POSTGRES_PASSWD,
                                      host="127.0.0.1",
                                      port="5432",
                                      database="rideshare")

        cursor = connection.cursor()

        # Perform SQL validation to prevent SQL injection
        query = sql.SQL("INSERT" +
                        " INTO " + table + "(" + insertColumns + ")" +
                        " VALUES " + "(" + insertValues + ");"
                        )

        cursor.execute(query.as_string(connection))
        connection.commit()
        count = cursor.rowcount

        if count != 0:
            result = {}
            result["status"] = 201
            return json.dumps(result)
        else:
            result = {}
            result["status"] = 201
            return json.dump(result)

    except Exception as err:
        print(err)
        return Response(status=400)
    finally:
        if connection:
            cursor.close()
            connection.close()

    return Response(status=201)


# Read from db
@app.route('/api/v1/db/read', methods=['POST'])
def read_db():
    """
        POST request data format -
        {
            "delete" : 1 or 0,
            "table" : "<table_name>",
            "columns" : ["<col_name>", ],
            "where" : "["<col_name='value'>",]
        }
    """

    req_data = request.get_json()

    delete = req_data.get("delete")

    if delete == 0:

        table = req_data.get("table")
        columns = req_data.get("columns")
        where = req_data.get("where")

        select_clause = ""
        for i in columns:
            select_clause += i + ","

        where_clause = ""
        for i in where:
            where_clause += i + " AND "

        select_clause = select_clause[0:-1]
        where_clause = where_clause[0:-5]

        count = 0
        try:
            connection = psycopg2.connect(user=POSTGRES_USER,
                                          password=POSTGRES_PASSWD,
                                          host="127.0.0.1",
                                          port="5432",
                                          database="rideshare")

            cursor = connection.cursor()

            query = sql.SQL("SELECT " + select_clause
                            + " FROM " + table
                            + " WHERE " + where_clause + ";"
                            )

            cursor.execute(query.as_string(connection))

            count = cursor.rowcount

            if count != 0:
                """
                    The query result is non empty. 
                    Create a dictionary with key = <column_name> and
                    corresponding value is an array of values returned
                    by the query for that column.
                    Return a json response along with the dictionary and the count.                    
                """
                reqNumberOfColumns = len(columns)

                # Maps every required column to its index from the query result
                colNameIndexMap = {}
                column = 0
                for d in cursor.description:
                    colNameIndexMap[d[0]] = column
                    column = column + 1

                result = {}
                result["count"] = count
                result["status"] = 200

                # Add column name : [values, ] to the dictionary for every required column
                for i in range(count):
                    row = cursor.fetchone()
                    if i == 0:
                        for j in range(reqNumberOfColumns):
                            result[columns[j]] = [
                                row[colNameIndexMap[columns[j]]]]
                    else:
                        for j in range(reqNumberOfColumns):
                            result[columns[j]].append(
                                row[colNameIndexMap[columns[j]]])

                cursor.close()
                return json.dumps(result, default=str)
            else:
                result = {}
                result["count"] = 0
                result["status"] = 400
                return json.dumps(result)

        except Exception as err:
            print(err)
            return Response(status=400)
        finally:
            if connection:
                cursor.close()
                connection.close()
            else:
                return Response(status=400)
    else:
        try:
            connection = psycopg2.connect(user=POSTGRES_USER,
                                          password=POSTGRES_PASSWD,
                                          host="127.0.0.1",
                                          port="5432",
                                          database="rideshare")

            cursor = connection.cursor()

            table = req_data.get("table")
            where = req_data.get("where")

            where_clause = ""
            for i in where:
                where_clause += i + " AND "

            where_clause = where_clause[0:-5]

            query = sql.SQL("DELETE "
                            + " FROM " + table
                            + " WHERE " + where_clause + ";"
                            )

            cursor.execute(query.as_string(connection))
            connection.commit()
            count = cursor.rowcount

            return Response(status=200)

        except Exception:
            return Response(status=400)
        finally:
            if connection:
                cursor.close()
                connection.close()
            else:
                return Response(status=400)


if __name__ == '__main__':
    app.run()