import sqlite3
from flask import Flask, render_template, jsonify, request, abort, url_for, Response
from flask_restful import Resource, Api
import json

import requests

from datetime import datetime

import csv


'''
con.execute("PRAGMA foreign_keys = 1") right after the connect statement 
take care of foreign keys 
'''


app = Flask(__name__)
api = Api(app)


def convertTime(timestamp):
    return datetime.strptime(timestamp, "%d-%m-%Y:%S-%M-%H")


def check_area_num(num):
    s_num = str(num)
    csvfile = open('AreaNameEnum.csv')
    readCSV = csv.reader(csvfile, delimiter=',')
    # print(readCSV)
    for row in readCSV:
        # print(row)
        if s_num == row[0]:
            csvfile.close()
            return True
        # print(row[0])
        # print(row[0],row[1],row[2],)
    csvfile.close()
    return False


def is_hex(s):
    try:
        int(s, 16)
        return True
    except ValueError:
        return False


class Dummy(Resource):
    def get(self):
        return Response('Hello World', status = 200, mimetype='application/jsons')


class DatabaseWrite(Resource):

    def post(self):
        print("START WRITE TO DB")

        jobj = request.get_json()
        print(jobj)
        temp = json.loads(jobj)
        print('CHECKPOINT1')
        # print(obj)
        try:
                # table = 'users'
            print('CHECKPOINT2')

            # data = request.json['data']
            # table = request.json['table']
            data = temp['data']
            table = temp['table']
            method = temp['method']
            print(method, data, table)
            print('CHECKPOINT3')

        except:
            return Response('{}', status=400, mimetype='application/json')

        print('CHECKPOINT4')

        if table == 'users':
            if method == 'PUT':
                username = data['username']
                password = data['password']
                print(table, username, password)
                try:
                    # msg = 'checkpoint2'
                    print('checkpoint5')
                    with sqlite3.connect("database.db") as con:
                        con.execute("PRAGMA foreign_keys = 1")
                        # msg = 'checkpoint3'
                        print('checkpoint6')

                        cur = con.cursor()
                        print('checkpoint7')

                        # msg = 'checkpoint4'
                        cur.execute("INSERT INTO "+table+" (username, password) \
                            VALUES (?,?)", (username, password))
                        # msg = 'checkpoint5'
                        print('checkpoint8')

                        con.commit()
                        print('checkpoint9')

                        # msg = 'checkpoint6'
                        code = 201

                except:
                    try:
                        con.rollback()
                    except:
                        pass
                    code = 400

                finally:
                    try:
                        con.close()
                    except:
                        pass
                    return Response('{}', status=code, mimetype='application/json')

            elif method == 'DELETE':
                username = data['username']
                print(username)
                try:
                    print('checkpoint5')
                    with sqlite3.connect("database.db") as con:
                        con.execute("PRAGMA foreign_keys = 1")
                        print('checkpoint6')

                        cur = con.cursor()
                        print('checkpoint7')

                        jdict = {
                            "table": "users",
                            "columns": ["username"],
                            "where": " username = '" + username + "'"
                        }

                        jobject = json.dumps(jdict)
                        response = requests.post(
                            'http://127.0.0.1:5000/api/v1/db/read', json=jobject)
                        # ret = response.json()
                        code = response.status_code

                        # if len(ret['rows']):
                        if code == 200:
                            command = "DELETE FROM "+table+" WHERE username = '" + username + "'"
                            # cur.execute("DELETE FROM "+table+" WHERE username = " + username)
                            print(command)
                            cur.execute(command)

                            # print("CHECKPOINT7.1")
                            # temp = cur.fetchall()
                            # print(temp)
                            print('checkpoint8')

                            # con.commit()
                            # print('checkpoint9')

                            jdict = {
                                "table": "rides",
                                "columns": ["ride_id", "users"],
                                "where": ""
                            }

                            jobject = json.dumps(jdict)
                            response = requests.post(
                                'http://127.0.0.1:5000/api/v1/db/read', json=jobject)
                            ret = response.json()
                            temp_code = response.status_code

                            if temp_code == 200:

                                # print('Gonna Remove from rides')
                                # print(username)
                                for i in range(len(ret['rows'])):
                                    # print(i)
                                    temp = ret['rows'][i][1].split(',')
                                    # print(temp)
                                    try:
                                        temp.remove(username)
                                        # print('removed')
                                    except:
                                        pass
                                    ret['rows'][i][1] = ','.join(temp)

                                # print('INTERLUDE')
                                for rec in ret['rows']:
                                    # print(rec)
                                    command = "UPDATE rides SET users ='" + \
                                        rec[1] + "' WHERE ride_id = " + \
                                        str(rec[0])
                                    print(command)
                                    cur.execute(command)

                            con.commit()
                            print('checkpoint9')

                            # msg = 'checkpoint6'
                            code = 200
                        else:
                            code = 400

                except:
                    try:
                        con.rollback()
                    except:
                        pass
                    code = 400

                finally:
                    try:
                        con.close()
                    except:
                        pass
                    return Response('{}', status=code, mimetype='application/json')

        elif table == 'rides':
            if method == 'POST':
                if('ride_id' in data.keys()):
                    ride_id = data['ride_id']
                    jdict = {
                        "table": "rides",
                        "columns": ["ride_id"],
                        "where": " ride_id = " + str(ride_id)
                    }

                    jobject = json.dumps(jdict)
                    response = requests.post(
                        'http://127.0.0.1:5000/api/v1/db/read', json=jobject)
                    # ret = response.json()
                    code = response.status_code
                    if(code == 204 or code != 200):
                        return Response('{}', status=code, mimetype='application/json')
                    else:
                        users = data['users']
                        print(users)
                        command = "UPDATE rides SET users ='" + \
                            users + "' WHERE ride_id = "+str(ride_id)
                        with sqlite3.connect("database.db") as con:
                            try:
                                con.execute("PRAGMA foreign_keys = 1")
                                print('checkpoint6')

                                cur = con.cursor()
                                print('checkpoint7')
                                cur.execute(command)
                                print("executed")
                                con.commit()
                                code = 200
                            except:
                                con.rollback()
                                print("write - after rollback exception")
                                code = 400
                            # y:
                            #     con.close()
                            # except:
                            #     pass
                            print(code)
                            print("OUR FLAG")
                            return Response('{}', status=code, mimetype='application/json')

                else:
                    created_by = data['created_by']
                    timestamp = data['timestamp']
                    source = data['source']
                    destination = data['destination']
                    users = data['users']

                    f = open('ride_id.txt', 'r+')
                    # id = int(f.read())
                    s = f.readline()
                    print(int(s))
                    s = int(s)
                    # l = list(s)
                    # l = str(l)
                    # # l = int(l)
                    # print(type(l))

                    # s = int(float(s))
                    ride_id = s
                    s += 1
                    f.truncate(0)
                    f.seek(0)
                    f.write(str(s))
                    f.close()

                    # print(ride_id, type(ride_id))
                    # print(created_by, type(created_by))
                    # print(timestamp, type(timestamp))
                    # print(source, type(source))
                    # print(destination, type(destination))
                    # print(users, type(users))

                    try:
                        print('checkpoint5')
                        with sqlite3.connect("database.db") as con:
                            con.execute("PRAGMA foreign_keys = 1")
                            print('checkpoint6')

                            cur = con.cursor()
                            print('checkpoint7')

                            cur.execute("INSERT INTO "+table+" (ride_id, created_by, timestamp, source, destination, users) \
                                VALUES (?,?,?,?,?,?)", (ride_id, created_by, timestamp, source, destination, users))
                            # cur.execute("DELETE FROM "+table+" WHERE username = " + username)
                            # print(command)
                            # cur.execute(command)

                            print('checkpoint8')

                            con.commit()
                            print('checkpoint9')

                            # msg = 'checkpoint6'
                            code = 201

                    except:
                        try:
                            con.rollback()
                        except:
                            pass
                        code = 400

                    finally:
                        try:
                            con.close()
                        except:
                            pass
                        return Response('{}', status=code, mimetype='application/json')

            elif method == 'DELETE':
                ride_id = data['ride_id']
                print(ride_id)
                try:
                    print('checkpoint5')
                    with sqlite3.connect("database.db") as con:
                        con.execute("PRAGMA foreign_keys = 1")
                        print('checkpoint6')

                        cur = con.cursor()
                        print('checkpoint7')

                        jdict = {
                            "table": "rides",
                            "columns": ["ride_id"],
                            "where": " ride_id = " + str(ride_id)
                        }

                        jobject = json.dumps(jdict)
                        response = requests.post(
                            'http://127.0.0.1:5000/api/v1/db/read', json=jobject)
                        ret = response.json()
                        code = response.status_code

                        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

                        # print(len(ret['rows']))
                        # if len(ret['rows']):
                        if code == 200:
                            command = "DELETE FROM "+table + \
                                " WHERE ride_id = " + str(ride_id)
                            # cur.execute("DELETE FROM "+table+" WHERE username = " + username)
                            print(command)
                            cur.execute(command)

                            print("CHECKPOINT7.1")
                            temp = cur.fetchall()
                            print(temp)
                            print('checkpoint8')

                            con.commit()
                            print('checkpoint9')

                            # msg = 'checkpoint6'
                            code = 200
                        else:
                            code = 400

                except:
                    try:
                        con.rollback()
                    except:
                        pass
                    code = 400

                finally:
                    try:
                        con.close()
                    except:
                        pass
                    return Response('{}', status=code, mimetype='application/json')


