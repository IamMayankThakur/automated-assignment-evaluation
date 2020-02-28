#!/usr/bin/env python3


import sys


from gevent import monkey
monkey.patch_all()


import requests
import flask
import pymongo
import datetime
import bson
from gevent.pywsgi import WSGIServer


app = flask.Flask(__name__)


def passwd_isValid(passwd):

    if len(passwd) != 40:
        return False

    for c in passwd.lower():
        if not c.isdigit():
            if c not in 'abcdef':
                return False

    return True

# API 1: Add user
@app.route('/api/v1/users', methods=['PUT'])
def addUser():

    '''
    c = pymongo.MongoClient()

    try:

        user = flask.request.get_json()
        username = user['username']
        password = user['password']

        exists = c.ridesharing.users.find_one({'username': username})
        if exists:
            raise ValueError('username already exists')

        if not passwd_isValid(password):
            raise ValueError('invalid password')

        c.ridesharing.users.insert_one(user)

        return flask.Response(status=201)

    except (ValueError, KeyError, TypeError) as e:
        flask.abort(flask.Response(response=str(e), status=400))

    finally:
        c.close()
    '''

    try:

        user = flask.request.get_json()
        username = user['username']
        password = user['password']

        host = flask.request.url_root + 'api/v1/db/'
        json = {
            'table': 'users',
            'where': 'username=' + username
        }

        resp = requests.post(host + 'read', json=json)
        if resp.status_code == 200:
            exists = True
        elif resp.status_code == 204:
            exists = False
        else:
            raise ValueError('bad request')

        if exists:
            raise ValueError('username already exists')

        if not passwd_isValid(password):
            raise ValueError('invalid password')

        json = {
            "operation": "insert",
            "table": "users",
            "ins_doc": user
        }

        resp = requests.post(host + 'write', json=json)

        return flask.jsonify(dict()), 201

    except (ValueError, KeyError, TypeError) as e:
        flask.abort(flask.Response(response=str(e), status=400))

    finally:
        pass


# API 2: Remove user
@app.route('/api/v1/users/<username>', methods=['DELETE'])
def delUser(username):

    '''
    c = pymongo.MongoClient()

    try:

        dels = c.ridesharing.users.delete_one({'username': username})
        n_deleted = dels.deleted_count
        if not n_deleted:
            raise ValueError('delete failed - no user deleted')

        return flask.Response(status=200)

    except (ValueError, KeyError, TypeError) as e:
        flask.abort(flask.Response(response=str(e), status=400))

    finally:
        c.close()
    '''

    try:

        host = flask.request.url_root + 'api/v1/db/'

        json = {
            'table': 'users',
            'where': 'username=' + username
        }

        resp = requests.post(host + 'read', json=json)
        if resp.status_code == 200:
            exists = True
        elif resp.status_code == 204:
            exists = False
        else:
            raise ValueError('bad request')

        if not exists:
            raise ValueError('delete failed - no user deleted')

        # delete the user
        json = {
            'operation': 'delete',
            'table': 'users',
            'where': 'username=' + username
        }

        resp = requests.post(host + 'write', json=json)
        if resp.status_code != 200:
            raise ValueError('delete failed')

        # remove the user from all the rides they are a part of
        json = {
            'operation': 'update',
            'table': 'rides',
            'update_op': {'$pull': {'users': username}}
        }

        resp = requests.post(host + 'write', json=json)
        if resp.status_code != 200:
            raise ValueError('delete failed')

        # delete all rides created by the user
        json = {
            'operation': 'delete',
            'table': 'rides',
            'where': 'created_by=' + username
        }

        resp = requests.post(host + 'write', json=json)
        if resp.status_code != 200:
            raise ValueError('delete failed')

        return flask.jsonify(dict()), 200

    except (ValueError, KeyError, TypeError) as e:
        flask.abort(flask.Response(response=str(e), status=400))

    finally:
        pass


