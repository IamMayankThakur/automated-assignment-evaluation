from flask import Flask, render_template,jsonify,request,abort,redirect,url_for 
import requests
import json
from flask_mysqldb import MySQL
from datetime import datetime
import csv

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'cloud'

mysql=MySQL(app)

ride_no = 1001
users = {}
rides = {}
password_check = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']


@app.route('/api/v1/users', methods=["PUT"])
def add_user():
	if(request.method == 'PUT'):
		details = request.get_json()
		username = details["username"]
		password = details["password"]
		if(len(password) == 40):
			check = set(password)
			for i in check:
				if i not in password_check:
					abort(400)
			temp = {"type":1, 'items':[username,password]}
			resp = requests.post('http://127.0.0.1:5000/api/v1/db/write', json = temp)
			d = resp.json()
			if(d['ret'] == 400):
				abort(400)
			else:
				return jsonify({}),201
		else:
			abort(400)
	else:
		abort(405)

@app.route('/api/v1/users/<username>', methods = ["DELETE"])
def delete_user(username):
	if(request.method == "DELETE"):
		temp = {'type':1, 'name':username}
		user_list = requests.post('http://127.0.0.1:5000/api/v1/db/read', json = temp)
		ans = user_list.json()['ans']

		if(ans == 'no'):
			abort(400)

		temp = {"type":2, 'items':[username]}
		resp = requests.post('http://127.0.0.1:5000/api/v1/db/write', json = temp)
		d = resp.json()

		if(d['ret'] == 400):
			abort(400)
		else:
			return jsonify({}), 200
	else:
		abort(405)

@app.route('/api/v1/rides', methods = ["POST"])
def create_ride():
	if(request.method == 'POST'):
		details = request.get_json()
		username = details["created_by"]
		temp = {'type':1, 'name':username}
		user_list = requests.post('http://127.0.0.1:5000/api/v1/db/read', json = temp)
		ans = user_list.json()['ans']
		if(ans == 'no'):
			abort(400)

		stamp = details["timestamp"]
		s = stamp.split(':')
		n1 = s[0].split('-')
		n2 = s[1].split('-')
		n = n1[2]+'-'+n1[1]+'-'+n1[0]+':'+n2[2]+'-'+n2[1]+'-'+n2[0]
		
		source = str(details["source"])
		destination = str(details["destination"])

		if(len(source) == 0 or len(destination) == 0 or source == destination):
			abort(400)

		with open('AreaNameEnum.csv', 'r') as file:
		    reader = csv.reader(file)
		    check_l = []
		    check_d = {}
		    for row in reader:
		        check_l.append(row[0])
		        check_d[row[0]] = row[1]

		if(source not in check_l or destination not in check_l):
			abort(400)

		source = int(details["source"])
		destination = int(details["destination"])

		global ride_no
		
		t1 = (ride_no, username, n, source, destination)
		temp = {'type':3, 'items':t1}
		resp = requests.post('http://127.0.0.1:5000/api/v1/db/write', json = temp)
		ride_no += 1
		if(resp.json()['ret'] == 200):
			return jsonify({}), 201
		else:
			abort(400)
	else:
		abort(405)

@app.route('/api/v1/rides')
def list_rides():
	if(request.method == 'GET'):
		source = request.args.get('source')
		destination = request.args.get('destination')

		with open('AreaNameEnum.csv', 'r') as file:
		    reader = csv.reader(file)
		    check_l = []
		    check_d = {}
		    for row in reader:
		        check_l.append(row[0])
		        check_d[row[0]] = row[1]

		if(source not in check_l or destination not in check_l):
			abort(400)

		source = int(source)
		destination = int(destination)

		temp = {'type':2, 'items':(source, destination)}
		user_list = requests.post('http://127.0.0.1:5000/api/v1/db/read', json = temp)
		ans = user_list.json()['ans']
		if(ans == 'no'):
			return jsonify({}), 204
		else:
			return jsonify(ans), 200
	else:
		abort(405)

@app.route('/api/v1/rides/<rideID>')
def ride_details(rideID):
	if(request.method == "GET"):
		temp = {'type':4, 'name':int(rideID)}
		user_list = requests.post('http://127.0.0.1:5000/api/v1/db/read', json = temp)
		ans = user_list.json()['ans']
		if(ans == 'no'):
			return jsonify({}), 204
		else:
			return jsonify(ans), 200
	else:
		abort(405)

@app.route('/api/v1/rides/<rideID>', methods = ["POST"])
def join_ride(rideID):
	if(request.method == 'POST'):
		details = request.get_json()
		username = details["username"]
		temp = {'type':3, 'name':int(rideID)}
		user_list = requests.post('http://127.0.0.1:5000/api/v1/db/read', json = temp)
		ans = user_list.json()['ans']
		if(ans == 'no'):
			abort(400)

		temp = {'type':1, 'name':username}
		user_list = requests.post('http://127.0.0.1:5000/api/v1/db/read', json = temp)
		ans = user_list.json()['ans']
		if(ans == 'no'):
			abort(400)

		t1 = (rideID, username)
		temp = {'type':4, 'items':t1}
		resp = requests.post('http://127.0.0.1:5000/api/v1/db/write', json = temp)
		ans = resp.json()['ret']
		if(ans == 400):
			return jsonify({}), 400
		else:
			return jsonify({}), 200
	else:
		abort(405)

