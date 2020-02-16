import pymysql,requests
from app import app
from db_config import mysql
from flask import jsonify
from flask import flash, request
import sys
import string
import re
import time
from datetime import datetime


# 1 API
@app.route('/api/v1/users',methods=['PUT','GET','POST','DELETE','HEAD','OPTIONS'])
def add_user():
	if request.method == 'PUT':
		try:
			_json = request.json
			_name = _json['username']
			_password = _json['password']

			if(is_sha1(_password)!=True):
				#return jsonify('password did not match the requirement'),400
				return jsonify({}),400
			else:
				pass
			if _name and _password and request.method == 'PUT':
				response = requests.post('http://0.0.0.0:5000/api/v1/db/read',json={'table':'tbl_user','columns':'passwords','where':['username',_name],'gofor':'username'})
				json_response = response.json()
				if(int(json_response)!=0):
					#return jsonify('Username already exists'),400
					return jsonify({}),400
				else:
					response = requests.post('http://0.0.0.0:5000/api/v1/db/write',json={'table':'tbl_user','columns':['username','passwords'],'values':[_name,_password],'gofor':'username'})
					status = response.status_code
					resp = jsonify('{}')
					resp.status_code = 201
					return resp
		except Exception as e:
			print(e)

	elif request.method != 'PUT' or 'DELETE':
		#return jsonify('Method not allowed!'),405
		return jsonify({}),405

# 2 API

@app.route('/api/v1/users/<username>', methods=['DELETE'])
def delete_user(username):
	
	try:
		response = requests.post('http://0.0.0.0:5000/api/v1/db/write',json={'table':'tbl_user','columns':'username','values':['username',username],'gofor':'delete'})
		response = requests.post('http://0.0.0.0:5000/api/v1/db/write',json={'table':'tbl_ride','columns':'username','values':['createdby',username],'gofor':'delete'})
		response = requests.post('http://0.0.0.0:5000/api/v1/db/write',json={'table':'shared_ride','columns':'username','values':['username',username],'gofor':'delete'})
		resp = jsonify({})
		resp.status_code = 200
		return resp
	except Exception as e:
		print(e)


@app.route('/api/v1/users/', methods=['DELETE'])
def invalid_delete_operation():
	#return jsonify('Username not provided'),400
	return jsonify({}),400

# 3 API

@app.route('/api/v1/rides',methods=['POST'])
def add_ride():
	try:
		_json = request.json
		_name = _json['created_by']
		_timestamp = _json['timestamp']
		_source = _json['source']
		_destination = _json['destination']
		if int(_source) == int(_destination):
			return jsonify('{}'),400
		try:                 
			time.strptime(_timestamp, "%d-%m-%Y:%S-%M-%H")
		except ValueError:
			#return jsonify("Invalid time format"),400
			return jsonify({}),400
		response = requests.post('http://0.0.0.0:5000/api/v1/db/read',json={'table':'tbl_user','columns':'passwords','where':['username',_name],'gofor':'username'})
		json_response = response.json()
		if(int(json_response)==0):
			#return jsonify('Username does not exists'),400
			return jsonify({}),400
		else:
			pass
		if _name and _timestamp and _source and _destination and request.method == 'POST':
			response = requests.post('http://0.0.0.0:5000/api/v1/db/write',json={'table':'tbl_ride','columns':['createdby','createdtime','sources','destination'],'values':[_name,_timestamp,_source,_destination],'gofor':'addride'})
			resp = jsonify('{}')
			resp.status_code = 201
			return resp
		else:
			return not_found()
	except Exception as e:
		print(e)


#4 API

@app.route('/api/v1/rides/', methods=['GET'])
def foo():
	try:
		summary = request.args.get('source', None) 
		change = request.args.get('destination', None)
		if summary==None or change==None:
			return jsonify({}),400
		else:
			pass
		resp = requests.post('http://0.0.0.0:5000/api/v1/db/read',json={'table':'tbl_ride','columns':['rideId','createdby','createdtime'],'where':['sources',summary,'destination',change],'gofor':'getride'})
		return resp.text,200
	except Exception as e:
		print(e)
		return jsonify({}),400

#API 5	
@app.route('/api/v1/rides/<int:rideId>',methods=['GET'])
def rides(rideId):
	response = requests.post('http://0.0.0.0:5000/api/v1/db/read',json={'table':'tbl_ride','columns':'createdby','where':['rideId',rideId],'gofor':'checkuser'})
	json_response = response.json()
	if(int(json_response)==0):
		return jsonify('The given rideId does not exist'),400
	else:
		pass
	
	try:
		response = requests.post('http://0.0.0.0:5000/api/v1/db/read',json={'table':'tbl_ride','columns':'createdby','where':['rideId',rideId],'gofor':'getridebyId'})
		response1 = requests.post('http://0.0.0.0:5000/api/v1/db/read',json={'table':'shared_ride','columns':'username','where':['rideId',rideId],'gofor':'getridebyuser'})
		main = validate_users_text(response1.text[1:-2])
		main1= response.text[2:-3]
		maintup = main1.split(',')
		return {
		"rideId": int(maintup[0]),
		"Createdby": str(maintup[1][1:-1]),
		"users": main,
		"timestamp": str(maintup[2][1:-1]),
		"source":int(maintup[3]),
		"destination":int(maintup[4])
    	}
	except Exception as e:
		print(e)
		

