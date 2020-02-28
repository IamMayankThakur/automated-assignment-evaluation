import pymysql
import requests
from app import app
from db_config import mysql
from flask import jsonify
from flask import flash, request
import pandas 
import json
import datetime
		
@app.route('/api/v1/users', methods=['PUT']) #API 1
def add_user():

		if(request.method!="PUT"):
			return jsonify({}),405
	
		_json = request.json
		_name = _json['username']
		_password = _json['password']
		
		if _name and _password and request.method == 'PUT':
		
			if(len(_password)==40):
				for i in _password:
					if(i=='A' or i=='a' or i=='B' or i=='b' or i=='C' or i=='c' or i=='D' or i=='d' or i=='E' or i=='e' or i=='F' or i=='f' or ( int(i)>=0 and int(i)<=9)):
						url='http://ec2-54-227-82-19.compute-1.amazonaws.com/api/v1/db/write' 
						obj={'table' : 'users', 'name':_name , 'password':_password,'method': 'PUT'}
						response = requests.post(url,json=obj)
						
						if(response.status_code == 200):
							return jsonify({}),201
						else:	
							return jsonify({}),400
			else:
				return jsonify({}),400
			
						
			
		
@app.route('/api/v1/users/<name>', methods=['DELETE']) # API 2
def delete_user(name):
		
		if(not(request.method=="DELETE")):
			return jsonify({}),405
			
		url='http://ec2-54-227-82-19.compute-1.amazonaws.com/api/v1/db/read' 
		obj={'table':'users','name':name,'method': 'GET'}
		response = requests.post(url,json=obj)	
		if(response.status_code == 400):
				return jsonify({}),400
		
		url='http://ec2-54-227-82-19.compute-1.amazonaws.com/api/v1/db/write' 
		obj={'table' : 'users', 'name':name,'method': 'DELETE'}
		response = requests.post(url,json=obj)
		if(response.status_code != 200):
				return jsonify({}),400
				
		url='http://ec2-54-227-82-19.compute-1.amazonaws.com/api/v1/db/write' 
		obj={'table' : 'rides', 'created_by':name,'method': 'DELETE2'}
		response = requests.post(url,json=obj)
		if(response.status_code != 200):
				return jsonify({}),400
				
		
		
				
				
	
		url='http://ec2-54-227-82-19.compute-1.amazonaws.com/api/v1/db/read'
		obj={'table':'rides','name':name,'method': 'GETUSERS'}
		response = requests.post(url,json=obj)
		x = json.loads(response.text)
		
		lst=[]
		for i in x:
			m=i['users']
			if not m:
				continue
			elif(name in m):
			
				lst.append(i['rideId'])
			else:
				continue
				
		
		length=len(lst)
		
		for i in lst:
			url='http://ec2-54-227-82-19.compute-1.amazonaws.com/api/v1/db/read'
			
			obj={'table':'rides','rideId':i,'method': 'GETALL'}
			response1 = requests.post(url,json=obj)
			
			x = json.loads(response1.text)
			passengers = x["users"]
			
			k=passengers.split(',')
			k.remove(name)
			
			newusers = ','.join(k)
			#return jsonify(newusers),200
			
						
			url='http://ec2-54-227-82-19.compute-1.amazonaws.com/api/v1/db/write' 
			obj={'table':'rides','users': newusers,'rideId':i,'method': 'UPDATE'}
			response = requests.post(url,json=obj)
			if(response.status_code == 200):
				continue
			else:	
				return jsonify({}),400
				
		return jsonify({}),200
			
		
			
			

@app.route('/api/v1/rides', methods=['POST']) #API 3
def add_ride():
	
	if(request.method!="POST"):
			return jsonify({}),405
		
	_json = request.json
	_created_by = _json['created_by']
	_timestamp = _json['timestamp']
	_source = _json['source']
	_destination = _json['destination']
	
	try:
		date_obj = datetime.datetime.strptime(_timestamp, '%d-%m-%Y:%S-%M-%H')
	except:
		return jsonify({}),400
	

		
	if _created_by and _timestamp and _source and _destination and request.method == 'POST':
		
		df = pandas.read_csv("AreaNameEnum.csv")
		if(int(_source) not in df["area"] or int(_destination) not in df["area"] or _source==_destination):
			return jsonify({}),400
		
		url='http://ec2-54-227-82-19.compute-1.amazonaws.com/api/v1/db/read' 
		obj={'table':'users','name':_created_by,'method': 'GET'}
		response = requests.post(url,json=obj)	
		if(response.status_code == 400):
				return jsonify({}),400
		
		
		
		url='http://ec2-54-227-82-19.compute-1.amazonaws.com/api/v1/db/write' 
		obj={'table':'rides','created_by':_created_by,'timestamp':_timestamp,'source':_source,'destination':_destination,  					'method': 'POST'}
		response = requests.post(url,json=obj)
		return jsonify({}),200
	
			


