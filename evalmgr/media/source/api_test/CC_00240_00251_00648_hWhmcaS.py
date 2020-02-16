 
from flask import Flask,jsonify,request,make_response
#from flask_httpauth import HTTPBasicAuth
import sqlite3 as sql
#auth = HTTPBasicAuth()
import datetime 
import binascii
from flask_cors import CORS,cross_origin
import random
  
app = Flask(__name__)
CORS(app)


with sql.connect('users.db') as con:
	cur = con.cursor()

	cur.execute('CREATE TABLE IF NOT EXISTS users_data (username TEXT,password TEXT)')
	print("Table created")

	con.commit()


with sql.connect('rides.db') as con:

	cur = con.cursor()
	cur.execute('CREATE TABLE IF NOT EXISTS rides_data (ride_id BIGINT AUTO_INCREMENT,username TEXT,time_stamp TEXT,source INT,destination INT)')
	print("Table created")

	con.commit()






@app.route('/',methods=["GET"])
def web_display():
	return "Flask is up and running!"


@app.route('/api/v1/users',methods=["PUT"])
def add_user():
	with sql.connect('users.db') as con:
		cur = con.cursor()

		cur.execute('CREATE TABLE IF NOT EXISTS users_data (username TEXT,password TEXT)')
		print("Table created")

		con.commit()


	if(not(request.json)):
		return jsonify(),400
	with sql.connect('users.db') as con:
		cur = con.cursor()
		cur.execute('SELECT * FROM users_data where username=?',(request.json['username'],))
		out = cur.fetchall()
		if(len(out)):
			return jsonify(),400
		
		pwd = request.json['password']
		for i in pwd:
			if(ord(i)>102):
				return jsonify(),400
		
		cur.execute("INSERT INTO users_data VALUES (?,?)",(request.json['username'],pwd,))
		con.commit()
		return jsonify(),201


#2
@app.route('/api/v1/users/<userName>',methods=['DELETE'])
def remove_user(userName):
	with sql.connect('users.db') as con:
		cur = con.cursor()
		cur.execute('SELECT username FROM users_data where username=?',(userName,))
		out = cur.fetchall()
		if(not(len(out))):
			return jsonify(),400
		cur.execute("DELETE FROM users_data where username=?",(userName,))
		con.commit()
		return jsonify(),200
"""

#4===== route krna h aur csv
@app.route('/api/v1/rides',methods=['GET'])
def aa(source,destination):
	with sql.connect("rides.db") as con:
		cur = con.cursor()
		cur.execute("SELECT source FROM rides_data WHERE source=? AND destination=?",(source,destination,))
		cat_name = cur.fetchall()
		if(not(cat_name)):
			return jsonify(),400
			
	with sql.connect("rides.db") as con:
		cur = con.cursor()
		cur.execute("SELECT * FROM rides_data")
		total = cur.fetchall()
		
		cur.execute("SELECT * FROM rides_data WHERE source=?",(source,))
		rides = cur.fetchall()
		
		if(not(rides)):
			return jsonify(),204
		out = []
		for i in range(len(rides)):
			ret_rides = {
				'ride_id': rides[i][0],
				'username': rides[i][1],
				'time_stamp': rides[i][2],
				'source': rides[i][3],
				'destination': rides[i][4]
			}
			out.append(ret_rides)
		return jsonify(out),200
		"""
	
#5
@app.route('/api/v1/rides/<rideid>',methods=['GET'])
def ride_details(rideid):
	with sql.connect("rides.db") as con:
		cur = con.cursor()
		cur.execute("SELECT ride_id,username,username,time_stamp,source,destination FROM rides_data WHERE ride_id=?",(rideid,))
		out = cur.fetchall()
		if(len(out)==0):
			return jsonify(),400
		
		aa=out[0][1]
		baburao=aa.split(',')[0]
		return jsonify({'ride_id':[out[0][0]]},{'created_by':[baburao]},{'users':[out[0][2]]},{'timestamp':[out[0][3]]},{'source':[out[0][4]]},{'destination':[out[0][5]]}),200


#6
@app.route('/api/v1/rides/<rideid>',methods=['POST'])
def join_ride(rideid):
	if(not(request.json)):
		return jsonify(),400
	with sql.connect("rides.db") as con:
		cur = con.cursor()
		cur.execute("SELECT * FROM rides_data WHERE ride_id=?",(rideid,))
		out = cur.fetchall()

		cur.execute("SELECT username FROM rides_data WHERE ride_id=?",(rideid,))
		out2 = cur.fetchall()
		usor = out2[0][0]

		if(len(out)==0 and len(out2)==0):
			return jsonify(),400

		jobba=request.json['username']
		cur.execute("UPDATE rides_data SET username = ? || ', ' || ? WHERE ride_id=? AND username=?",(usor,jobba,rideid,usor,))
		
		con.commit()
		return jsonify(),200
		
