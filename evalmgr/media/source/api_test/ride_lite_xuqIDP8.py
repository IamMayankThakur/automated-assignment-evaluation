from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy

import requests
import os
import sys

from datetime import datetime
import csv

application = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

application.config["DEBUG"] = True
application.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///"+os.path.join(basedir,"db.sqlite")

db = SQLAlchemy(application)

db_write_url = "http://127.0.0.1:5000/api/v1/db/write"
db_read_url = "http://127.0.0.1:5000/api/v1/db/read"

#___________________________________________________________________#
#                             Vishwas                               #
#___________________________________________________________________#

class User(db.Model):
    username = db.Column(db.Text(), primary_key=True,
                         nullable=False, autoincrement=False)
    password = db.Column(db.Text(), nullable=False)


class Places(db.Model):
    place_id = db.Column(db.Integer(), primary_key=True, autoincrement=False)
    name = db.Column(db.Text())


class Ride(db.Model):
    ride_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    creator = db.Column(db.Text(), db.ForeignKey(
        "user.username"), nullable=False)

    source_id = db.Column(db.Integer(), db.ForeignKey(
        "places.place_id"), nullable=False)
    destination_id = db.Column(db.Integer(), db.ForeignKey(
        "places.place_id"), nullable=False)

    timestamp = db.Column(db.DateTime(), nullable=False)


class Share(db.Model):
    index = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    ride_id = db.Column(db.Integer(), db.ForeignKey(
        "ride.ride_id"), nullable=False)
    username = db.Column(db.Text(), db.ForeignKey(
        "user.username"), nullable=False)


def create_db():
    db.create_all()
    place = Places.query.first()
    if(place is None):
        with open("AreaNameEnum.csv") as csv_file:
            rows = list(csv.reader(csv_file, delimiter=","))[1:]
            for num, name in rows:
                num = int(num)
                place = Places(place_id=num, name=name)
                db.session.add(place)
        db.session.commit()

#___________________________________________________________________#
#                            Ananth                                 #
#___________________________________________________________________#

@application.route("/api/v1/users", methods=["PUT"])
def add_user():
    req_data = request.get_json()
    name = req_data["username"]
    pword = req_data["password"]
    valid_token = {"A", "B", "C", "D", "E", "F", "0", "1", "2", "3", "4", "5", "6", "7",
                   "8", "9", "a", "b", "c", "d", "e", "f"}

    count = 0
    for i in pword:
        if i in valid_token:
            count = count + 1

    if(count == 40):

        insert_dict = {"method": "insert",
                       "column": ["username", "password"],
                       "table": "user",
                       "values": [name, pword]
                       }

        query_dict = {"method": "select",
                      "column": ["username"],
                      "table": "user",
                      "values": [name]
                      }

        response = requests.post(
            db_read_url, json=query_dict).json()["results"]
        if(response == []):
            res = requests.post(db_write_url, json=insert_dict)
            response_msg = {}
            status = 201
        else:
            response_msg = {}
            status = 400
    else:
        response_msg = {}
        status = 400

    return jsonify(response_msg), status


@application.route("/api/v1/users/<name>", methods=["DELETE"])
def remove_user(name):
    query_dict = {"method": "select",
                  "table": "user",
                  "columns": ["username"],
                  "values": [name]
                  }

    response = requests.post(db_read_url, json=query_dict).json()["results"]

    if response == []:
        response_msg = {}
        status = 400
    else:
        delete_dict = {"method": "delete",
                       "table": "user",
                       "columns": ["username"],
                       "values": [name]
                       }

        requests.post(db_write_url, json=delete_dict)
        response_msg = {}
        status = 200

    return jsonify(response_msg), status

#___________________________________________________________________#
#                             Achintya                              #
#___________________________________________________________________#


