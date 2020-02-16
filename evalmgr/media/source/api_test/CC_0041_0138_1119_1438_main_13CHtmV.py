from flask import Flask, request, Response
from flask_sqlalchemy import SQLAlchemy
import requests as req
import json
import config
from datetime import datetime
from areas import area
import re

app = Flask(__name__)
app.config.from_object(config.Config)
db = SQLAlchemy(app)  # object to communicate with db

# 1. MODEL DEFINITIONS
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(40), nullable=False)

    def __repr__(self):
        return json.dumps({'username': self.username, 'password': self.password})

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Ride(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_by = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete='CASCADE'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    source = db.Column(db.Integer, nullable=False)
    destination = db.Column(db.Integer, nullable=False)
    # helper function to serialize Ride object

    def as_dict(self):
        obj = {}
        for c in self.__table__.columns:
            attr = getattr(self, c.name)
            if(c.name == 'created_by'):
                attr = User.query.filter_by(id=attr).first().username
            if isinstance(attr, (datetime)):
                attr = attr.strftime('%d-%m-%Y:%S:%M:%H')
            obj.update({c.name: attr})
        return obj


class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rider = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    ride = db.Column(db.Integer, db.ForeignKey(
        'ride.id', ondelete='CASCADE'), nullable=False)
    # helper function to serialize Ride object

    def as_dict(self):
        obj = {}
        for c in self.__table__.columns:
            attr = getattr(self, c.name)
            if(c.name == 'rider'):
                attr = User.query.filter_by(id=attr).first().username
            obj.update({c.name: attr})
        return obj
    # def __repr__(self):
    #     return json.dumps({'username': self.username, 'password': self.password})

# uncomment first time to create necessary db tables
db.create_all()

# 2. ALL HELPER FUNCTIONS

def resolve_area(area_num):
    try:
        return area[int(area_num)]
    except:
        return False

def validate_date(date_text):
    try:
        datetime.strptime(date_text, '%d-%m-%Y:%S:%M:%H')
        return True
    except:
        return False

def isValidHash(text):
    return re.match(r"^([0-9a-fA-F]{40})$", text)

def write_to_db(write_params):
    return req.post(
        url=app.config['URL']+'/api/v1/db/write',
        data=json.dumps(write_params),
        headers={'Content-Type': 'application/json'}
    )


def read_from_db(read_params):
    return req.post(
        url=app.config['URL']+'/api/v1/db/read',
        data=json.dumps(read_params),
        headers={'Content-Type': 'application/json'}
    )

# 3. ALL API ROUTES

# create user
@app.route('/api/v1/users', methods=['PUT'])
def create_user():
    # Get the request body
    req_data = request.get_json()
    if 'username' in req_data and 'password' in req_data and req_data['username'] != '' and req_data['password'] != '' and isValidHash(req_data['password']):
        # send a post request to write into the DB with the username and password
        write_request_body = {
            'type': 'add',
            'table': 'user',
            'data': {
                'username': req_data['username'],
                'password': req_data['password']
            }
        }
        write_request = write_to_db(write_request_body)
        response = json.loads(write_request.text)
        if write_request.status_code == 200:
            return Response(status=201)
        elif response['message'] == 'User already exists':
            return Response(status=400)
        else:
            return Response(status=500)
    else:
        return Response(status=400)

# remove user
@app.route('/api/v1/users/<username>', methods=['DELETE'])
def remove_user(username):
    if username != '':
        # send a post request to delete the user from the DB
        delete_request_body = {
            'type': 'delete',
            'table': 'user',
            'data': {'username': username}
        }
        write_request = write_to_db(delete_request_body)
        response = json.loads(write_request.text)
        if write_request.status_code == 200 or response['message'] == 'User not found':
            return Response(status=200)
        else:
            return Response(status=500)
    else:
        return Response(status=400)

# create new ride
@app.route('/api/v1/rides', methods=['POST'])
def create_ride():
    req_data = request.get_json()
    if all(keys in req_data for keys in app.config['ATTRIBUTES']['ride']) and validate_date(req_data['timestamp']) and (resolve_area(req_data['source'])) and (resolve_area(req_data['destination'])):
        # send a post request to write into the DB with the keys
        write_request_body = {
            'type': 'add',
            'table': 'ride',
            'data': {
                'created_by': req_data['created_by'],
                'timestamp': req_data['timestamp'],
                'source': req_data['source'],
                'destination': req_data['destination']
            }
        }
        write_request = write_to_db(write_request_body)
        # response = json.loads(write_request.text)
        if write_request.status_code == 200:
            return Response(status=201)
        elif write_request.status_code == 400:
            return Response(status=400)
        else:
            return Response(status=500)
    else:
        return Response(status=400)

# list all upcoming rides for a source and destination
@app.route('/api/v1/rides', methods=['GET'])
def list_rides():
    args = request.args
    if resolve_area(args['source']) and resolve_area(args['destination']):
        read_request_body = {
            'table': 'ride',
            'wheres': {
                'source': args['source'],
                'destination': args['destination']
            }
        }
        rides_request = read_from_db(read_request_body)
        rides = json.loads(rides_request.content)
        print(rides)
        if len(rides) == 0:
            return Response(status=204)
        response_data = {}
        for ride in rides:
            ride['source'] = resolve_area(ride['source'])
            ride['destination'] = resolve_area(ride['destination'])
            response_data.update({
                'rideId': ride['id'],
                'username': ride['created_by'],
                'timestamp': ride['timestamp']
            })
        return Response(json.dumps(rides), status=200, mimetype='application/json')
    else:
        message = {"success": False,
                   "message": "Please include source and destination"}
        return Response(json.dumps(message), status=400, mimetype='application/json')

# list all details of a given ride
@app.route('/api/v1/rides/<ride_id>', methods=['GET'])
def ride_details(ride_id):
    if ride_id:
        read_request_body = {
            'table': 'ride',
            'wheres': {
                'id': ride_id
            }
        }
        rides_request = read_from_db(read_request_body)
        ride_detail = json.loads(rides_request.content)
        read_request_body = {
            'table': 'trip',
            'wheres': {
                'ride': ride_id
            }
        }
        trips = json.loads(read_from_db(read_request_body).content)
        if len(trips) == 0:
            return Response(status=204)
        ride_detail[0].update({'usernames': [trip['rider'] for trip in trips]})
        ride_detail[0]['source'] = resolve_area(ride_detail[0]['source'])
        ride_detail[0]['destination'] = resolve_area(ride_detail[0]['destination'])
        return Response(json.dumps(ride_detail[0]), status=200, mimetype='application/json')
    else:
        message = {"success": False, "message": "Please include ride id"}
        return Response(json.dumps(message), status=400, mimetype='application/json')

# join an existing ride
@app.route('/api/v1/rides/<ride_id>', methods=['POST'])
def join_ride(ride_id):
    req_data = request.get_json()
    if 'username' in req_data and ride_id:
        write_request_body = {
            'type': 'add',
            'table': 'trip',
            'data': {
                'rider': req_data['username'],
                'ride': ride_id
            }
        }
        write_request = write_to_db(write_request_body)
        if write_request.status_code == 200:
            return Response(status=200)
        elif write_request.status_code == 400:
            return Response(status=400)
        else:
            return Response(status=500)
    else:
        return Response(status=400)

# delete a ride
@app.route('/api/v1/rides/<ride_id>', methods=['DELETE'])
def delete_ride(ride_id):
    if(ride_id):
        write_request_body = {
            'table': 'ride',
            'type': 'delete',
            'data': {'rideId': ride_id}
        }
        write_request = write_to_db(write_request_body)
        if write_request.status_code == 200:
            return Response(status=200)
        elif write_request.status_code == 400:
            return Response(status=400)
        else:
            return Response(status=500)
    else:
        return Response(status=400)

# write to db
@app.route('/api/v1/db/write', methods=['POST'])
def write_db():
    # Get the request body
    req_data = request.get_json()
    # Check if all the fields are present in the request body
    if 'type' not in req_data or 'table' not in req_data or 'data' not in req_data:
        message = {"success": False,
                   "message": "Please follow correct request body format"}
        return Response(json.dumps(message), status=400, mimetype='application/json')
    table_name = req_data['table']
    data = req_data['data']
    # if the operation is to be performed on the user table
    if table_name.lower() == 'user':
        # if the operation is to add to user table
        if req_data['type'] == 'add':
            # check if user already exists in the table by the username
            if not User.query.filter_by(username=data['username']).first():
                # if not already present add a new user to the table
                new_user = User(
                    username=data['username'], password=data['password'])
                db.session.add(new_user)
                db.session.commit()
                message = {"success": True,
                           "message": "User successfully added"}
                return Response(json.dumps(message), status=200, mimetype='application/json')
            else:
                message = {"success": False, "message": "User already exists"}
                return Response(json.dumps(message), status=201, mimetype='application/json')
        # if the operation is to delete a user from the table
        elif req_data['type'] == 'delete':
            user = User.query.filter_by(username=data['username']).first()
            # check if user is already present in the table
            if user:
                db.session.delete(user)
                db.session.commit()
                message = {"success": True,
                           "message": "User successfully deleted"}
                return Response(json.dumps(message), status=200, mimetype='application/json')
            else:
                message = {"success": False, "message": "User not found"}
                return Response(json.dumps(message), status=400, mimetype='application/json')
        else:
            message = {"success": False, "message": "Write type unidentified"}
            return Response(json.dumps(message), status=500, mimetype='application/json')
    elif table_name.lower() == 'ride':
        # if the operation is to add to ride table
        if req_data['type'] == 'add':
            # check if user already exists in the table by the username
            creator = User.query.filter_by(
                username=str(data['created_by'])).first()
            if creator is not None:
                timestamp = datetime.strptime(data['timestamp'], '%d-%m-%Y:%S:%M:%H')
                new_ride = Ride(created_by=creator.id, timestamp=timestamp, source=data['source'], destination=data['destination'])
                db.session.add(new_ride)
                db.session.commit()
                if(new_ride is not None):
                    new_trip = Trip(rider=creator.id, ride=new_ride.id)
                    db.session.add(new_trip)
                    db.session.commit()
                    message = {"success": True,
                               "message": "Ride successfully added"}
                    return Response(json.dumps(message), status=200, mimetype='application/json')
            else:
                message = {"success": False, "message": "User does not exist"}
                return Response(json.dumps(message), status=400, mimetype='application/json')
        # if the operation is to delete a user from the table
        elif req_data['type'] == 'delete':
            trips = Trip.query.filter_by(ride=data['rideId']).all()
            ride = Ride.query.filter_by(id=data['rideId']).first()
            if trips and ride:
                # delete all trips associated with that ride
                for trip in trips:
                    db.session.delete(trip)
                db.session.commit()
                # delete the ride itself
                db.session.delete(ride)
                db.session.commit()
                message = {"success": True,
                           "message": "Ride successfully deleted"}
                return Response(json.dumps(message), status=200, mimetype='application/json')
            else:
                message = {"success": False, "message": "Ride not found"}
                return Response(json.dumps(message), status=400, mimetype='application/json')
        else:
            message = {"success": False, "message": "Write type unidentified"}
            return Response(json.dumps(message), status=400, mimetype='application/json')
    elif table_name.lower() == 'trip':
        # if the operation is to add to ride table
        if req_data['type'] == 'add':
            rider = User.query.filter_by(username=data['rider']).first()
            ride = Ride.query.filter_by(id=data['ride']).first()
            if rider and ride:
                exists = Trip.query.filter_by(rider=rider.id, ride=ride.id).all()
                if(not exists):
                    new_trip = Trip(rider=rider.id, ride=ride.id)
                    db.session.add(new_trip)
                    db.session.commit()
                    message = {"success": True,
                               "message": "Trip successfully added"}
                    return Response(json.dumps(message), status=200, mimetype='application/json')
                else:
                    message = {"success": False}
                    return Response(json.dumps(message), status=400, mimetype='application/json')
            else:
                message = {"success": False,
                           "message": "No such ride or rider present"}
                return Response(json.dumps(message), status=400, mimetype='application/json')
    else:
        message = {"success": False,
                   "message": "No such table is present in the db"}
        return Response(json.dumps(message), status=400, mimetype='application/json')

    # FUTURE CHANGES, GENERALIZE TABLE OBJECT
    # if table_name.lower() == 'user':
    #     obj=User
    # elif table_name.lower() == 'ride':
    #     obj=Ride
    # elif table_name.lower() == 'trip':
    #     obj=Trip
    # else:
    #    message = {"success": False, "message": "No such table is present in the db"}
    #    return Response(json.dumps(message), status = 400, mimetype = 'application/json')


# read from db
@app.route('/api/v1/db/read', methods=['POST'])
def read_db():
    # send { table : table_name, wheres : {attr1:attr1, attr2:attr2, ...} }
    req_data = request.get_json()
    table_name = req_data['table'].lower()
    wheres = req_data['wheres']
    tables = {'user': User, 'ride': Ride, 'trip': Trip}
    if table_name in tables.keys():
        Table = tables[table_name]
    else:
        message = {"success": False,
                   "message": "No such table is present in the db"}
        return Response(json.dumps(message), status=400, mimetype='application/json')
    query = {}
    # build query from request
    for attr in wheres:
        if attr in app.config['ATTRIBUTES'][table_name] or attr == 'id':
            query.update({str(attr): wheres[attr]})
    result = Table.query.filter_by(**query)
    # serialize the result into python dict
    result = [i.as_dict() for i in result]
    return Response(json.dumps(result), mimetype='application/json')


if __name__ == "__main__":
    app.run(debug=True)
