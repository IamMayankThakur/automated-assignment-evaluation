from datetime import datetime
from random import random
import pandas as pd

from flask import Flask, jsonify, request, current_app, abort
from flask_restful import Api, Resource, reqparse
import flask_restful
from requests import post
from werkzeug.exceptions import HTTPException

from database import execute, fetchone, fetchall

app = Flask(__name__)
api = Api(app)

port = 4000
URL = "http://localhost:"+str(port)

def sha1(value):
    if len(value)==40:
        int(value,16)
        return value
    raise ValueError('Length is not 40')

def mydatetime(value):
    datetime.strptime(value, '%d-%m-%Y:%S-%M-%H')
    return value


class Argument(reqparse.Argument):
    def handle_validation_error(self, error, bundle_errors):
        """Called when an error is raised while parsing. Aborts the request
        with a 400 status and an error message
        :param error: the error that was raised
        :param bundle_errors: do not abort when first error occurs, return a
            dict with the name of the argument and the error message to be
            bundled
        """
        #error_str = six.text_type(error)
        #error_msg = self.help.format(error_msg=error_str) if self.help else error_str
        #msg = {self.name: error_msg}
        msg={}
        if current_app.config.get("BUNDLE_ERRORS", False) or bundle_errors:
            return error, msg
        #flask_restful.abort(400, message=msg)
        try:
            abort(400)
        except HTTPException as e:
            e.data={}
            raise
        

class RequestParser(reqparse.RequestParser):
    def parse_args(self, req=None, strict=False, http_error_code=400):
        """Parse all arguments from the provided request and return the results
        as a Namespace
        :param req: Can be used to overwrite request from Flask
        :param strict: if req includes args not in parser, throw 400 BadRequest exception
        :param http_error_code: use custom error code for `flask_restful.abort()`
        """
        if req is None:
            req = request

        namespace = self.namespace_class()

        # A record of arguments not yet parsed; as each is found
        # among self.args, it will be popped out
        req.unparsed_arguments = dict(self.argument_class('').source(req)) if strict else {}
        errors = {}
        for arg in self.args:
            value, found = arg.parse(req, self.bundle_errors)
            if isinstance(value, ValueError):
                errors.update(found)
                found = None
            if found or arg.store_missing:
                namespace[arg.dest or arg.name] = value
        if errors:
            flask_restful.abort(http_error_code, message=errors)

        if strict and req.unparsed_arguments:
            #raise exceptions.BadRequest('Unknown arguments: %s'
                                        #% ', '.join(req.unparsed_arguments.keys()))
            try:
                abort(400)
            except HTTPException as e:
                e.data={}
                raise

        return namespace


class Users(Resource):
    def __init__(self):
        self.reqparser = RequestParser()
        self.reqparser.add_argument(Argument('username', type = str, required = True))
        self.reqparser.add_argument(Argument('password', type = sha1, required = True))
        super(Users, self).__init__()

    def put(self):
        args = self.reqparser.parse_args(strict = True) #400 if extra or less fields, non sha1 password
        username = args['username']
        password = args['password']
        req = {
            'query':'insert',
            'table':'users',
            'values': {
                'username':username,
                'password':password
            }
        }
        res = post(URL+"/api/v1/db/write", json = req)
        return {}, (201 if res.status_code==200 else 400) #400 if insert fail


class User(Resource):
    def delete(self, username):
        if not request.get_json():
            req = {
                'table': 'users',
                'columns': ['username'],
                'condition': {
                    'username': username
                }
            }
            res = post(URL+"/api/v1/db/read", json = req)
            if res.json():
                req = {
                    'query': 'delete',
                    'table': 'users',
                    'condition': {
                        'username': username
                    }
                }
                post(URL+"/api/v1/db/write", json = req)
                return {}, 200
        return {}, 400 #non empty request json or username doesnt exist


class Rides(Resource):
    def post(self):
        reqparser = RequestParser()
        reqparser.add_argument(Argument('created_by', type = str, required = True))
        reqparser.add_argument(Argument('timestamp', type = mydatetime, required = True))
        reqparser.add_argument(Argument('source', type = int, required = True))
        reqparser.add_argument(Argument('destination', type = int, required = True))
        args = reqparser.parse_args(strict = True) #400 if incorrect timestamp format, any extra/less fields
        created_by = args['created_by']
        timestamp = args['timestamp']
        source = args['source']
        destination = args['destination']
        
        enum = pd.read_csv('AreaNameEnum.csv')
        if source in enum['Area No'] and destination in enum['Area No'] and source!=destination:
            req = {
                'query': 'insert',
                'table': 'rides',
                'values': {
                    'created_by': created_by,
                    'timestamp': timestamp,
                    'source': source,
                    'destination': destination
                }
            }
            res1 = post(URL+"/api/v1/db/write", json = req)
            if res1.status_code==200:
                return {}, 201
        return {}, 400 #if source/destination same or incorrect or username doesnt exist

    def get(self):
        reqparser = RequestParser()
        reqparser.add_argument(Argument('source', location='args', type = int, required = True))
        reqparser.add_argument(Argument('destination', location='args',type = int, required = True))
        args = reqparser.parse_args(strict = True)
        source = args['source']
        destination = args['destination']

        enum = pd.read_csv('AreaNameEnum.csv')
        if source in enum['Area No'] and destination in enum['Area No'] and source!=destination:
            req = {
                'table': 'rides',
                'columns': ['rideId', 'created_by', 'timestamp'],
                'condition': {
                    'source': source,
                    'destination': destination
                }
            }
            res=post(URL+"/api/v1/db/read", json = req)
            res_json=[ride for ride in res.json() if datetime.strptime(ride['timestamp'], '%d-%m-%Y:%S-%M-%H') > datetime.now()]
            for ride in res_json:
                ride['username']=ride.pop('created_by')
            return res_json, (200 if res_json else 204) #204 if no rides
        return {}, 400 #if source/destination same or incorrect