#6 API
@app.route('/api/v1/rides/<int:rideId>',methods=['POST'])
def join_ride(rideId):
	try:
		_json = request.json
		_name = _json['username']
		response = requests.post('http://0.0.0.0:5000/api/v1/db/read',json={'table':'tbl_ride','columns':'createdby','where':['rideId',rideId],'gofor':'checkuser'})
		json_response = response.json()
		if(int(json_response)==0):
			#return jsonify('The given rideId does not exist'),400
			return jsonify({}),400

		response1 = requests.post('http://0.0.0.0:5000/api/v1/db/read',json={'table':'tbl_user','columns':'passwords','where':['username',_name],'gofor':'checkuser'})
		json_response1 = response1.json()
		if(int(json_response1)==0):
			#return jsonify('The given username does not exist'),400
			return jsonify({}),400

		response2 = requests.post('http://0.0.0.0:5000/api/v1/db/write',json={'table':'shared_ride','columns':['rideId','username'],'values':[rideId,_name],'gofor':'username'})
		resp = jsonify({})
		resp.status_code = 200
		return resp
	except Exception as e:
		print(e)

#7 API


@app.route('/api/v1/rides/<rideId>',methods=['DELETE'])
def delete_ride(rideId):
	#conn = mysql.connect()
	#cursor = conn.cursor()
	response = requests.post('http://0.0.0.0:5000/api/v1/db/read',json={'table':'tbl_ride','columns':'createdby','where':['rideId',rideId],'gofor':'checkuser'})
	json_response = response.json()
	if(int(json_response)==0):
		return jsonify('The given rideId does not exist'),400
	else:
		pass
	try:
		response = requests.post('http://0.0.0.0:5000/api/v1/db/write',json={'table':'tbl_ride','columns':'rideId','values':['rideId',rideId],'gofor':'delete'})
		resp = jsonify({})
		resp.status_code = 200
		return resp
	except Exception as e:
		print(e)


# 8 API

@app.route('/api/v1/db/read',methods=['PUT','GET','POST','DELETE','HEAD','OPTIONS'])
def read_username_db():	
	try:
		_json = request.json
		tablename = _json['table']
		columns	  = _json['columns']
		condition = _json['where']
		gofor	  = _json['gofor']
		conn = mysql.connect()
		cursor = conn.cursor()
		if(gofor=='username'):
			sql1="SELECT (%s) from (%s) WHERE (%s)=('%s')"%(columns,tablename,condition[0],condition[1])
			cursor.execute(sql1)
			row_count = cursor.rowcount
			return jsonify(row_count)
		elif(gofor=='getride'):
			sql1="SELECT rideId,createdby,createdtime from (%s) WHERE (%s)=(%d) AND (%s)=(%d) AND DATE_FORMAT(NOW(),'%%d-%%m-%%Y:%%s-%%i-%%H') < createdtime"%(tablename,condition[0],int(condition[1]),condition[2],int(condition[3]))
			cursor.execute(sql1)
			rows = cursor.fetchall()
			dictionary = {}
			l = []
			for i in rows:
				dict1 = {}
				dict1["rideId"] = i[0]
				dict1["username"] = i[1]
				dict1["timestamp"]=i[2]
				l.append(dict1)
			return jsonify(l)
		elif(gofor=='checkuser'):
			sql1="SELECT %s FROM %s WHERE %s='%s'"%(columns,tablename,condition[0],condition[1])
			cursor.execute(sql1)
			row_count = cursor.rowcount
			return jsonify(row_count)
		elif(gofor=='getridebyId'):
			sql1="SELECT * FROM %s WHERE %s='%s'"%(tablename,condition[0],condition[1])
			cursor.execute(sql1)
			rows = cursor.fetchall()
			return jsonify(rows)
		elif(gofor=='getridebyuser'):
			sql1="SELECT %s FROM %s WHERE %s='%s'"%(columns,tablename,condition[0],condition[1])
			cursor.execute(sql1)
			rows = cursor.fetchall()
			return jsonify(rows)
	except Exception as e:
		print(e)
	finally:
		cursor.close()
		conn.close()

# 9 API

@app.route('/api/v1/db/write',methods=['PUT','GET','POST','DELETE','HEAD','OPTIONS'])
def write_username_db():
	try:
		_json = request.json
		tablename = _json['table']
		columns   = _json['columns']
		values 	  = _json['values']
		gofor	  = _json['gofor']
		conn = mysql.connect()
		cursor = conn.cursor()
		if(gofor=='username'):
			sql = "INSERT INTO %s(%s,%s) VALUES('%s', '%s')"%(tablename,columns[0],columns[1],values[0],values[1])
			cursor.execute(sql)
			conn.commit()
			resp = jsonify('')
			resp.status_code = 201
			return resp
		elif(gofor=='delete'):
			sql = "DELETE FROM %s WHERE %s='%s'"%(tablename,values[0],values[1])
			cursor.execute(sql)
			conn.commit()
			resp = jsonify('')
			resp.status_code = 200
			return resp
		elif(gofor=='addride'):
			sql = "INSERT INTO %s(%s,%s,%s,%s) VALUES('%s','%s','%s','%s')"%(tablename,columns[0],columns[1],columns[2],columns[3],values[0],values[1],values[2],values[3])
			cursor.execute(sql)
			conn.commit()
			resp = jsonify('')
			resp.status_code = 201
			return resp
	except Exception as e:
		print(e)
	finally:
		cursor.close()
		conn.close()

def is_sha1(pattern1):
	pattern = re.compile(r'\b[0-9a-f]{40}\b')
	match = re.match(pattern,pattern1)
	try:
		match.group(0)
	except AttributeError:
		return False
	return True  

@app.route('/api/hello',methods=['GET'])
def hello():
	return "Hello World"

def validate_users_text(main):
	main = main.split(',')
	out = list()
	for i in main:
		print(i)
		text = ""
		for j in i:
			if (j>='a' and j<='z') or (j>='A' and j<='Z'):
				print(j)
				text = text+j
		out.append(text)
	return out


@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp
		
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
