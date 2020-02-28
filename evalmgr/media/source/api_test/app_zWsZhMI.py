from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy import text
from datetime import datetime
import os
from flask_api import status
import csv
import sqlalchemy as db

#Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
#Database
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
#Init DB
db = SQLAlchemy(app)
#Init MA
ma = Marshmallow(app)
a_no=[]
a_nam=[]
with open('AreaNameEnum.csv','rt')as f:
	a = csv.reader(f)
	head=next(a)
	for row in a:
		a_no.append(row[0])
		a_nam.append(row[1])
#print(a_no)
#print(a_nam)

class user(db.Model):
	__tablename__="user"
	username=db.Column(db.String(30),primary_key=True)
	password=db.Column(db.String(50),nullable=False)
	ride = db.relationship('ride',backref=db.backref('ride.created_by'),primaryjoin='user.username==ride.created_by',lazy='dynamic')
	def __init__(self, username, password):
		self.username = username
		self.password = password
	
class userSchema(ma.Schema):
	class Meta:
		fields = ('username', 'password')

#Init Schema
user_schema = userSchema()
users_schema = userSchema(many=True)

class ride(db.Model):
	__talblename__ = "ride"
	ride_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
	created_by=db.Column(db.String(30),db.ForeignKey('user.username', ondelete='CASCADE'),nullable=False)
	source=db.Column(db.Integer)
	timestamp=db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
	destination=db.Column(db.Integer)
	users=db.Column(db.VARCHAR(200), nullable=True)

	def __init__(self,created_by,timestamp,source,destination):
		self.created_by = created_by
		self.timestamp = timestamp
		self.source = source
		self.destination = destination
		self.users = created_by

class rideSchema(ma.Schema):
	class Meta:
		fields = ('ride_id', 'created_by', 'timestamp', 'source', 'destination','users')

#Init Schema
ride_schema = rideSchema()
rides_schema = rideSchema(many=True)

#Add User
@app.route('/api/v1/users', methods=['PUT'])
def add_user():
	username = request.json['username']
	password = request.json['password']	
	new_user = user(username, password)
	db.session.add(new_user)
	db.session.commit()
	return user_schema.jsonify(new_user),status.HTTP_201_CREATED
	return (jsonify(''),400)
	return (jsonify(''),405)

#Add Ride
@app.route('/api/v1/rides', methods=['POST'])
def add_ride():
	created_by = request.json['created_by']
	timestamp = request.json['timestamp']
	timestamp=datetime.strptime(timestamp,'%d-%m-%Y:%H-%M-%S')
	try:
		time.strptime(timestamp,"%d-%m-%Y:%S-%M-%H")
		print("valid timestamp")
	except ValueError:
		print("Invalid timestamp")
	timestamp2 = str(datetime.now().replace(microsecond=0))
	t1 = datetime.strptime(timestamp,"%d-%m-%Y:%S-%M-%H")
	t2 = datetime.strptime(timestamp2, "%Y-%m-%d %H:%M:%S")
#	if(t2>t1):
#		print("ride is in the future")
#	else:
#		print('f')
	source = request.json['source']
	destination = request.json['destination']
	new_ride = ride(created_by,timestamp,source,destination)
	db.session.add(new_ride)
	db.session.commit()
	return ride_schema.jsonify(new_ride),200
	return (jsonify(''),400)
	return (jsonify(''),405)

#Get all Users
@app.route('/api/v1/users', methods=['GET'])
def get_users():
	all_users = user.query.all()
	result = users_schema.dump(all_users)
	return jsonify(result)

#Get all Rides
@app.route('/api/v1/rides', methods=['GET'])
def get_rides():
	all_rides = ride.query.all()
	result = rides_schema.dump(all_rides)
	return jsonify(result)

#Get Single User
@app.route('/api/v1/users/<username>', methods=['GET'])
def get_single_user(username):
	u = user.query.get(username)
	return user_schema.jsonify(u)

#Remove User
@app.route('/api/v1/users/<username>', methods=['DELETE'])
def del_user(username):
	username = user.query.get(username)
	db.session.delete(username)
	db.session.commit()
	return (jsonify(''), 200)
	return (jsonify(''), 400)
	return (jsonify(''), 405)

#Join user to ride
@app.route('/api/v1/rides/<id>', methods=['POST'])
def join_ride(id):
	unam = request.json['username']
	r = db.select([ride.users]).where(ride.ride_id==id)
	print(r)
	r = r+unam
	db.update(ride).values(ride.users==r)

#All rides between source and destination
@app.route('/api/v1/rides?source=<source>&destination=<destination>',methods=['GET'])
def get_source_rides(source,destination):
	query = db.select([ride.columns.ride_id,ride.columns.username,ride.column.timestamp]).where(db._and(ride.columns.source==source,ride.columns.destination==destination))
	res = db.session.execute(query)
	db.session.commit()
	return (jsonify(res), 200)
	return (jsonify(''), 204)
	return (jsonify(''), 400)

#Details of a given ride
@app.route('/api/v1/rides/<ride_id>',methods=['GET'])
def get_ride(ride_id):
	rides = ride.query.get(ride_id)
	return ride_schema.jsonify(rides),200
	return 

#Delete a ride
@app.route('/api/v1/rides/<ride_id>',methods=['DELETE'])
def del_ride(ride_id):
	r = ride.query.get(ride_id)
	db.session.delete(r)
	db.session.commit()
	return (jsonify(''), 200)
	return (jsonify('',405))

#Write to a database(insert,column,table)
@app.route('/api/v1/db/write',methods=['POST'])
def table_write():
	input_insert = request.json['insert']
	input_column = request.json['column']
	input_table = request.json['table']
	query = db.update(input_table).values(input_column=input_insert)
	db.session.execute(query)
	db.session.commit()
	return(jsonify(''))
#	query = db.update(emp).values(salary = 100000)

#Read from a database(table,column,where)
@app.route('/api/v1/db/read',methods=['POST'])
def table_read():
	input_table=request.json['table']
	input_columns=request.json['columns']
	input_where=request.json['where']
	for column in columns:
		res = db.select([input_table.columns.input_column]).where(db.input_table.columns.input_where)
		db.session.execute(res)
		db.session.commit()
	return (jsonify(''))

#Run Server
if __name__ == "__main__":
	app.run(debug=True)