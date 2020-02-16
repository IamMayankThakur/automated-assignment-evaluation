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


if __name__ == '__main__':	
	app.debug=True
	app.run()