@app.route('/api/v1/rides',methods=['GET']) #API 4
def ride():

	if(not(request.method == 'GET')):
		return jsonify({}),405
		
	df = pandas.read_csv("AreaNameEnum.csv")
		
	
			
				
		
	_source=request.args.get('source')
	_destination=request.args.get('destination')
	
	if(int(_source) not in df["area"] or int(_destination) not in df["area"]):
			return jsonify({}),400
	
	url='http://ec2-54-227-82-19.compute-1.amazonaws.com/api/v1/db/read'
	
	obj={'table':'rides','source':_source,'destination':_destination,'columns':["rideId","created_by","timestamp"],'method': 'GET'}
	response = requests.post(url,json=obj)
	x =json.loads(response.text.replace("created_by","username"))
	now_timestamp = datetime.datetime.now()

	
	if(response.text=="{}\n"):
		return jsonify({}),204
	else:	
		
		
		lst=[]
		for i in x:
			m=i['timestamp']
			if(datetime.datetime.strptime(m,'%d-%m-%Y:%S-%M-%H')>=now_timestamp):
				lst.append(i)
			else:
				continue
 			
		
		
		if(lst):
			return jsonify(lst),200
		else:
			return jsonify({}),204	
	
	
	
	
@app.route('/api/v1/rides/<int:rideId>',methods=['GET'])  #API 5
def oneride(rideId):

		
	
		url='http://ec2-54-227-82-19.compute-1.amazonaws.com/api/v1/db/read'
		
		if(not(request.method == 'GET')):
			return jsonify({}), 405
			
        	
	
		obj={'table':'rides','rideId':rideId,'method': 'GETALL'}
		response = requests.post(url,json=obj)
		
		if(response.text == "{}\n"):
			return jsonify({}), 204
			
		elif(response.status_code==200):
			return response.text,200
        	
        	
       
		
@app.route('/api/v1/rides/<int:rideId>', methods=['POST'])   #API 6
def update_user(rideId):
	
		if(not(request.method=='POST')):
			return jsonify('dd'),405
			
		url='http://ec2-54-227-82-19.compute-1.amazonaws.com/api/v1/db/read'
			
		obj={'table':'rides','rideId':rideId,'method': 'GETALL'}
		response1 = requests.post(url,json=obj)
		
		if(response1.text == "{}"):
			return jsonify({}), 400
			
				
		_json = request.json
		_name= _json['username']
				
		url='http://ec2-54-227-82-19.compute-1.amazonaws.com/api/v1/db/read' 
		obj={'table':'users','name':_name,'method': 'GET'}
		response2 = requests.post(url,json=obj)	
		if(response2.status_code == 400):
				return jsonify({}),400
				
		x = json.loads(response1.text)
		passengers = x["users"]
		
		
		if not passengers:                         #if no passengers onboard
			passengers = _name 
		else:
			if(_name in passengers):
				return jsonify({}),204
			passengers=passengers +','+_name
		
		
		
		url='http://ec2-54-227-82-19.compute-1.amazonaws.com/api/v1/db/write' 
		obj={'table':'rides','users': passengers,'rideId':rideId,'method': 'UPDATE'}
		response = requests.post(url,json=obj)
		if(response.status_code == 200):
				return jsonify({}),200
		else:	
				return jsonify({}),400
			
		
			
		

@app.route('/api/v1/rides/<rideId>', methods=['DELETE']) #API 7
def delete_ride(rideId):
	
		if(not(request.method=="DELETE")):
			return jsonify({}),405
			
		url='http://ec2-54-227-82-19.compute-1.amazonaws.com/api/v1/db/read'
			
		obj={'table':'rides','rideId':rideId,'method': 'GETALL'}
		response = requests.post(url,json=obj)
		
		if(response.text == "{}\n"):
			return jsonify({}), 400
		
		url='http://ec2-54-227-82-19.compute-1.amazonaws.com/api/v1/db/write' 
		obj={'table':'rides','rideId':rideId,'method': 'DELETE'}
		response = requests.post(url,json=obj)
		return jsonify({}),200
		
		
		
 
	


