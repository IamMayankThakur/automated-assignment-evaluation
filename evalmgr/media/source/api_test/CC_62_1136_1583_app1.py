from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
import requests
import json
from areas import Areas
import datetime

application = Flask(__name__)
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///testing.db'
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(application)


class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True, nullable=False)
	password = db.Column(db.String(80), nullable=False)

	def __repr__(self):
		return f'{self.username}'


class Ride(db.Model):
	rideId = db.Column(db.Integer, primary_key=True)
	created_by = db.Column(db.String(80), nullable=False)
	timestamp = db.Column(db.DateTime, nullable=False)
	source = db.Column(db.Integer, nullable=False)
	destination = db.Column(db.Integer, nullable=False)


class RideUsers(db.Model):
	Id = db.Column(db.Integer, primary_key=True)
	rideId = db.Column(db.Integer, unique=False)
	username = db.Column(db.String(80), nullable=False)


ADDR = "http://127.0.0.1"
PORT = ":8000"
WRADR = f'{ADDR}{PORT}/api/v1/db/write'
RADR = f'{ADDR}{PORT}/api/v1/db/read'
headers = {"Content-Type": "application/json"}


def is_hex(s):
	try: int(s, 16)
	except: return False
	return True


@application.route("/api/v1/db/write", methods=["POST"])
def write_to_db():
	operation = request.get_json()["operation"]
	if operation == 1:
		uname = request.get_json()["username"]
		passwd = request.get_json()["password"]
		new_user = User(username=uname, password=passwd)
		db.session.add(new_user)
	elif operation == 2:
		# send this request only if you know that the user already exists
		uname = request.get_json()["username"]
		remove_this_user = User.query.filter_by(username=uname).first()
		db.session.delete(remove_this_user)
	elif operation == 3:
		created_by = request.get_json()["created_by"]
		timestamp = request.get_json()["timestamp"]
		timestamp = datetime.datetime.strptime(timestamp, "%d-%m-%Y:%S-%M-%H")
		src = request.get_json()["source"]
		dst = request.get_json()["destination"]
		new_ride = Ride(created_by=created_by,
                  timestamp=timestamp, source=src, destination=dst)
		db.session.add(new_ride)

		# ride = Ride.query.filter_by(source=src,destination=dst,timestamp=timestamp).first()
		# ride_users=RideUsers(rideId=ride.rideId, username=created_by)

		# db.session.add(ride_users)

	elif operation == 6:
		rideid = request.get_json()["rideId"]
		uname = request.get_json()["username"]
		usr = User.query.filter_by(username=uname).first()
		ride = Ride.query.filter_by(rideId=rideid).first()
		if not usr or not ride:
			return jsonify({"Error": "user or ride or both do not exist"})
		new_entry = RideUsers(rideId=ride.rideId, username=usr.username)
		db.session.add(new_entry)

	elif operation == 7:
		rideid = request.get_json()["rideId"]
		ride = Ride.query.filter_by(rideId=rideid).first()
		if not ride:
			return jsonify({"Error": "ride does not exist"})
		entries_from_RideUsers = RideUsers.query.filter_by(rideId=rideid).all()
		for entry in entries_from_RideUsers:
			db.session.delete(entry)
		db.session.delete(ride)
	db.session.commit()
	return jsonify({"Error": ""})


@application.route("/api/v1/db/read", methods=["POST"])
def read_from_db():
	operation = request.get_json()["operation"]
	if operation == 1 or operation == 2 or operation == 3:
		uname = request.get_json()["username"]
		if not User.query.filter_by(username=uname).first():
			return jsonify({"Error": "user does not exist"})
		return jsonify({"Error": ""})
	elif operation == 4:
		src = request.get_json()["source"]
		dst = request.get_json()["destination"]
		src_exist = Ride.query.filter_by(source=src).first()
		dst_exist = Ride.query.filter_by(source=src).first()
		if not src_exist or not dst_exist:
			return jsonify({"Error": "source or destination or both do not exist"})
		current_time = datetime.datetime.now().replace(microsecond=0)
		#print("*************** abc",current_time)
		current_time = datetime.datetime.strftime(
			current_time, "%d-%m-%Y:%S-%M-%H")
		#print("*************** pqr",current_time)
		ctime = datetime.datetime.strptime(current_time, "%d-%m-%Y:%S-%M-%H")
		# print("***************",ctime)
		rides = Ride.query.filter_by(source=src, destination=dst).filter(
			Ride.timestamp > ctime).all()
		rides_list = [{"rideId": ride.rideId, "created_by": ride.created_by,
                 "timestamp": ride.timestamp} for ride in rides]
		return jsonify({"Error": "", "rideList": rides_list})
	elif operation == 5:
		rideid = request.get_json()["rideId"]
		ride = Ride.query.filter_by(rideId=rideid).first()
		if not ride:
			return jsonify({"Error": "rideId does not exist"})
		ts = datetime.datetime.strftime(ride.timestamp, "%d-%m-%Y:%S-%M-%H")
		user_list = [entry.username for entry in RideUsers.query.filter_by(
			rideId=rideid).all()]
		ride_details = {"created_by": ride.created_by, "source": ride.source, "destination": ride.destination,
                  "timestamp": ts, "users": user_list}
		return jsonify({"Error": "", "ride_details": ride_details})

	return jsonify({"Error": ""})