# API 3: Create a new ride (POST)
# API 4: List all the upcoming rides for a given source and destination (GET)
@app.route('/api/v1/rides', methods=['GET', 'POST'])
def createAndListRides():

    try:

        if flask.request.method == 'GET':

            query = {
                'source': flask.request.args.get('source'),
                'destination': flask.request.args.get('destination')
            }

            host = flask.request.url_root + 'api/v1/db/'
            json = {
                'table': 'rides',
                'where': 'source=' + query['source'] + \
                         '&destination=' + query['destination']
            }

            f = open('AreaNameEnum.csv')
            data = dict()
            for line in f.readlines()[1:]:
                l, r = line.strip().split(',')
                data[l] = r
            f.close()

            source = query['source']
            dest = query['destination']
            if source not in data.keys() or \
               dest not in data.keys() or \
               source == dest:
                raise ValueError('invalid source/destination')

            resp = requests.post(host + 'read', json=json)

            if resp.status_code not in (200, 204):
                raise ValueError('database read failed')

            if resp.status_code == 204:
                return flask.Response(status=204)
            else:
                temp = resp.json()
                resp_data = [None for i in range(len(temp))]
                for i, ride_id_hex in enumerate(temp):
                    tmp_json = temp[ride_id_hex]
                    timestamp = tmp_json['timestamp']
                    accept = datetime.datetime.strptime(timestamp,
                                               '%d-%m-%Y:%S-%M-%H') \
                                            > datetime.datetime.now()
                    if accept:
                        tmp_json['rideId'] = str(int(ride_id_hex, 16))
                        tmp_json['username'] = tmp_json['created_by']
                        del tmp_json['created_by']
                        del tmp_json['source']
                        del tmp_json['destination']
                        resp_data[i] = tmp_json
                resp_data = list(filter(lambda x: x is not None,
                                        resp_data))
                return flask.jsonify(resp_data), 200


        else: # POST

            ride = flask.request.get_json()
            source = ride['source'].strip()
            dest = ride['destination'].strip()
            user = ride['created_by']
            timestamp = ride['timestamp']

            host = flask.request.url_root + 'api/v1/db/'
            json = {
                'table': 'users',
                'where': 'username=' + user
            }

            resp = requests.post(host + 'read', json=json)
            if resp.status_code == 200:
                exists = True
            elif resp.status_code == 204:
                exists = False
            else:
                raise ValueError('bad request')

            if not exists:
                raise ValueError('user does not exist')

            f = open('AreaNameEnum.csv')
            data = dict()
            for line in f.readlines()[1:]:
                l, r = line.strip().split(',')
                data[l] = r
            f.close()

            if source not in data.keys() or \
               dest not in data.keys() or \
               source == dest:
                raise ValueError('invalid source/destination')

            datetime.datetime.strptime(timestamp, '%d-%m-%Y:%S-%M-%H')

            ride['users'] = []  # users who joined (excluding creator)

            # if execution reaches here, input is valid
            json = {
                "operation": "insert",
                "table": "rides",
                "ins_doc": ride
            }

            resp = requests.post(host + 'write', json=json)

            return flask.jsonify(dict()), 201

    except (ValueError, KeyError, TypeError) as e:
        flask.abort(flask.Response(response=str(e), status=400))

    finally:
        pass


# API 5: List all the details of a given ride (GET)
# API 6: Join an existing ride (POST)
# API 7: Delete a ride (DELETE)
@app.route('/api/v1/rides/<ride_id>', methods=['GET', 'POST', 'DELETE'])
def listRideDetailsOrJoinRideOrDeleteRide(ride_id):

    try:

        if flask.request.method == 'GET':

            host = 'locahost' + 'api/v1/db/'
            host = flask.request.url_root + 'api/v1/db/'
            json = {
                'table': 'rides',
                'where': '_id=' + ride_id
            }

            resp = requests.post(host + 'read', json=json)
            if resp.status_code == 400:
                raise ValueError('database operation failed')
            resp_json = resp.json()
            rideId = list(resp_json.keys())[0]
            resp_json = resp_json[rideId]
            resp_json['rideId'] = str(int(rideId, 16))

            if resp.status_code == 200:
                return resp_json, 200

            else:
                return flask.Response(status=204)

        elif flask.request.method == 'DELETE':

            host = flask.request.url_root + 'api/v1/db/'

            json = {
                'table': 'rides',
                'where': '_id=' + ride_id
            }

            resp = requests.post(host + 'read', json=json)
            if resp.status_code == 400:
                raise ValueError('database operation failed')
            elif resp.status_code == 204:
                raise ValueError('ride not found')

            json = {
                'operation': 'delete',
                'table': 'rides',
                'where': '_id=' + ride_id
            }

            resp = requests.post(host + 'write', json=json)

            return flask.jsonify(dict()), 200

        else:  # POST

            username = flask.request.get_json()['username']

            host = flask.request.url_root + 'api/v1/db/'

            json = {
                'table': 'users',
                'where': 'username=' + username
            }

            resp = requests.post(host + 'read', json=json)
            if resp.status_code == 200:
                exists = True
            elif resp.status_code == 204:
                exists = False
            else:
                raise ValueError('bad request')

            if not exists:
                raise ValueError(400)

            json = {
                'table': 'rides',
                'where': '_id=' + ride_id
            }

            resp = requests.post(host + 'read', json=json)
            if resp.status_code == 200:
                exists = True
            elif resp.status_code == 204:
                exists = False
            else:
                raise ValueError('bad request')

            if not exists:
                raise ValueError(400)

            host = flask.request.url_root + 'api/v1/db/'
            json = {
                'operation': 'update',
                'table': 'rides',
                'where': '_id=' + ride_id,
                'update_op': {'$addToSet': {'users': username}}
            }

            resp = requests.post(host + 'write', json=json)

            return flask.jsonify(dict()), 200

    except (ValueError, KeyError, TypeError) as e:
        flask.abort(flask.Response(response=str(e), status=400))

    finally:
        pass


