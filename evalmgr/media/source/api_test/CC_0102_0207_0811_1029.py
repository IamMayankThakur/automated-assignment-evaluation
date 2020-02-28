#!/home/ubuntu/env/bin python3
from flask import Flask, render_template, jsonify, request, abort
import requests
import sqlite3
import re
import json
import csv
import datetime

app=Flask(__name__)


filename = "AreaNameEnum.csv"
fields = []
rows = []
cols1 = []
cols2 = []

with open(filename, 'r') as csvfile:
	csvreader = csv.reader(csvfile)
	fields = next(csvreader) 
	for row in csvreader:
		cols1.append(row[0])
		cols2.append(row[1])

def initialize():
	try:
		conn = sqlite3.connect('rideshare.db')
	except:
		abort(500)
	cur = conn.cursor()
	cur.execute("PRAGMA foreign_keys = ON;")
	cur.execute("CREATE TABLE IF NOT EXISTS user_details(username varchar(50) primary key, password varchar(41) not null);")
	cur.execute("CREATE TABLE IF NOT EXISTS rides(username varchar(50), source varchar(100) not null, destination varchar(100) not null, timess text not null, ride_id integer not null primary key autoincrement, foreign key (username) references user_details (username) on delete cascade);")
	cur.execute("CREATE TABLE IF NOT EXISTS ride_join(username varchar(50), ride_id integer, foreign key (username) references user_details (username) on delete cascade, foreign key (ride_id) references rides (ride_id) on delete cascade);")

def read(table, args, where = "1"):
	columns = ""
	for i in args:
		columns += i + ', '
	columns = columns[:-2]
	sql = list()
	sql.append("SELECT " + columns)
	sql.append(" FROM %s" % table)
	sql.append(" WHERE " + where)
	sql.append(";")
	return "".join(sql)


def upsert(table, **kwargs):
    keys = ["%s" % k for k in kwargs]
    values = ["'%s'" % v for v in kwargs.values()]
    sql = list()
    sql.append("INSERT OR REPLACE INTO %s (" % table)
    sql.append(", ".join(keys))
    sql.append(") VALUES (")
    sql.append(", ".join(values))
    sql.append(")")
    sql.append(";")
    return "".join(sql)


def delete(table, **kwargs):
    sql = list()
    sql.append("DELETE FROM %s " % table)
    sql.append("WHERE " + " AND ".join("%s = '%s'" % (k, v) for k, v in kwargs.items()))
    sql.append(";")
    return "".join(sql)

def engineer(time):
	arr = time.split(':')
	date = arr[0]
	date = date.split("-")
	time = arr[1]
	time = time.split('-')
	entry = date[2] + "-" + date[1] + '-' + date[0] + " " + time[2] + "-" + time[1] + "-" + time[0]
	return entry

def reverse_engineer(time):
	arr = time.split(" ")
	date = arr[0]
	date = date.split('-')
	date.reverse()
	time = arr[1]
	time = time.split('-')
	time.reverse()
	exit = ""
	for i in date:
		exit += i + "-"
	exit = exit[:-1]
	exit += ":"
	for i in time:
		exit += i + "-"
	exit = exit[:-1]
	return exit

def check_password(passwd):
	if(re.fullmatch('[0-9abcdef]{40}', passwd) == None):
		abort(400)

def check_date(date):
	date = date.split(':')
	if(re.fullmatch('^(0[1-9]|[1-2][0-9]|(3)[0-1])-(((0)[13578])|((1)[02]))-\d{4}$', date[0])):
		pass
	elif(re.fullmatch('^(0[1-9]|[1-2][0-9]|30)-(((0)[469])|((1)[1]))-\d{4}$', date[0])):
		pass
	elif(re.fullmatch('^(0[1-9]|2[0-8]|1[0-9])-(((0)[2]))-\d{4}$', date[0])):
		pass
	elif(re.fullmatch('^(0[1-9]|2[0-9]|1[0-9])-(((0)[2]))-\d{4}$', date[0])):
		string = date[0].split("-")
		if((int(string[2])%4 == 0) and (int(string[2])%100 != 0) or (int(string[2])%400 == 0)):
			pass
		else:
			abort(400)
	else:
		abort(400)


	if(None == re.fullmatch('^[0-5][0-9]-[0-5][0-9]-([0-1][0-9]|[2][0-3])', date[1])):
		abort(400)
