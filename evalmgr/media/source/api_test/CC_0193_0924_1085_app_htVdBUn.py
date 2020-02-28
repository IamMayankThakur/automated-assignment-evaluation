from flask import Flask,render_template,jsonify,request,abort
import requests
import sqlite3
import re
import csv
from datetime import datetime


app=Flask(__name__)


@app.route('/')
def hello_world():
	return "RideShare API"


@app.route('/api/v1/users',methods=["PUT"])
def add_user():
	data = request.get_json()
	if("username" in data and "password" in data):
		new_username = request.get_json()["username"]
		new_passw = (request.get_json()["password"]).lower()
		url = 'http://127.0.0.1:5000/api/v1/db/read'
		myobj = {"command": "select","table":"users","where":"username="+"'"+new_username+"'"}
		response = requests.post(url, json = myobj)
		y = response.json()
		n = len(y)
		if(n==0 and re.match(r"[0-9a-f]{40}", new_passw) and len(new_username)>0 and len(new_passw)==40):
			url = 'http://127.0.0.1:5000/api/v1/db/write'
			myobj = {"command": "insert","table":"users","column_list":{"username":"'"+new_username+"'","password":"'"+new_passw+"'"}}
			response = requests.post(url, json = myobj)
			return jsonify ({}),201
		else:
			return jsonify ({}),400
	else:
		return jsonify ({}),400

@app.route('/api/v1/db/write',methods=["POST"])
def write_db():
	data = request.get_json()
	if("table" not in data or "command" not in data):
		return "Incorrect command/data.",400
	else:
		table=data["table"]
	if(data["command"]=="insert"):
		cols = data["column_list"]
		s=""
		for i in cols:
			s=s+i+","
		s=s[:len(s)-1]
		t=""
		for i in cols:
			t=t+cols[i]+","
		t=t[:len(t)-1]
		sql = "insert into "+table+"("+s+") VALUES ("+t+")"
	elif(data["command"]=="delete"):
		s = ""
		sql = "delete from "+table 
		if("where" in data):
			sql = sql + " where "+ data["where"]
	else:
		return "Incorrect command/data.",400
	try:
		with sqlite3.connect("rideshare.db") as con:
			cur = con.cursor()
			cur.execute(sql)
			con.commit()
		return "Ok",200
	except:
		return "Incorrect command/data.",400

@app.route('/api/v1/db/read',methods=["POST"])
def read_db():
	data = request.get_json()
	if("table" not in data):
		return "Incorrect command/data.",400
	else:
		table=data["table"]
	sql = "select "
	if(data["command"]=="select"):
		if("column_list" in data):
			for i in data["column_list"]:
				sql = sql + i + ","
			sql = sql[:len(sql)-1] + " from " + table
		else:
			sql = sql+"* from "+table
		if("where" in data):
			sql = sql + " where "+ data["where"]
		if("group by" in data):
			sql = sql + " group by "
			for i in data["group by"]:
				sql = sql + i + ","
			sql = sql[:len(sql)-1]
		try:
			with sqlite3.connect("rideshare.db") as con:
				cur = con.cursor()
				cur.execute(sql)
				rows = cur.fetchall()
				con.commit()
			return jsonify(rows),200
		except:
			return "Incorrect command/data.",400
	else:
		return "Incorrect command/data.",400


if __name__ == '__main__':	
	app.debug=True
	app.run()