from flask import Flask, render_template,\
jsonify,request,abort,redirect
from flask_sqlalchemy import SQLAlchemy
import random
import csv
from datetime import datetime
import requests
import json
import time

import re

with open('AreaNameEnum.csv', mode='r') as infile:
    reader = csv.reader(infile)
    with open('coors_new.csv', mode='w') as outfile:
        writer = csv.writer(outfile)
        mydict = {rows[0]:rows[1] for rows in reader}


app=Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
db = SQLAlchemy(app)

class User(db.Model):
    username = db.Column(db.String(80), unique=True,primary_key=True)
    password = db.Column(db.String(40), nullable=False)

class Rides(db.Model):
    RideID = db.Column(db.Integer, unique=True,primary_key=True)
    Created_by = db.Column(db.String(40), nullable=False)
    #Users = db.Column(db.ARRAY(db.Integer))
    Timestamp = db.Column(db.String(20), nullable=False)
    Source = db.Column(db.Integer, nullable=False)
    Destination = db.Column(db.Integer, nullable=False)

class Share(db.Model):
	ID=db.Column(db.Integer, primary_key=True)
	RideID=db.Column(db.Integer,nullable=False)
	User=db.Column(db.String(40),nullable=False)

db.create_all()
client = app.test_client()


@app.route('/api/v1/users',methods=['PUT'])
def add_user():
	x=request.get_json()
	pattern=re.compile("^[a-fA-F0-9]{40}$")
	if(not("username" in x.keys() and "password" in x.keys())):
		abort(400,"Wrong request parameters recieved")
	user=request.get_json()["username"]
	password=request.get_json()["password"]
	if(not(pattern.match(password))):
		abort(400,"Password not valid SHA1 hash rex")

	url='/api/v1/db/read'
	obj={
		"table": "User",
		"columns": ["username","password"],
		"where": "username="+user
		}
	response = client.post(url, json=obj).get_json()
	

	check=response["info"]
	if(check):
		return "Request succesfully recieved but username already exists",200
	else:
		url='/api/v1/db/write'
		obj = {
				"insert_data": [
				{
					"col": "username",
					"data": user
				},
				{
					"col": "password",
					"data": password
				}
			],
		"table": "User"
		}
		response = client.post(url, json=obj).get_json()
	return {},201 #succesful PUT
@app.route('/api/v1/db/write',methods=['POST'])
def write_db():
	x=request.get_json()
	if("insert_data" in x):
		insert_data=x["insert_data"]
		tab=x["table"]
		newentry=eval(tab)()
		#return str(newentry)
		for i in insert_data:
			hi=i["col"]
			setattr(newentry,hi,i["data"])
		db.session.add(newentry)
	elif("delete_data" in x):
		delete_data=x["delete_data"]
		tab=eval(x["table"])
		d1=getattr(tab,delete_data[0]["col"])
		x=tab.query.filter(d1==delete_data[0]["data"]).delete()
		#db.session.delete(x)
	db.session.commit()
	return '',200

@app.route('/api/v1/db/read',methods=['POST'])
def read_db():
	x=request.get_json()
	cols=x["columns"]
	tab=eval(x["table"])
	if(not(x["where"])):
		q=tab.query.all()
	else:
		if('&' in x["where"]):
			d_form="%d-%m-%Y:%S-%M-%H"
			curr_time=time.strftime(d_form)
			
			#return {"info":[curr_time]}
			sp=x["where"].split('&')
			lhs1=sp[0].split("=")[0]
			d1=getattr(tab,lhs1)
			rhs1=sp[0].split("=")[1]
			lhs2=sp[1].split("=")[0]
			d2=getattr(tab,lhs2)
			rhs2=sp[1].split("=")[1]
			if(x["table"]=="Share"):
				q=tab.query.filter((d1==rhs1)&(d2==rhs2)).all()
			else:
				d3=getattr(tab,"Timestamp")
				d4=getattr(tab,"RideID")
				#return {"info":"hi"}
				#q=tab.query.filter((d1==rhs1)&(d2==rhs2)&((datetime.strptime(getattr(tab,"Timestamp"),d_form)-datetime.strptime(curr_time,d_form)).total_seconds()>0)).all()
				q=tab.query.filter((d1==rhs1)&(d2==rhs2)).all()
				#return {"info":[hi]}

		else:
			lhs=x["where"].split("=")[0]
			d=getattr(tab,lhs)
			rhs=x["where"].split("=")[1]
			q=tab.query.filter(d==rhs).all()
	response={"info":[]}
	for j in q:
		#return {"info":str(j)}
		temp={}
		for i in cols:
			col=i
			if(i=="Timestamp"):
				if((datetime.strptime(getattr(j,i),d_form)-datetime.strptime(curr_time,d_form)).total_seconds()>0):
					temp[i]=getattr(j,i)
					continue
				else:
					temp={}
					break
				return {"info":str(type(getattr(j,i)))}
			temp[i]=getattr(j,i)
		if(temp):
			response["info"].append(temp)
	return response
if __name__ == '__main__':	
	app.debug=True
	app.run()