#7
@app.route('/api/v1/rides/<rideId>',methods=['DELETE'])
def delete_ride(rideId):
	with sql.connect("rides.db") as con:
		cur = con.cursor()
		cur.execute("SELECT * FROM rides_data WHERE ride_id=?",(rideId,))
		out = cur.fetchall()
		if(len(out)==0):
			return jsonify(),400
		cur.execute("DELETE FROM rides_data WHERE ride_id=?",(rideId,))
		con.commit()
		return jsonify(),200
		
#3,4
@app.route('/api/v1/rides',methods=['POST', 'GET'])
def create_show_ride():


	if(request.method == 'POST'):

		if(not(request.json)):
			return jsonify(),400

		user = request.json['created_by']
		ts = request.json['timestamp']
		cap = request.json['source']
		cat_name = request.json['destination']
		a_id = random.randint(100, 999) 
		
	
		with sql.connect("rides.db") as con:
			cur = con.cursor()
			
			try:
				datetime.datetime.strptime(ts,'%d-%m-%Y:%S-%M-%H')
			except:
				return jsonify(),400
			
			with sql.connect('users.db') as con2:
				cur2 = con2.cursor()
				cur2.execute("select username from users_data where username=?",(user,))
				out2 = cur2.fetchall()
				if(not(len(out2))):
					return jsonify(),400
			
			
			cur.execute("INSERT INTO rides_data VALUES (?,?,?,?,?)",(a_id,user,ts,cap,cat_name,))
			con.commit()
			return jsonify(),201

	if(request.method == 'GET'):
		source = request.args.get('source')
		destination = request.args.get('destination')	
		source=int(source)
		destination=int(destination)



		if source == None or source == '""' or source == '':
			return {}, 400
		if destination == None or destination == '""' or destination == '':
			return {}, 400
		if(source>=1 and source<=198 )and(destination>=1 and destination<=198):


			with sql.connect("rides.db") as con:
				cur = con.cursor()
				cur.execute("SELECT source FROM rides_data WHERE source=? AND destination=?",(source,destination,))
				blabla = cur.fetchall()
				if(not(blabla)):
					return jsonify(),400
				
			with sql.connect("rides.db") as con:
				cur = con.cursor()
				cur.execute("SELECT * FROM rides_data")
				total = cur.fetchall()
				
				cur.execute("SELECT * FROM rides_data WHERE source=? AND destination=?",(source,destination,))
				rides = cur.fetchall()
				
				if(not(rides)):
					return jsonify(),204
				out = []
				for i in range(len(rides)):
					ret_rides = {
						'ride_id': rides[i][0],
						'username': rides[i][1],
						'time_stamp': rides[i][2],
						#'source': rides[i][3],
						#'destination': rides[i][4]
					}
					out.append(ret_rides)
				return jsonify(out),200
		else:
			return jsonify(),204




		
	
#8
@app.route('/api/v1/db/write',methods=['POST'])
def db_write():
	
	if(not(request.json)):
		return jsonify(),400
	
	data = request.json['insert']
	col = request.json['column']
	tab = request.json['table']
	#print(data,col,tab)
	with sql.connect("writetryda.db") as con:
		cur = con.cursor()

		print(data)
	#conn.execute('DROP TABLE users_data')
		cur.execute("CREATE TABLE if not exists {0} ({1} TEXT)".format(tab,col))
	#conn.execute('alter table ? add ? VARCHAR',(tab,col,))
		cur.execute("INSERT INTO {0}({1}) VALUES ('{2}')".format(tab,col,data))
		con.commit()
	return jsonify(),201


#9
@app.route('/api/v1/db/read',methods=['POST'])
def db_read():
	
	if(not(request.json)):
		return jsonify(),400
	
	data = request.json['where']  
	col = request.json['columns']
	tab = request.json['table']

	data=data.split('=')[1] 
	
	print(data,col,tab)
	with sql.connect("writetryda.db") as con:
		cur = con.cursor()

		#print(data)
		#cur.execute("CREATE TABLE if not exists {0} ({1} TEXT)".format(tab,col))
	#conn.execute('alter table ? add ? VARCHAR',(tab,col,))
		cur.execute("SELECT * from {0} WHERE {1} = '{2}'".format(tab,col,data))
		out2 = cur.fetchall()
		con.commit()
	return jsonify(out2),201




	
@app.errorhandler(405)
def method_not_found(e):
	return jsonify(),405
'''
@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 403)	
   ''' 
if __name__=='__main__':
	app.run(debug=True,host="0.0.0.0") 
	