@application.route("/api/v1/users", methods=["PUT"])
def add_a_user():
	uname = request.get_json()["username"]

	check = requests.post(
		url=RADR, json={"operation": 1, "username": uname}, headers=headers)
	c_json = check.json()
	if c_json["Error"] == "user does not exist":
		passwrd = request.get_json()["password"]
		if len(passwrd) == 40 and is_hex(passwrd):
			data = {"operation": 1, "username": uname, "password": passwrd}
			resp = requests.post(url=WRADR, json=data, headers=headers)
			r_json = resp.json()
			if r_json["Error"] == "":
				# No Errors, 200 OK
				return {}, 201
			else: return {}, 400
		else:
			# if length of password < 40 or it is not in hex or both
			# Bad Request
			return {}, 400
	else:
		return {}, 400


@application.route("/api/v1/rides/<rideid>", methods=["DELETE"])
def delete_a_ride(rideid):
	rideid = int(rideid)
	data = {"operation": 7, "rideId": rideid}
	resp = requests.post(url=WRADR, json=data, headers=headers)
	r_json = resp.json()
	if r_json["Error"] == "ride does not exist":
		return {}, 400
	else:
		return {}, 200


@application.route("/api/v1/users/<username>", methods=["DELETE"])
def delete_a_user(username):
	data = {"operation": 2, "username": username}
	check = requests.post(url=RADR, json=data, headers=headers)
	c_json = check.json()

	if c_json["Error"] == "user does not exist":
		# no user, bad request
		return {}, 400
	else:
		resp = requests.post(url=WRADR, json=data, headers=headers)
		if resp.json()["Error"] == "":
			# delete successful
			return {}, 200


@application.route("/api/v1/rides", methods=["POST"])
def add_a_ride():
	#ts = datetime.datetime.now().timestamp().replace(microsecond=0)
	#newts=datetime.datetime.strptime(tt, "%Y-%m-%d %H:%M:%S").strftime('%d-%m-%Y %S:%M:%H')
	# print(newts)
	created_by = request.get_json()["created_by"]
	source = request.get_json()["source"]
	destination = request.get_json()["destination"]
	timestamp = request.get_json()["timestamp"]

	user_data = {"operation": 3, "username": created_by}
	areas_list = list(map(str, Areas))
	check = requests.post(url=RADR, json=user_data, headers=headers)
	c_json = check.json()

	if c_json["Error"] == "user does not exist":
		# no user, bad request
		return {}, 400
	else:

		if str(Areas(source)) in areas_list and str(Areas(destination)) in areas_list:
			data = {"operation": 3, "created_by": created_by, "source": source,
					"destination": destination, "timestamp": timestamp}
			resp = requests.post(url=WRADR, json=data, headers=headers)
			r_json = resp.json()
			if r_json["Error"] == "":
				return {}, 201
		else:
			return {}, 400


@application.route("/api/v1/rides/<rideid>", methods=["GET"])
def get_ride_details(rideid):
	rideid = int(rideid)
	data = {"operation": 5, "rideId": rideid}
	resp = requests.post(url=RADR, json=data, headers=headers)
	err = resp.json()["Error"]
	if err == "rideId does not exist":
		return {}, 204
	else:
		return resp.json()["ride_details"], 200


@application.route("/api/v1/rides/<rideid>", methods=["POST"])
def join_a_ride(rideid):
	rideid = int(rideid)
	uname = request.get_json()["username"]
	data = {"operation": 6, "username": uname, "rideId": rideid}

	resp = requests.post(url=WRADR, json=data, headers=headers)
	err = resp.json()["Error"]
	if err == "user or ride or both do not exist":
		# no content available for the given pair of rideId and username
		return {}, 204
	else:
		# all OK
		return {}, 200


@application.route("/api/v1/rides", methods=["GET"])
def upcoming_rides():
	src = request.args.get("source")
	dst = request.args.get("destination")
	if src is None or dst is None:
		return {}, 400

	data = {"operation": 4, "source": src, "destination": dst}
	resp = requests.post(url=RADR, json=data, headers=headers)
	r_json = resp.json()
	err = r_json["Error"]
	ride_list = r_json["rideList"]
	if ride_list == []:
		return {}, 204
	# details
	else:
		return jsonify(ride_list), 200

@application.route("/")
def index():
	return jsonify("<h4>Hello World</h4>")


if __name__ == "__main__":
	db.drop_all()
	db.create_all()
	application.run(port=int(PORT[1:]))
