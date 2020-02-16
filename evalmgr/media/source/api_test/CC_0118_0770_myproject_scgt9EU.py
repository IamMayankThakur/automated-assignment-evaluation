import json
import sqlite3
from datetime import datetime as dt

import requests
from flask import Flask, abort, jsonify, request, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rideshare.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
	__tablename__ = "users"
	id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	username = db.Column(db.String(32), index=True)
	password = db.Column(db.String(40))

	def __repr__(self): return self.username


class Ride(db.Model):
	__tablename__ = "rides"
	ride_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	created_by = db.Column(db.String(32), index=True)
	timestamp = db.Column(db.String(50))
	source = db.Column(db.String(40))
	destination = db.Column(db.String(40))


class JoinRide(db.Model):
	__tablename__ = "joinride"
	joinid = db.Column(db.Integer, autoincrement=True, primary_key=True)
	ride_id = db.Column(db.Integer, index=True)
	username = db.Column(db.String(32), index=True)


def sha(passwo):
	if len(passwo) != 40: return False
	try: sha1 = int(passwo, 16)
	except ValueError: return False
	return True


@app.route('/api/v1/db/write', methods=['POST'])
def write_to_db():
	args = request.get_json()
	op = int(args["op"])
	if op == 1:
		username = args["username"]
		password = args["password"]
		add_user = User(username=username, password=password)
		db.session.add(add_user)
		db.session.commit()
		return {}
	if op == 2:
		created_by = args["created_by"]
		timestamp = args["timestamp"]
		source = args["source"]
		destination = args["destination"]
		add_ride = Ride(created_by=created_by, timestamp=timestamp,
						source=source, destination=destination)
		db.session.add(add_ride)
		db.session.commit()
		return {}
	if op == 3:
		db.delete()
		db.session.commit()
	if op == 4:
		delete_ride.delete()
		delete_ride.session.commit()


@app.route('/api/v1/users', methods=['PUT'])
def new_user():
	args = request.get_json()
	username = args["username"]
	password = args["password"]
	user_in_db = db.session.query(User).filter(
		User.username == username).all()
	if user_in_db: return {}, 400
	check = sha(password)
	if not check: return {}, 400
	query = {"op": 1, "username": username, "password": password}
	user = requests.post(
		'http://0.0.0.0:80/api/v1/db/write', json=query)
	return {}, 201


@app.route('/api/v1/users/<string:username>', methods=['DELETE'])
def del_user(username):
	user_in_db = db.session.query(User).filter(User.username == username)
	if not user_in_db.first(): return {}, 400
	user_in_db.delete()
	user_in_db.session.commit()
	return {}, 200


@app.route('/api/v1/rides', methods=['POST'])
def create_ride():
	args = request.get_json()
	created_by = args["created_by"]
	timestamp = args["timestamp"]
	source = args["source"]
	destination = args["destination"]
	user_in_db = db.session.query(User).filter(
		User.username == created_by).first()
	if not user_in_db: return {}, 400
	else:
		if source == destination or source not in range(1, 199) or destination not in range(1, 199): return {}, 400
		query = {"op": 2, "created_by": created_by, "timestamp": timestamp,
					"source": source, "destination": destination}
		ride = requests.post(
			'http://0.0.0.0:80/api/v1/db/write', json=query)
		return {}, 201


@app.route('/api/v1/rides', methods=['GET'])
def upcoming_rides():
	args = request.args
	source = int(args['source'])
	destination = int(args['destination'])
	if source == destination or source not in range(1, 199) or destination not in range(1, 199): return {}, 400
	sd_in_db = db.session.query(Ride).filter(
		Ride.source == source).filter(Ride.destination == destination)
	if not sd_in_db.all(): return {}, 204
	d = [{"rideId": i.ride_id, "created_by": i.created_by, "timestamp": i.timestamp} for i in sd_in_db.all() if dt.strptime(i.timestamp, "%d-%m-%Y:%S-%M-%H") > dt.now()]
	return jsonify(d)


@app.route('/api/v1/rides/<int:ride_id>', methods=['GET'])
def details_ride(ride_id):
	ride_details = db.session.query(
		Ride).filter(Ride.ride_id == ride_id).first()
	if not ride_details: return {}, 400
	ride_users = db.session.query(JoinRide).filter(JoinRide.ride_id == ride_id)
	u = [i.username for i in ride_users]
	s = {"rideId": ride_id, "created_by": ride_details.created_by, "timestamp": ride_details.timestamp, "source": ride_details.source, "destination": ride_details.destination, "users": u}
	return jsonify(s), 200


@app.route('/api/v1/rides/<int:ride_id>', methods=['POST'])
def join_ride(ride_id):
	rideid_in_db = db.session.query(Ride).filter(Ride.ride_id == ride_id)
	if not rideid_in_db.all(): return {}, 400
	args = request.get_json()
	username = args["username"]
	user_in_db = db.session.query(User).filter(
		User.username == username)
	if not user_in_db.all(): return {}, 400
	user_joined = db.session.query(JoinRide).filter(
		JoinRide.username == username).filter(JoinRide.ride_id == ride_id)
	if user_joined.all(): return {}, 400
	new_user_ride = JoinRide(ride_id=ride_id, username=username)
	db.session.add(new_user_ride)
	db.session.commit()
	return {}, 200


@app.route('/api/v1/rides/<int:ride_id>', methods=['DELETE'])
def del_ride(ride_id):
	delete_ride = db.session.query(Ride).filter(Ride.ride_id == ride_id)
	if not delete_ride.all(): return {}, 400
	delete_ride.delete()
	delete_ride.session.commit()
	return {}, 200


if __name__ == "__main__":
	app.run(debug=True, port=80)
