# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 19:45:02 2020

@author: Hrushikesh Karanth
"""
import pymysql
import requests
import json
import flask
import hashlib
import re
from flask.testing import FlaskClient
from flask_json import FlaskJSON, JsonError, json_response, as_json
from app import app
from dbconfig import mysql
from flask import jsonify, Response, abort, redirect, url_for, make_response
from requests import post
from flask import flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import exists
import urllib.parse
import httplib2
from httplib2 import Http
from urllib.parse import urlencode
from flask import Flask

app = Flask(__name__)

@app.route("/api/v1/users", methods=["PUT"])
def users():
    _json = request.json
    _name = _json['username']
    _password = _json['password']
    pattern = re.compile(r'\b[0-9a-f]{40}\b')
    match = re.match(pattern, _password)
    if match:
        user = {"tablename": "user", "action": "add",
                "username": _name, "password": _password}
        response = requests.post("http://127.0.0.1:5000/api/v1/db/read", json=user)
        return response.text, 200
    else:
        response = jsonify('Password not in SHA1 hash format!')
        response.status_code = 400
        return response


@app.route("/api/v1/users/<username>", methods=["DELETE"])
def delete_user(username):
    user = {"tablename": "user", "action": "delete", "username": username}
    response = requests.post("http://127.0.0.1:5000/api/v1/db/read", json=user)
    return response.text, 200
# create new ride
@app.route("/api/v1/rides", methods=["POST"])
def create():
    _json = request.json
    _name = _json['created_by']
    _source = _json['source']
    _destination = _json['destination']
    ride = {"tablename": "ride", "action": "add", "created_by": _name,
            "source": _source, "destination": _destination}
    response = requests.post("http://127.0.0.1:5000/api/v1/db/read", json=ride)
    return response.text, 200

# list all upcoming rides for a given source and destination
@app.route('/api/v1/rides?source={source}&destination={destination}', methods=['GET'])
def area(source,destination):
    source = request.args.get('source')
    destination = request.args.get('destination')
    ride = {"tablename": "ride", "action": "list", "source": source, "destination": destination}
    response = requests.post("http://127.0.0.1:5000/api/v1/db/read", json=ride)
    return response.text, 200

# list all the details of a given rides
@app.route("/api/v1/rides/<rideid>", methods=["GET"])
def rides(rideid):
    ride = {"tablename": "join_ride", "action": "list", "rideid": rideid}
    response = requests.post("http://127.0.0.1:5000/api/v1/db/read", json=ride)
    return response.text, 200

# join an existing ride
@app.route("/api/v1/rides/<rideid>", methods=["POST"])
def joinride(rideid):
    _json = request.json
    _name = _json['username']
    ride = {"tablename": "join_ride", "action": "add",
            "rideid": rideid, "username": _name}
    response = requests.post("http://127.0.0.1:5000/api/v1/db/read", json=ride)
    return response.text, 200

# delete a ride
@app.route("/api/v1/rides/<rideid>", methods=["DELETE"])
def delete_ride(rideid):
    ride = {"tablename": "ride", "action": "delete", "rideid": rideid}
    response = requests.post("http://127.0.0.1:5000/api/v1/db/read", json=ride)
    return response.text, 200

# write to db
@app.route("/api/v1/db/write", methods=["POST"])
def write():
    data = request.get_json()
    if(data["tablename"] == "user" and data["action"] == "add"):
        sql = "INSERT INTO user(username, password) VALUES(%s, %s)"
        datas = (data["username"], data["password"])
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(sql, datas)
        conn.commit()
        response = jsonify('User added successfully!')
        return response, 201
    elif(data["tablename"] == "user" and data["action"] == "delete"):
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user WHERE username=%s", data["username"])
        conn.commit()
        response = jsonify('User deleted successfully!')
        return response.text, 201
    elif(data["tablename"] == "ride" and data["action"] == "add"):
        sql = "INSERT INTO ride(created_by, source, destination) VALUES(%s, %s, %s)"
        datas = (data["created_by"], data["source"], data["destination"])
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(sql, datas)
        conn.commit()
        response = jsonify('Ride created successfully!')
        return response, 201
    elif(data["tablename"] == "join_ride" and data["action"] == "add"):
        sql = "INSERT INTO join_ride(rideid, associateduser) VALUES(%s, %s)"
        datas = (data["rideid"], data["username"])
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(sql, datas)
        conn.commit()
        response = jsonify('Ride joined successfully!')
        return response, 201
    elif(data["tablename"] == "ride" and data["action"] == "delete"):
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ride WHERE rideid=%s", data["rideid"])
        conn.commit()
        response = jsonify('Ride deleted successfully!')
        return response, 201
    else:
        return not_found()
        cursor.close()
        conn.close()

@app.route("/api/v1/db/read", methods=["POST"])
def read():
    data = request.get_json()
    if(data["tablename"] == "user" and data["action"] == "add"):
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM user WHERE username=%s",
                       data["username"])
        row = cursor.fetchone()
        if row:
            response = jsonify('User already exists!')
            response.status_code = 400
            return response
        else:
            response = requests.post("http://127.0.0.1:5000/api/v1/db/write", json=data)
            return 'ok', 200
    elif(data["tablename"] == "user" and data["action"] == "delete"):
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM user WHERE username=%s",
                       data["username"])
        row = cursor.fetchone()
        if row:
            response = requests.post("http://127.0.0.1:5000/api/v1/db/write", json=data)
            return 'ok', 200
        else:
            response = jsonify('User not found!')
            response.status_code = 400
            return response
    elif(data["tablename"] == "ride" and data["action"] == "add"):
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM user WHERE username=%s",
                       data["created_by"])
        row = cursor.fetchone()
        if row:
            cursor.execute(
                "SELECT * FROM ride WHERE created_by=%s", data["created_by"])
            row1 = cursor.fetchone()
            if row1:
                response = jsonify('Ride already exists!')
                response.status_code = 400
                return response
            else:
                response = requests.post(
                    "http://127.0.0.1:5000/api/v1/db/write", json=data)
                return 'ok', 200
        else:
            response = jsonify('Username doesnot exists!')
            response.status_code = 400
            return response
    elif(data["tablename"] == "ride" and data["action"] == "list"):
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT rideid,created_by,timestamp FROM ride WHERE source=%d and destination=%d", data["source"], data["destination"])
        row = cursor.fetchone()
        if row:
            response = jsonify(row)
            return response, 200
        else:
            response = jsonify('That ride doesnot exists!')
            return response, 204
    elif(data["tablename"] == "join_ride" and data["action"] == "list"):
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            "SELECT ride.rideid,ride.created_by,join_ride.associateduser,ride.timestamp,ride.source,ride.destination FROM ride, join_ride WHERE ride.rideid=%s", data["rideid"])
        row = cursor.fetchone()
        if row:
            response = jsonify(row)
            return response, 200
        else:
            response = jsonify('That ride doesnot exists!')
            response.status_code = 204
            return response
    elif(data["tablename"] == "join_ride" and data["action"] == "add"):
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            "SELECT rideid FROM ride WHERE rideid=%s", data["rideid"])
        row = cursor.fetchall()
        if row:
            response = requests.post(
                "http://127.0.0.1:5000/api/v1/db/write", json=data)
            return '', 200
        else:
            response = jsonify('That ride doesnot exists!')
            return response, 400
    elif(data["tablename"] == "ride" and data["action"] == "delete"):
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM ride WHERE rideid=%s", data["rideid"])
        row = cursor.fetchone()
        if row:
            response = requests.post("http://127.0.0.1:5000/api/v1/db/write", json=data)
            return 'ok', 200
        else:
            response = jsonify('Ride not found!')
            return response, 204

if __name__ == "__main__":
    app.run()