class DatabaseRead(Resource):
    def post(self):
        ret = ''
        print("START READ FROM DB")

        jobj = request.get_json()
        print(jobj)
        # print(jobj['table'])
        # temp = jobj #use this if you're calling this API directly in postman

        # use this if you're calling this API from aome other API
        temp = json.loads(jobj)
        print('CHECKPOINT1')

        try:
                # table = 'users'
            print('CHECKPOINT2')

            # data = request.json['data']
            # table = request.json['table']
            table = temp['table']
            print('CHECKPOINT2.1')

            columns = temp['columns']
            print('CHECKPOINT2.2')

            # where = []
            # if temp['where'] != "":
            where = temp['where']
            # method = temp['method']
            # print(method, data, table)
            print('CHECKPOINT3')

        except:
            return Response('{}', status=400, mimetype='application/json')

        print('CHECKPOINT4')

        command = 'SELECT ' + ', '.join(columns) + ' FROM ' + table
        if len(where):
            command = command + ' WHERE ' + where

        try:
            print('checkpoint5')
            with sqlite3.connect("database.db") as con:
                con.execute("PRAGMA foreign_keys = 1")
                print('checkpoint6')

                cur = con.cursor()
                print('checkpoint7')
                print(command)
                cur.execute(command)
                print('checkpoint8')

                rows = cur.fetchall()
                print(rows)
                # print('gonna print')
                # for row in rows:

                #     print(row)
                # print('done with print')

                if not len(rows):
                    print("I SHOULD BE PRINTED")
                    code = 204
                    ret = ''
                else:
                    ret = {
                        "rows": rows
                    }
                    code = 200

                    ret = json.dumps(ret)

                    # msg = 'checkpoint6'
                con.commit()
                print('checkpoint9')
        except:
            print("i'm in the except")
            try:
                con.rollback()
            except:
                pass
            code = 400

        finally:
            print(code)
            try:
                con.close()
            except:
                pass
            return Response(ret, status=code, mimetype='application/json')


