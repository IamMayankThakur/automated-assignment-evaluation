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


if __name__ == '__main__':	
	app.debug=True
	app.run()