class Ride(Resource):
    def get(self, id):
        if not request.get_json():
            req = {
                'table': 'rides',
                'columns': ['rideId', 'created_by', 'timestamp', 'source', 'destination'],
                'condition': {
                    'rideId': id
                }
            }
            res = post(URL+"/api/v1/db/read", json = req)
            if res.json():
                res_json=res.json()[0]
                req = {
                    'table': 'riders',
                    'columns': ['user'],
                    'condition': {
                        'rideId': id
                    }
                }
                resr = post(URL+"/api/v1/db/read", json = req)
                res_json['users']=[i['user'] for i in resr.json()]
                return res_json, 200
            return {}, 204 #if no rides found
        return {}, 400 #if request json is not empty
        #idk 405 here

    def post(self, id):
        reqparser = RequestParser()
        reqparser.add_argument(Argument('username', type = str, required = True))
        args = reqparser.parse_args(strict = True) #400 if any extra or less fields
        username = args['username']
        req = {
            'table': 'rides',
            'columns': ['rideId'],
            'condition': {
                'rideId': id
            }
        }
        res = post(URL+"/api/v1/db/read", json = req)
        if res.json():
            req = {
                'table': 'rides',
                'columns': ['created_by'],
                'condition': {
                    'created_by': username
                }
            }
            resr = post(URL+"/api/v1/db/read", json = req)
            req = {
                'query': 'insert',
                'table': 'riders',
                'values': {
                    'rideId': id,
                    'user': username
                }
            }
            resw = post(URL+"/api/v1/db/write", json = req)
            return {}, (200 if (resw.status_code==200 and not resr.json()) else 400) #400 if user not found or user already joined ride or user is creator
        return {}, 204 #ride not found

    def delete(self, id):
        if not request.get_json():
            req = {
                'table': 'rides',
                'columns': ['rideId'],
                'condition': {
                    'rideId': id
                }
            }
            res = post(URL+"/api/v1/db/read", json = req)
            if res.json():
                req = {
                    'query': 'delete',
                    'table': 'riders',
                    'condition': {
                        'rideId': id
                    }
                }
                post(URL+"/api/v1/db/write", json = req)
                return {}, 200
        return {}, 400 #if request json not empty or ride not found


class DBWrite(Resource):
    def __init__(self):
        self.reqparser = RequestParser()
        self.reqparser.add_argument(Argument('query', type = str, required = True))
        self.reqparser.add_argument(Argument('table', type = str, required = True))
        self.reqparser.add_argument(Argument('values', type = dict))
        self.reqparser.add_argument(Argument('condition', type = dict))
        super(DBWrite, self).__init__()

    def post(self):
        args = self.reqparser.parse_args()
        query = args['query']
        table = args['table']

        if query=='insert':
            if 'values' in args:
                values = args['values']
                insert_query = '''
                    INSERT INTO ''' + table + '(' + ','.join(values.keys()) + ') ' + '''
                    VALUES ''' + '(' + ','.join(map(repr, values.values())) + ')'
                if execute(insert_query):
                    return {}, 200
            return {}, 400
        
        elif query=='delete':
            if 'condition' in args:
                condition = args['condition']
                delete_query = '''
                    DELETE FROM ''' + table + '''
                    WHERE ''' + ' AND '.join(map(lambda x, y: x+'='+repr(y), condition.keys(), condition.values()))
                execute(delete_query)
                return {}, 200
            return {}, 400


class DBRead(Resource):
    def post(self):
        args = request.get_json()
        table = args['table']
        if 'columns' in args:
            columns = args['columns']
            select_query = '''
                SELECT ''' + ','.join(columns) + '''
                FROM ''' + table + '''
                ''' + ('WHERE ' + ' AND '.join(map(lambda x, y: x+'='+repr(y), args['condition'].keys(), args['condition'].values())) if 'condition' in args else '')
            rows = fetchall(select_query)
            res = []
            if rows:
                for row in rows:
                    res.append({columns[i]: row[i] for i in range(len(columns))})
            return res, 200
        return {}, 400


api.add_resource(Users, '/api/v1/users')
api.add_resource(User, '/api/v1/users/<string:username>')
api.add_resource(Rides, '/api/v1/rides')
api.add_resource(Ride, '/api/v1/rides/<int:id>')
api.add_resource(DBWrite, '/api/v1/db/write')
api.add_resource(DBRead, '/api/v1/db/read')

if __name__ == '__main__':
	app.run(port = port)