@app.route('/api/v1/rides/<rideID>', methods = ["DELETE"])
def delete_ride(rideID):
	if(request.method == "DELETE"):
		temp = {'type':3, 'name':int(rideID)}
		user_list = requests.post('http://127.0.0.1:5000/api/v1/db/read', json = temp)
		ans = user_list.json()['ans']
		if(ans == 'no'):
			abort(400)

		temp = {"type":5, 'items':[rideID]}
		resp = requests.post('http://127.0.0.1:5000/api/v1/db/write', json = temp)
		d = resp.json()

		if(d['ret'] == 400):
			abort(400)
		else:
			return jsonify({}), 200
		
	else:
		abort(405)



@app.route('/api/v1/db/read', methods = ["POST"])
def read_db():
	if(request.method == 'POST'):
		l = request.get_json()
		if(l["type"] == 1):
			u_handle = mysql.connection.cursor()
			u_handle.execute("SELECT username FROM users WHERE username = %s", (l['name'],))
			ret = u_handle.fetchall()
			print(ret)
			if(len(ret) == 0):
				return {'ans':'no'}
			else:
				return {'ans':'yes'}
		if(l["type"] == 2):
			u_handle = mysql.connection.cursor()
			cur_time = datetime.now()
			print(cur_time)
			print(l['items'])
			send = tuple(l["items"])+(cur_time,)
			u_handle.execute("SELECT ride_id, created_by, time_stamp FROM rides WHERE source_loc = %s AND destination_loc = %s AND time_stamp > %s", send)
			ret = u_handle.fetchall()
			print(ret)
			if(len(ret) == 0):
				return {'ans':'no'}

			tl = []
			for item in ret:
				dat = item[2]
				tim = dat.strftime('%d-%m-%Y:%S-%M-%H')
				td = {}
				td['rideID'] = item[0]
				td['username'] = item[1]
				td['timestamp'] = tim
				tl.append(td)
			
			return {'ans': tl}

		if(l["type"] == 3):
			u_handle = mysql.connection.cursor()
			u_handle.execute("SELECT ride_id FROM rides WHERE ride_id = %s", (l['name'],))
			ret = u_handle.fetchall()
			print(ret)
			if(len(ret) == 0):
				return {'ans':'no'}
			else:
				return {'ans':'yes'}

		if(l["type"] == 4):
			u_handle = mysql.connection.cursor()
			u_handle.execute("SELECT * FROM rides WHERE ride_id = %s", (l['name'],))
			ret = u_handle.fetchall()
			print(ret)
			if(len(ret) == 0):
				return {'ans':'no'}
			
			u_handle2 = mysql.connection.cursor()
			u_handle2.execute("SELECT username FROM riders_list WHERE ride_id = %s", (l['name'],))
			ret2 = u_handle2.fetchall()


			tl = []
			for i in ret2:
				tl.append(i[0])

			universal = ['rideID', 'created_by', 'users', 'timestamp', 'source', 'destination']

			with open('AreaNameEnum.csv', 'r') as file:
			    reader = csv.reader(file)
			    check_l = []
			    check_d = {}
			    for row in reader:
			        check_l.append(row[0])
			        check_d[row[0]] = row[1]

			print(tl)
			td = {}
			td[universal[0]] = ret[0][0]
			td[universal[1]] = ret[0][1]
			td[universal[2]] = tl
			td[universal[3]] = ret[0][2]
			td[universal[4]] = check_d[str(ret[0][3])]
			td[universal[5]] = check_d[str(ret[0][4])]

			return {'ans':td}
	else:
		return {'ret':400}

@app.route('/api/v1/db/write', methods = ["POST"])
def write_db():
	if(request.method == 'POST'):
		l = request.get_json()

		if(l["type"] == 1):
			u_handle = mysql.connection.cursor()
			try:
				u_handle.execute("INSERT INTO users values(%s, %s)",(l['items'][0], l['items'][1]))
			except:
				return {'ret':400}
			mysql.connection.commit()  
			u_handle.close()
			return {'ret':200}

		if(l["type"] == 2):
			u_handle = mysql.connection.cursor()
			try:
				u_handle.execute("DELETE FROM users WHERE username = %s",(l['items'][0],))
			except Exception as e:
				print(e)
				return {'ret':400}
			mysql.connection.commit()  
			u_handle.close()
			return {'ret':200}

		if(l["type"] == 3):
			u_handle = mysql.connection.cursor()
			date_obj = datetime.strptime(l['items'][2], '%Y-%m-%d:%H-%M-%S')
			l['items'][2] = date_obj
			try:
				u_handle.execute("INSERT INTO rides values(%s, %s, %s, %s, %s)",l['items'])
			except Exception as e:
				print(e)
				return {'ret':400}
			mysql.connection.commit()  
			u_handle.close()
			return {'ret':200}

		if(l["type"] == 4):
			u_handle = mysql.connection.cursor()
			try:
				print(l['items'])
				u_handle.execute("INSERT INTO riders_list values(%s, %s)",(l['items'][1], l['items'][0]))
			except:
				return {'ret':400}
			mysql.connection.commit()  
			u_handle.close()
			return {'ret':200}

		if(l["type"] == 5):
			u_handle = mysql.connection.cursor()
			try:
				u_handle.execute("DELETE FROM rides WHERE ride_id = %s",(l['items'][0],))
			except Exception as e:
				print(e)
				return {'ret':400}
			mysql.connection.commit()  
			u_handle.close()
			return {'ret':200}

	else:
		return {'ret':400}


if __name__ == '__main__':	
	app.debug=True
	app.run()