class Users(Resource):
    def put(self):
        print("START PUT USERS")
        try:
            username = request.json['username']
            password = request.json['password']
        except:
            return Response('{}', status=400, mimetype='application/json')

        if not is_hex(password) or len(password) != 40:
            return Response('{}', status=400, mimetype='application/json')

        table = 'users'

        jdict = {
            "method": "PUT",
            "data": {
                "username": username,
                "password": password
            },
            "table": table
        }

        jobject = json.dumps(jdict)
        print('GONNA REDIRECT')
        # response = redirect(url_for('write_to_db'), code=307)
        # a = Database()
        # a.post(jobject)

        # return response\

        response = requests.post(
            'http://127.0.0.1:5000/api/v1/db/write', json=jobject)
        code = response.status_code
        return Response('{}', status=code, mimetype='application/json')

    def delete(self, username):
        print("USERNAME")
        print(username)

        if username == '':
            # code = 400
            return Response('{}', status=400, mimetype='application/json')
        else:
            table = "users"
            jdict = {
                "method": "DELETE",
                "data": {
                    "username": username,
                },
                "table": table
            }

            jobject = json.dumps(jdict)
            response = requests.post(
                'http://127.0.0.1:5000/api/v1/db/write', json=jobject)
            code = response.status_code

        return Response('{}', status=code, mimetype='application/json')