@application.route("/api/v1/rides", methods=["POST", "GET"])
def ride_create_list():
    if(request.method == "POST"):
        data = request.get_json()

        name = data['created_by']
        source = data['source']
        destination = data['destination']
        timestamp = data['timestamp']
        dt = datetime.strptime(timestamp, "%d-%m-%Y:%S-%M-%H")
        now = datetime.now()

        source_query_dict = {"method": "select",
                             "table": "places",
                             "columns": ["id"],
                             "values": [source]
                             }

        destination_query_dict = {"method": "select",
                                  "table": "places",
                                  "columns": ["id"],
                                  "values": [destination]
                                  }

        name_query_dict = {"method": "select",
                           "table": "user",
                           "columns": ["username"],
                           "values": [name]
                           }

        name_response = requests.post(
            db_read_url, json=name_query_dict).json()["results"]
        source_response = requests.post(
            db_read_url, json=source_query_dict).json()["results"]
        destination_response = requests.post(
            db_read_url, json=destination_query_dict).json()["results"]

        if (name_response == [] or source_response == [] or destination_response == [] or dt < now):
            response_msg = {}
            status = 400
        else:
            insert_dict = {"method": "insert",
                           "table": "ride",
                           "columns": ["creator", "source_id", "destination_id", "timestamp"],
                           "values": [name, source, destination, timestamp]
                           }
            requests.post(db_write_url, json=insert_dict)
            response_msg = {}
            status = 201
    else:
        source = request.args.get('source')
        destination = request.args.get('destination')

        destination_query_dict = {"method": "select",
                                  "table": "places",
                                  "columns": ["id"],
                                  "values": [destination]
                                  }

        source_query_dict = {"method": "select",
                             "table": "places",
                             "columns": ["id"],
                             "values": [source]
                             }

        source_response = requests.post(
            db_read_url, json=source_query_dict).json()["results"]
        destination_response = requests.post(
            db_read_url, json=destination_query_dict).json()["results"]

        if (source_response == [] or destination_response == []):
            response_msg = {}
            status = 400
        else:
            query_dict = {"method": "select",
                          "table": "ride",
                          "columns": ["source", "destination"],
                          "values": [source, destination]
                          }
            query_response = requests.post(
                db_read_url, json=query_dict).json()["results"]

            if(query_response == []):
                response_msg = {}
                status = 404
            else:
                response_msg = []
                for ride_id, user, timestamp in query_response:
                    response_msg.append({"rideId": ride_id,
                                         "username": user,
                                         "timestamp": timestamp
                                         })
                status = 200
    return jsonify(response_msg), status

#___________________________________________________________________#
#                             Abhishek                              #
#___________________________________________________________________#

@application.route("/api/v1/rides/<ride_id>", methods=["GET", "POST", "DELETE"])
def ride_details(ride_id):

    ride_query_dict = {"method": "select",
                       "table": "ride",
                       "columns": ["id"],
                       "values": [ride_id]
                       }

    response = requests.post(
        db_read_url, json=ride_query_dict).json()["results"]

    if(response == []):
        response_msg = {}
        status = 405
    else:
        if(request.method == "GET"):
            ride_id, creator, timestamp, source_id, destination_id = response

            ride_query_dict["table"] = "share"
            shares = requests.post(db_read_url, json=ride_query_dict).json()[
                "results"]

            ride_query_dict["table"] = "places"
            ride_query_dict["values"] = [source_id]
            source = requests.post(db_read_url, json=ride_query_dict).json()[
                "results"][1]

            ride_query_dict["values"] = [destination_id]
            destination = requests.post(db_read_url, json=ride_query_dict).json()[
                "results"][1]

            users = [i[1] for i in shares]
            response_msg = {
                "rideID": ride_id,
                "Created_by": creator,
                "users": users,
                "Timestamp": timestamp,
                "source": source,
                "destination": destination
            }
            status = 200

        elif(request.method == "POST"):
            name = request.get_json()['username']

            query_dict = {"method": "select",
                          "column": ["username"],
                          "table": "user",
                          "values": [name]
                          }

            response = requests.post(
                db_read_url, json=query_dict).json()["results"]
            if(response == []):
                response_msg = {}
                status = 405
            else:
                share_dict = {"method": "insert",
                              'table': "share",
                              'columns': ['id', "name"],
                              'values': [ride_id, name]
                              }

                response = requests.post(db_write_url, json=share_dict)
                response_msg = {}
                status = 200

        else:
            ride_query_dict["method"] = "delete"
            response = requests.post(
                db_write_url, json=ride_query_dict)
            response_msg = {}
            status = 200

    return jsonify(response_msg), status