def check_current_time(string):
	current_time = datetime.datetime.now()
	string = string.split(":")
	string[0] = string[0].split("-")
	string[1] = string[1].split("-")
	given_time = datetime.datetime(int(string[0][2]), int(string[0][1]), int(string[0][0]), int(string[1][2]), int(string[1][1]), int(string[1][0]), 000000)
	if(given_time >= current_time):
		return True
	else:
		return False

initialize()


@app.route('/api/v1/db/write', methods = ['POST'])
def write_db():
	req = request.get_json()
	req_type = req['type']
	table_name = req['table']
	del req['table']
	del req['type']
	with sqlite3.connect("rideshare.db") as con:
		cur = con.cursor()
		cur.execute("PRAGMA foreign_keys = ON;")
		if(req_type == "delete"):
			string = delete(table_name, **req)
		elif(req_type == "write"):
			string = upsert(table_name, **req)
		try:
			cur.execute(string);
			return jsonify({})
		except:
			abort(500)

@app.route('/api/v1/db/read', methods = ['POST'])
def read_db():
	req = request.get_json()

	table_name = req['table']
	try:
		where = req['where']
	except:
		where = "1"
	columns = req['columns']

	with sqlite3.connect("rideshare.db") as con:
		cur = con.cursor()
		cur.execute("PRAGMA foreign_keys = ON;")
		string = read(table_name, columns, where)
		try:
			cur.execute(string);
		except:
			abort(400)
		data = cur.fetchall()
		return json.dumps(data)

@app.route('/api/v1/users', methods = ['PUT'])
def add_user():
	try:
		user_name = request.get_json()['username']
		password = request.get_json()['password']
		check_password(password)
	except:
		abort(400)
	json_send = {'table': 'user_details', 'columns': ["*"], "where": "username = '" + user_name + "'"}
	res = requests.post('http://localhost:5000/api/v1/db/read', json=json_send)
	count = 0
	for i in res.json():
		count += 1
	if(count != 0):
		abort(400)
	json_send = {'username': user_name, 'password': password, 'table': 'user_details', 'type':'write'}
	res = requests.post('http://localhost:5000/api/v1/db/write', json=json_send)
	try:
		res.json()
	except:
		abort(500)
	return res.json(), 201




@app.route('/api/v1/users/<name>', methods = ['DELETE'])
def remove_user(name):
	json_send = {'table': 'user_details', 'columns': ["*"], "where": "username = '" + name + "'"}
	res = requests.post('http://localhost:5000/api/v1/db/read', json=json_send)
	try:
		res.json()
	except:
		abort(400)
	count = 0
	for i in res.json():
		count += 1
	if(count > 0):
		json_send = {'username': name, 'table': 'user_details', 'type':'delete'}
		res = requests.post('http://localhost:5000/api/v1/db/write', json=json_send)
		try:
			res.json()
		except:
			abort(500)			
		return jsonify({})
	abort(400)

@app.route('/api/v1/rides', methods = ['POST'])
def new_ride():
	user_name = request.get_json('created_by')
	timestamp = request.get_json('timestamp')
	source = request.get_json('source')
	destination = request.get_json('destination')
	if(str(source['source']) not in cols1):
		abort(400)
	if(str(destination['destination']) not in cols1):
		abort(400)

	time = timestamp["timestamp"]
	check_date(time)
	entry = engineer(time)
	if(cols2[int(source['source']) - 1] == cols2[int(destination['destination']) - 1]):
		return jsonify({}), 400
	json_send = {'username': user_name['created_by'], 'source': cols2[int(source['source']) - 1], 'destination': cols2[int(destination['destination']) - 1], 'timess': entry, 'table': 'rides', 'type':'write'}
	res = requests.post('http://localhost:5000/api/v1/db/write', json=json_send)
	try:
		res.json()
	except:
		abort(400)
	return res.json(), 201