@app.route('/api/v1/db/write',methods=["POST"])  #API 8
def write():
	try:
		_json = request.get_json()
		
		if(_json['table']=='users'):
			if (_json['method']=='PUT'):
				sql = "INSERT INTO users(username,password) VALUES(%s,%s)"
				data = (_json['name'],_json['password'],)
				conn = mysql.connect()
				cursor = conn.cursor()
				x=cursor.execute(sql, data)
				conn.commit()
				cursor.close() 
				conn.close()
				if(x):
					return jsonify({}),200
				else:
					return jsonify({}),400	
				
				
				
				
				
			if (_json['method']=='DELETE'):
							
				conn = mysql.connect()
				cursor = conn.cursor()
				x=cursor.execute("DELETE FROM users WHERE username=%s", (_json['name'],))
				
				conn.commit()
				cursor.close() 
				conn.close()
				
				if(x):
					return jsonify({}),200
				else:
					return jsonify({}),400	
				
				
			else:
				return not_found()	
			
			
			
			
				
		if(_json['table']=='rides'):
			if (_json['method']=='POST'):
				sql = "INSERT INTO rides(created_by,timestamp,source,destination) VALUES(%s,%s,%s,%s)"
				data = (_json['created_by'],_json['timestamp'],_json['source'],_json['destination'],)
				conn = mysql.connect()
				cursor = conn.cursor()
				cursor.execute(sql, data)
				conn.commit()
				cursor.close() 
				conn.close()
				return jsonify({}),200

		
			if (_json['method']=='DELETE2'):	
				conn = mysql.connect()
				cursor = conn.cursor()
				cursor.execute("DELETE FROM rides WHERE created_by=%s", (_json['created_by'],))
				conn.commit()
				cursor.close() 
				conn.close()
				return jsonify({}),200
			
			if (_json['method']=='DELETE'):	
				conn = mysql.connect()
				cursor = conn.cursor()
				cursor.execute("DELETE FROM rides WHERE rideId=%s", (_json['rideId'],))
				conn.commit()
				cursor.close() 
				conn.close()
				return jsonify({}),200
				
			if (_json['method']=='UPDATE'):
				sql = "UPDATE rides SET users = %(users)s WHERE rideId = %(rideId)s"
				#data = (_json['created_by'],_json['timestamp'],_json['source'],_json['destination'],)
				conn = mysql.connect()
				cursor = conn.cursor()
				x=cursor.execute(sql, {'users':_json["users"],'rideId':_json["rideId"]} )
				conn.commit()
				cursor.close() 
				conn.close()
				
				if(x):
					return jsonify({}),200
				else:
					return jsonify({}),400	
			
		
		
			else:
				return not_found()			
			
				
						
	except Exception as e:
		print(e)
			


@app.route('/api/v1/db/read',methods=['POST'])   #API 9
def read():


	try:
		_json = request.get_json()
		
		
		if(_json['table']=='users'):
		
			if (_json['method']=='GET'):
				conn = mysql.connect()
				cursor = conn.cursor(pymysql.cursors.DictCursor)
				select_stmt = "SELECT * FROM users WHERE username= %s"
				x=cursor.execute(select_stmt,_json['name'])
				
				if(x):
					return jsonify({}),200
				else:
					return jsonify({}),400	
				
		
		if(_json['table']=='rides'):
		
			if (_json['method']=='GET'):
			
				columns=_json["columns"]
				conn = mysql.connect()
				cursor = conn.cursor(pymysql.cursors.DictCursor)
				select_stmt = "SELECT * FROM rides WHERE source = %(source)s and destination = %(destination)s"
				cursor.execute(select_stmt, { 'source': _json['source'] , 'destination':_json['destination'] })
				rows = cursor.fetchall()
				x=rows
				for i in x:
 					del i['destination']
 					del i['source']
 					del i['users']

				return jsonify(x),200
				
				
			if (_json['method']=='GETUSERS'):
			
				_name=_json["name"]
				conn = mysql.connect()
				cursor = conn.cursor(pymysql.cursors.DictCursor)
				select_stmt = "SELECT * FROM rides"
				x=cursor.execute(select_stmt)
				rows = cursor.fetchall()
				resp = jsonify(rows)
				
				if(x):
					return resp,200
				else:
					return jsonify({}),400	
				
				
				
			if (_json['method']=='GETALL'):	
				conn = mysql.connect()
				cursor = conn.cursor(pymysql.cursors.DictCursor)
				x=cursor.execute("SELECT * FROM rides WHERE rideId = %s ", _json['rideId'])
				row = cursor.fetchone()
				resp = jsonify(row)
				
				if(x):
					return resp,200
				else:
					return jsonify({}),400	
				
				
				
				
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()
				




		
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
    app.run()