class Rides(Resource):
    def delete(self, ride_id):
        print("RIDE_ID")
        print(ride_id)

        if ride_id == '':
            code = 400
        else:
            table = "rides"
            jdict = {
                "method": "DELETE",
                "data": {
                    "ride_id": ride_id,
                },
                "table": table
            }

            jobject = json.dumps(jdict)
            response = requests.post(
                'http://127.0.0.1:5000/api/v1/db/write', json=jobject)
            code = response.status_code

        return Response('{}', status=code, mimetype='application/json')

    def get(self, ride_id=''):

        if(ride_id):
            jdict = {
                "table": "rides",
                "columns": ["ride_id", "created_by", "users", "timestamp", "source", "destination"],
                "where": " ride_id = " + str(ride_id)
            }
            jobject = json.dumps(jdict)
            response = requests.post(
                'http://127.0.0.1:5000/api/v1/db/read', json=jobject)
            code = response.status_code

            # if not len(ret['rows']):
            if code == 204:
                # code = 204
                final_ret_jobject = '{}'
            else:
                ret = response.json()

                ret_ride_id = ret['rows'][0][0]
                ret_created_by = ret['rows'][0][1]
                ret_users = ret['rows'][0][2]
                ret_timestamp = ret['rows'][0][3]
                ret_source = ret['rows'][0][4]
                ret_destination = ret['rows'][0][5]

                final_ret = {
                    "ride_id": ret_ride_id,
                    "Created_by": ret_created_by,
                    "users": ret_users,
                    "timestamp": ret_timestamp,
                    "source": ret_source,
                    "destination": ret_destination
                }

                final_ret_jobject = json.dumps(final_ret)
        else:
            try:
                source = request.args.get('source')
                destination = request.args.get('destination')
            except:
                print('FIRST 400')
                return Response('', status=400, mimetype='application/json')
            try:
                source = int(source)
                destination = int(destination)
                jdict = {
                    "table": "rides",
                    "columns": ["ride_id", "created_by", "timestamp"],
                    "where": " source = " + str(source) + " AND destination = " + str(destination)
                }
                jobject = json.dumps(jdict)
                response = requests.post(
                    'http://127.0.0.1:5000/api/v1/db/read', json=jobject)
                # ret = response.json()
                print('CHK1')
                code = response.status_code
                print('CHK1')

                if code == 200:
                    ret = response.json()
                    print('CHK2')

                    ret_list = ret['rows']
                    print(ret_list)
                    print('CHK3')

                    time_now = datetime.now()
                    print('CHK4')
                    final_ret = []
                    for i in ret_list:

                        ride_id = i[0]
                        username = i[1]
                        timestamp = i[2]
                        temp = convertTime(timestamp)
                        if temp > time_now:
                            d = {
                                "ride_id": ride_id,
                                "username": username,
                                "timestamp": timestamp
                            }
                            final_ret.append(d)
                            # print("appened")
                    print('CHK5')

                    code = 200
                else:
                    print('GONE TO 204')
                    final_ret = ''
                    code == 204
                # jdict = final_list
            except:
                print('SECOND 400')
                code = 400
                final_ret = ''

            print(final_ret)
            final_ret_jobject = jsonify(final_ret)
            print(final_ret_jobject)
            # final_ret_jobject = final_ret
        return Response(final_ret_jobject, status=code, mimetype='application/json')

    def post(self, ride_id=''):
        if ride_id != '':
            try:
                username = request.json['username']
                print(username)
            except:
                print("first exception")
                return Response('{}', status=400, mimetype='application/json')

            if username == '':
                print("second exception")
                return Response('{}', status=400, mimetype='application/json')

            jdict0 = {
                "table": "users",
                "columns": ["username"],
                "where": " username = '" + username + "'"
            }

            jobject = json.dumps(jdict0)
            response = requests.post(
                'http://127.0.0.1:5000/api/v1/db/read', json=jobject)
            # ret = response.json()
            code = response.status_code

            # if not len(ret['rows']):
            if code == 204 or code != 200:
                return Response('{}', status=400, mimetype='application/json')

            jdict1 = {
                "table": "rides",
                # "columns": ["ride_id", "created_by", "users", "timestamp", "source", "destination"],
                "columns": ["ride_id", "created_by", "users", "timestamp"],
                "where": " ride_id = " + str(ride_id)
            }
            jobject = json.dumps(jdict1)
            response = requests.post(
                'http://127.0.0.1:5000/api/v1/db/read', json=jobject)
            code = response.status_code

            # if not len(ret['rows']):
            if code == 204:
                return Response('{}', status=400, mimetype='application/json')
            # else:
            ret = response.json()

            ride_id = ret['rows'][0][0]
            created_by = ret['rows'][0][1]
            users = ret['rows'][0][2]
            users = users.split(',')
            timestamp = ret['rows'][0][3]

            if username == created_by:
                return Response('{}', status=400, mimetype='application/json')

            if convertTime(timestamp) < datetime.now():
                return Response('{}', status=400, mimetype='application/json')

            if username in users:
                return Response('{}', status=400, mimetype='application/json')

            users.append(username)
            try:
                users.remove('')
            except:
                pass
            users = ','.join(users)

            table = "rides"

            jdict2 = {
                "method": "POST",
                "data": {
                    "ride_id": ride_id,
                    "users": users,
                },
                "table": table
            }

            jobject = json.dumps(jdict2)
            response = requests.post(
                'http://127.0.0.1:5000/api/v1/db/write', json=jobject)
            code = response.status_code

            return Response('{}', status=code, mimetype='application/json')

        else:
            try:
                created_by = request.json['created_by']
                timestamp = request.json['timestamp']
                source = request.json['source']
                destination = request.json['destination']

            except:
                return Response('{}', status=400, mimetype='application/json')

            if created_by == '' or timestamp == '' or check_area_num(source) == False or check_area_num(destination) == False:
                return Response('{}', status=400, mimetype='application/json')

            if convertTime(timestamp) < datetime.now():
                return Response('{}', status=400, mimetype='application/json')

            table = "rides"
            jdict = {
                "method": "POST",
                "data": {
                    "created_by": created_by,
                    "timestamp": timestamp,
                    "source": source,
                    "destination": destination,
                    "users": ""
                },
                "table": table
            }

            jobject = json.dumps(jdict)
            response = requests.post(
                'http://127.0.0.1:5000/api/v1/db/write', json=jobject)
            code = response.status_code

            return Response('{}', status=code, mimetype='application/json')


api.add_resource(Users,
                 '/api/v1/users',
                 '/api/v1/users/<string:username>')

api.add_resource(Rides, '/api/v1/rides',
                        '/api/v1/rides/<int:ride_id>')

api.add_resource(DatabaseWrite, '/api/v1/db/write')

api.add_resource(DatabaseRead, '/api/v1/db/read')

api.add_resource(Dummy,'/')


#if __name__ == '__main__':
 #   app.run(debug=True)