@app.route('/api/v1/rides', methods = ['GET'])
def get_ride():
	source = request.args.get('source')
	destination = request.args.get('destination')
	if(str(source) not in cols1):
		abort(400)
	if(str(destination) not in cols1):
		abort(400)
	ride_holder = []
	json_send = {'table': 'rides', 'columns': ["*"], "where": "source = '" + cols2[int(source) - 1] + "' and destination = '" + cols2[int(destination) - 1] + "'"}
	res = requests.post('http://localhost:5000/api/v1/db/read', json=json_send)
	try:
		res.json()
	except:
		abort(400)
	for i in res.json():
		ride_holder.append({'rideId': i[4], 'username': i[0], 'timestamp': reverse_engineer(i[3])})
	if(ride_holder == []):
		return jsonify(ride_holder), 204
	refine = []
	for i in ride_holder:
		if(check_current_time(i['timestamp'])):
			refine.append(i)
	return jsonify(refine)


@app.route('/api/v1/rides/<ride_id>', methods = ['GET'])
def list_ride(ride_id):
	ride_holder = []
	users = []

	json_send = {'table': 'rides', 'columns': ["*"], "where": "ride_id = '" + str(ride_id) + "'"}
	res = requests.post('http://localhost:5000/api/v1/db/read', json=json_send)
	try:
		res.json()
	except:
		abort(400)
	count = 0
	for i in res.json():
		count += 1
	if(count == 0):
		return jsonify({}), 204
	json_send = {'table': 'ride_join', 'columns': ["*"], "where": "ride_id = '" + str(ride_id) + "'"}
	res = requests.post('http://localhost:5000/api/v1/db/read', json=json_send)
	try:
		res.json()
	except:
		abort(400)
	for i in res.json():
		users.append(i[0])
	json_send = {'table': 'rides', 'columns': ["*"], "where": "ride_id = '" + str(ride_id) + "'"}
	res = requests.post('http://localhost:5000/api/v1/db/read', json=json_send)
	try:
		res.json()
	except:
		abort(400)
	for i in res.json():
		ride_holder.append({'rideId': i[4], 'created_by': i[0], 'timestamp': reverse_engineer(i[3]),'users': list(set(users)), 'source': i[1], 'destination': i[2]})
	return jsonify(ride_holder[0])

@app.route('/api/v1/rides/<ride_id>', methods = ['POST'])
def join_ride(ride_id):
	json_send = {'table': 'rides', 'columns': ["*"], "where": "ride_id = '" + str(ride_id) + "'"}
	res = requests.post('http://localhost:5000/api/v1/db/read', json=json_send)
	try:
		res.json()
	except:
		abort(400)
	count = 0
	for i in res.json():
		count += 1
	if(count == 0):
		return jsonify({}), 204
	username = request.get_json('username')['username']
	json_send = {'username': username, 'ride_id': str(ride_id), 'table': 'ride_join', 'type':'write'}
	res = requests.post('http://localhost:5000/api/v1/db/write', json=json_send)
	try:
		res.json()
	except:
		abort(400)
	return jsonify({})

@app.route('/api/v1/rides/<ride_id>', methods = ['DELETE'])
def delete_ride(ride_id):
	json_send = {'table': 'rides', 'columns': ["*"], "where": "ride_id = '" + str(ride_id) + "'"}
	res = requests.post('http://localhost:5000/api/v1/db/read', json=json_send)
	try:
		res.json()
	except:
		abort(400)
	count = 0
	for i in res.json():
		count += 1
	if(count == 0):
		return jsonify({}), 204
	json_send = {'ride_id': str(ride_id), 'table': 'ride_join', 'type':'delete'}
	res = requests.post('http://localhost:5000/api/v1/db/write', json=json_send)
	try:
		res.json()
	except:
		abort(400)
	json_send = {'ride_id': str(ride_id), 'table': 'rides', 'type':'delete'}
	res = requests.post('http://localhost:5000/api/v1/db/write', json=json_send)
	try:
		res.json()
	except:
		abort(500)
	return jsonify({})

if __name__ == '__main__':
	app.run(debug=False, port = '5000', host = '127.0.0.1')