#___________________________________________________________________#
#                             Vishwas                               #
#___________________________________________________________________#

@application.route("/api/v1/db/write", methods=["POST"])
def db_write():
    data = request.get_json()

    if(data["method"] == "insert"):
        if(data["table"] == "user"):
            user = User(username=data["values"][0], password=data["values"][1])
            db.session.add(user)
            db.session.commit()
            response = {"response": "User inserted"}
            status = 201
        elif(data["table"] == "ride"):
            time = datetime.strptime(
                data["values"][3], "%d-%m-%Y:%S-%M-%H")
            ride = Ride(creator=data["values"][0], source_id=data["values"]
                        [1], destination_id=data["values"][2])
            db.session.add(ride)
            db.session.commit()
            response = {"response": "Ride inserted"}
            status = 200
        elif(data["table"] == "share"):
            share = Share(ride_id=data["values"][0],
                          username=data["values"][1])
            db.session.add(share)
            db.session.commit()
        else:
            response = {"response": "Table Not Present"}
            status = 405

    elif(data["method"] == "delete"):
        if(data["table"] == "user"):
            user = User.query.filter_by(username=data["values"][0]).first()
            if(user is not None):
                db.session.delete(user)
                db.session.commit()
                response = {"response": "User deleted"}
                status = 200
            else:
                response = {"response": "User not present"}
                status = 405
        elif(data["table"] == "ride"):
            ride = Ride.query.filter_by(ride_id=data["values"][0]).first()
            if(ride is not None):
                db.session.delete(ride)
                db.session.commit()
                response = {"response": "Ride deleted"}
                status = 200
            else:
                response = {"response": "Ride not present"}
                status = 405
        else:
            response = {"response": "Table Not Present"}
            status = 405

    else:
        response = {"response": "Method Not Supported"}
        status = 405

    return jsonify(response), status


@application.route("/api/v1/db/read", methods=["POST"])
def db_read():
    data = request.get_json()
    res = []
    status = 200
    if(data["method"] == "select"):
        if(data["table"] == "user"):
            user = User.query.filter_by(username=data["values"][0]).first()
            if(user is not None):
                res = [user.username, user.password]
            response = {"results": res}

        elif(data["table"] == "places"):
            place = Places.query.filter_by(place_id=data["values"][0]).first()
            if(place is not None):
                res = [place.place_id, place.name]
            response = {"results": res}

        elif(data["table"] == "ride"):
            if(data["columns"][0] == "id"):
                ride = Ride.query.filter_by(ride_id=data["values"][0]).first()
                if(ride is not None):
                    time = ride.timestamp
                    time = time.strftime("%d-%m-%Y:%S-%M-%H")
                    res = [ride.ride_id, ride.creator, time,
                           ride.source_id, ride.destination_id]
            else:
                time_now = datetime.now()
                rides = Ride.query.filter_by(
                    source_id=data["values"][0], destination_id=data["values"][1]).all()
                if(rides is not None):
                    for ride in rides:
                        time = ride.timestamp
                        if(time >= time_now):
                            time = time.strftime("%d-%m-%Y:%S-%M-%H")
                            res.append([ride.ride_id, ride.creator, time])
            response = {"results": res}
        elif(data["table"] == "share"):
            shares = Share.query.filter_by(ride_id=data["values"][0]).all()
            if(shares is not None):
                for share in shares:
                    res.append([share.ride_id, share.username])
                response = {"results": res}
        else:
            response = {"response": "Table Not Present"}
            status = 405

    else:
        response = {"response": "Method Not Supported"}
        status = 405

    return jsonify(response), status


if __name__ == "__main__":
    create_db()
    application.run()