@app.route('/api/v1/db/write', methods=['POST'])
def DBWrite():

    '''
        _id in where must be given in integer form. Converstion to hex
            will be done in this function.
    '''

    c = pymongo.MongoClient()

    try:

        return_status = 200

        query = flask.request.get_json()
        if query is None:
            raise ValueError('no query data')
        table = query['table']
        # cols = query['cols'] # will return all columns
        if 'where' in query:
            where = query['where']
            temp = where.split('&')
            where = dict()
            for cond in temp:
                l, r = cond.split('=')
                if l != '_id':
                    where[l] = r
                else:
                    where[l] = bson.objectid.ObjectId(hex(int(r))[2:])
        else:
            where = dict()

        if 'update_op' in query:
            update_op = query['update_op']

        if table == 'users':
            collection = c.ridesharing.users
        elif table == 'rides':
            collection = c.ridesharing.rides
        else:
            raise ValueError('no collection {:s}'.format(table))

        if query['operation'].lower() == 'insert':
            if 'ins_doc' not in query:
                raise ValueError('values not given')
            collection.insert_one(query['ins_doc'])
            return_status = 201

        elif query['operation'].lower() == 'delete':
            collection.delete_many(where)

        elif query['operation'].lower() == 'update':
            collection.update_many(where, update_op)

        else:
            raise ValueError('invalid operation')

        return (flask.jsonify(dict()), return_status)

    except (ValueError, KeyError, TypeError) as e:
        flask.abort(flask.Response(response=str(e), status=400))

    finally:
        c.close()


@app.route('/api/v1/db/read', methods=['POST'])
def DBRead():

    '''
        _id in where must be given in integer form. Converstion to hex
            will be done in this function.
    '''

    c = pymongo.MongoClient()

    try:

        query = flask.request.get_json()
        if query is None:
            raise ValueError('no query data')
        table = query['table']
        # cols = query['cols'] # will return all columns
        if 'where' in query:
            where = query['where']
            temp = where.split('&')
            where = dict()
            for cond in temp:
                l, r = cond.split('=')
                if l != '_id':
                    where[l] = r
                else:
                    where[l] = bson.objectid.ObjectId(hex(int(r))[2:])
        else:
            where = dict()

        if table == 'users':
            collection = c.ridesharing.users
        elif table == 'rides':
            collection = c.ridesharing.rides
        else:
            raise ValueError('no collection {:s}'.format(table))

        temp = collection.find(where)
        db_out = dict()
        for doc in temp:
            _id = str(doc['_id'])
            del doc['_id']
            db_out[_id] = doc
        if db_out == dict():
            return (flask.jsonify(db_out), 204)

        return (flask.jsonify(db_out), 200)

    except (ValueError, KeyError, TypeError) as e:
        flask.abort(flask.Response(response=str(e), status=400))

    finally:
        c.close()


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        if sys.argv[1] in ('debug', 'deploy'):
            server_type = sys.argv[1]
        else:
            print('Usage: ./<filename> [debug|deploy]')
    else:
        server_type = 'debug'

    if server_type == 'debug':
        app.run(debug=True)
    else:
        app.debug = True
        http_server = WSGIServer(('', 5000), app)
        http_server.serve_forever()
