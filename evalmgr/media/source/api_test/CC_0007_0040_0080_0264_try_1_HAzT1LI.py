import os
import flask
import json as j

import sqlalchemy as sql
import sqlalchemy.orm as orm
import flask_sqlalchemy_session as fss
from flask import abort, Response, request

from flask_sqlalchemy_session import current_session as s
from sqlalchemy.ext.declarative import declarative_base

from datetime import datetime
import requests
import traceback
import hashlib

Base = declarative_base()
app = flask.Flask(__name__)

#scp -i assignment1.pem -r Assignment1 user@ec2-3-93-153-150.compute-1.amazonaws.com:~

class UserTable(Base):
    __tablename__ = 'user_table'
    user_id = sql.Column(sql.Integer , autoincrement  = True, primary_key = True )
    user_name = sql.Column(sql.String(40), unique = True, nullable = False)
    user_password = sql.Column(sql.String(40), nullable = False)

    User_Rides = orm.relationship("RideTable" , cascade = "all,delete")
    Ongoing_rides = orm.relationship("RideUsersTable" , cascade = "all,delete")

    def write_to_db(self):
        s.add(self)
        s.commit()
    
    def read_from_db(self):
        s.delete(self)
        s.commit()
    
    def delete_from_db(self):
        s.delete(self)
        s.commit()
    
    @staticmethod
    def query_db(name_user):
        #return the User_class table
        obj = s.query(UserTable)
        #returns one if username exists, otherwise zero.
        unames = obj.filter(UserTable.user_name == name_user).one_or_none() 
        return unames

    @staticmethod
    def get_from_request(body):
        return UserTable(user_name=body['username'], user_password=body['password'])
    
    @staticmethod
    def get_json(body):
        if 'username' not in body:
            abort(400, 'username is not present')
        if 'password' not in body:
            abort(400, 'password is not present')
        
        sha_obj = hashlib.sha1((str(body["password"])).encode('utf-8'))
        res = sha_obj.hexdigest()
        return {"username" : body["username"] , "password" : res}


class RideTable(Base):
    __tablename__ = 'ride_user_table'
    ride_id = sql.Column(sql.Integer, primary_key=True, autoincrement=True)
    created_by = sql.Column(sql.String(80), sql.ForeignKey(
        "user_table.user_name"), nullable=False)
    source = sql.Column(sql.Integer, nullable=False)
    destination = sql.Column(sql.Integer, nullable=False)
    timestamp = sql.Column(sql.DateTime, nullable=False)
    ride_users = orm.relationship("RideUsersTable", cascade="all,delete")

    def write_to_db(self):
        s.add(self)
        s.commit()
        return self.ride_id

    def delete_from_db(self):
        s.delete(self)
        s.commit()

    @staticmethod
    def list_upcoming_rides(source, destination):
        return s.query(RideTable).filter(RideTable.source == source)\
        .filter(RideTable.destination == destination)\
        .filter(RideTable.timestamp >= datetime.now())\
        .all()

    @staticmethod
    def read_from_db(ride_id):
        return s.query(RideTable).get(ride_id)

    @staticmethod
    def read_from_username(username):
        return s.query(RideTable).filter(RideTable.created_by == username).one_or_none()

    @staticmethod
    def get_from_ride_id(ride_id):
        return s.query(RideTable).filter(RideTable.ride_id == ride_id).one_or_none()        

    @staticmethod
    def validateSrc(src):
        if(int(src) >=1 and int(src) <=198):
            return src
        else:
            return "error"
    
    @staticmethod
    def validateDst(dst):
        if(int(dst) >=1 and int(dst) <=198):
            return dst
        else:
            return "error"

    @staticmethod
    def validateTimestamp(tz):
        try:
            return datetime.strptime(tz, "%d-%m-%Y:%S-%M-%H")
        except:
            abort(400, "invalid timestamp %s format. format is DD-MM-YYYY:SS-MM-HH" % (tz))
        return tz

    
    @staticmethod
    def get_from_request(body):
        return RideTable(created_by=body['username'],\
            source=RideTable.validateSrc(body['source']),\
                destination=RideTable.validateDst(body['destination']),\
                    timestamp=RideTable.validateTimestamp(body['timestamp']))
    
    @staticmethod
    def get_json(body):
        if 'destination' not in body:
            abort(400, 'destination not passed in the request')
        if 'timestamp' not in body:
            abort(400, 'timestamp not passed in the request')
        if 'created_by' not in body:
            abort(400, 'created_by not passed in the request')
        if 'source' not in body:
            abort(400, 'source not passed in the request')

        RideTable.validateTimestamp(body['timestamp'])

        json_dict = {"username" : body['created_by'],\
            "source" : RideTable.validateSrc(body['source']),\
                "destination" : RideTable.validateDst(body['destination']),\
                    "timestamp" : body['timestamp']}
            
        return json_dict



class RideUsersTable(Base):
    __tablename__ = 'ride_users_table'
    ride_users_id = sql.Column(sql.Integer, primary_key=True, autoincrement=True)
    ride_table_id = sql.Column(sql.Integer, sql.ForeignKey("ride_user_table.ride_id"), nullable=False)
    user_table_name = sql.Column(sql.String(40), sql.ForeignKey(
        "user_table.user_name"), nullable=False)

    @staticmethod
    def read_from_db(ride_id):
        return s.query(RideUsersTable).filter(RideUsersTable.ride_table_id == ride_id).all()

    def write_to_db(self):
        s.add(self)
        s.commit()
        return self.ride_table_id

    def delete_from_db(self):
        s.delete(self)
        s.commit()


def check_content_type(req):
    if not req.is_json:
        abort(400, 'Content-Type unrecognized')

def myconverter(o):
    if isinstance(o, datetime.datime):
        return o.__str__()

@app.route("/api/v1/users", methods={'PUT'})
def add_user():
    check_content_type(request)

    json_format = UserTable.get_json(request.json)
    json_format["action"] = "get_user"
    r = requests.post("http://127.0.0.1:5000/api/v1/db/read" , json = json_format)

    if(r.status_code == 200):
        abort(400 , 'user %s already exists' % (json_format['username']))
    
    else:
        json_format["action"] = "write_user"
        r = requests.post("http://127.0.0.1:5000/api/v1/db/write" , json = json_format)
        if(r.status_code == 201):
            return Response(None, status=201, mimetype='application/json')
        else:
            abort(500 , "Internal Server Error")




@app.route("/api/v1/users/<user_name>", methods={'DELETE'})
def delete_user(user_name):

    #check_content_type(request)

    json_format = dict()
    json_format["username"] = user_name
    json_format["action"] = "delete_user"

    r = requests.post("http://127.0.0.1:5000/api/v1/db/read" , json = json_format)

    if(r.status_code == 400): #user was not found
        abort(400 , 'user %s does not exists' % (user_name))
    else:
        r = requests.post("http://127.0.0.1:5000/api/v1/db/write" , json = json_format)
        if(r.status_code == 200):
            return Response(None, status=200, mimetype='application/json')
        else:
            abort(500 , "Internal Server Error")
    

@app.route("/api/v1/rides", methods={'POST'})
    
def ride_add():

    check_content_type(request)

    json_format = RideTable.get_json(request.json)
    
    if(json_format["source"] != json_format["destination"]):
        json_format["action"] = "get_user"

        j_one = json_format

        r = requests.post("http://127.0.0.1:5000/api/v1/db/read" , json = j_one)
    #print (r.text)
        if(r.status_code == 400):
            abort(400 , 'user %s does not exists' % (json_format["username"]))
        else:
            j_one["action"] = "write_ride"
            r = requests.post("http://127.0.0.1:5000/api/v1/db/write" , json = j_one)
            if(r.status_code == 201):
                return Response(None, status=200, mimetype='application/json')
            else:
                abort(500 , "Internal Server Error")
    else:
        abort(400 , "souce and destination cannot be same")

@app.route("/api/v1/rides", methods={'GET'})
def all_upcoming_rides():
    src = request.args.get("source")
    dst = request.args.get("destination")
    if(src != dst):
        src = RideTable.validateSrc(src)
        dst = RideTable.validateDst(dst)
        if(src == "error"):
            abort(400 , "invalid source passed")
        elif(dst == "error"):
            abort(400 , "invalid destination passed")
        else:
            json_format = dict()
            json_format["action"] = "upcoming_rides"
            json_format["source"] = src
            json_format["destination"] = dst
            r = requests.post("http://127.0.0.1:5000/api/v1/db/read" , json = json_format)
            if(r.status_code == 204):
                return Response(None , status = 204 , mimetype='application/json')
            else:
                dic = j.loads(r.text)
                return Response(j.dumps(dic , indent=4) , status=200 , mimetype='application/json')
    else:
        abort(400 , "souce and destination cannot be same")

@app.route("/api/v1/rides/<int:ride_id>", methods={'GET'})
def ride_info(ride_id):
    json_format = dict()
    json_format["ride_id"] = ride_id
    json_format["action"] = "ride_info"
    r = requests.post("http://127.0.0.1:5000/api/v1/db/read" , json = json_format)
    if(r.status_code == 204):
        return Response(None, status=204, mimetype='application/json')
    if(r.status_code == 200):
        dic = j.loads(r.text)
        return Response(j.dumps(dic , indent=4) , status=200 , mimetype='application/json')
    else:
        traceback.print_exc()
        abort(500 , "internal server error")


@app.route("/api/v1/rides/<int:ride_id>", methods={'POST'})
def join_ride(ride_id):
    if("username" not in request.json):
        abort(400 , "username not passed")
    json_format = dict()
    json_format["username"] = request.json["username"]
    json_format["ride_id"] = ride_id

    json_format["action"] = "get_user"
    r = requests.post("http://127.0.0.1:5000/api/v1/db/read" , json = json_format)
    if(r.status_code == 400):
       abort(400 , 'user %s does not exists' % (json_format["username"]))

    json_format["action"] = "ride_info"
    r = requests.post("http://127.0.0.1:5000/api/v1/db/read" , json = json_format)
    if(r.status_code == 204):
        return Response(None , status=204 , mimetype='application/json')
    
    json_format["action"] = "join_ride"
    r = requests.post("http://127.0.0.1:5000/api/v1/db/write" , json = json_format)
    if(r.status_code == 200):
        return Response(None, status=200, mimetype='application/json')
    else:
        abort(500 , "Internal Server error")

@app.route("/api/v1/rides/<int:ride_id>", methods={'DELETE'})
def del_ride(ride_id):
    json_format = dict()
    json_format["ride_id"] = ride_id

    json_format["action"] = "ride_info"
    r = requests.post("http://127.0.0.1:5000/api/v1/db/read" , json = json_format)
    if(r.status_code == 204):
        return Response(None , status=204 , mimetype='application/json')

    json_format["action"] = "delete_ride"
    r = requests.post("http://127.0.0.1:5000/api/v1/db/write" , json = json_format)

    if(r.status_code == 200):
        return Response(None, status=200, mimetype='application/json')
    else:
        abort(500 , "Internal Server Error")
    

#ALL READ WRITE API CALLS FROM HERE:

@app.route("/api/v1/db/read" , methods={'POST'})
def read():
    body = request.get_json()
    action = body["action"]
    if(action == "get_user"):
        ret_val = UserTable.query_db(body["username"])
        if ret_val is None:
            abort(400, "user not found")
        d = {"username" : ret_val.user_name , "pswd" : ret_val.user_password}
        return Response(j.dumps(d), status=200, mimetype='application/json')
    
    elif(action == "delete_user"):
        ret_val = UserTable.query_db(body["username"])
        if(ret_val is None):
            abort(400 , "not found")
        return Response(None , status= 200 , mimetype='application/json')
    
    elif(action == "upcoming_rides"):
        rides  = RideTable.list_upcoming_rides(body["source"] , body["destination"])
        response = list()
        if(rides is not None and len(rides) > 0):
            for ride in rides:
                users = list()
                for u in RideUsersTable.read_from_db(ride.ride_id):
                    users.append(u.user_table_name)
                response.append({"ride_id": ride.ride_id, "username": users,
                                 "timestamp": ride.timestamp.strftime("%d-%m-%Y:%S-%M-%H")})
            return Response(j.dumps(response, indent=4), status=200, mimetype='application/json')
        else:
            return Response(None, status=204, mimetype='application/json')
    
    elif(action == "ride_info"):
        try:
            ride = RideTable.read_from_db(body["ride_id"])
            if(ride is None):
                return Response(None , status=204 , mimetype='application/json')
            else:
                users = list()
                all_riders = RideUsersTable.read_from_db(ride.ride_id)
                for u in all_riders:
                    users.append(u.user_table_name)
                #obj = RideTable.get_from_ride_id(ride.ride_id)
                response = dict()
                response["ride_id"] = ride.ride_id
                response["created_by"] = ride.created_by
                response["users"] = users
                response["timestamp"] = ride.timestamp.strftime("%d-%m-%Y:%S-%M-%H")
                response["source"] = ride.source
                response["destination"] = ride.destination
                return Response(j.dumps(response , indent=4) , status=200 , mimetype='application/json')
        except:
            abort(500 , "Internal Server error")



    
@app.route("/api/v1/db/write" , methods={'POST'})
def write():
    body = request.get_json()
    action = body["action"]
    if(action == "write_user"):
        UserTable.get_from_request(body).write_to_db()
        return Response(None, mimetype="application/json", status=201)


    elif(action == "delete_user"):
        UserTable.query_db(body["username"]).delete_from_db()
        return Response(None, mimetype="application/json", status=200)


    elif(action == "write_ride"):
        ride_request = RideTable.get_from_request(body)
        ride_id = ride_request.write_to_db()#Returns the incremented ride id.
        ride_table_id = RideUsersTable(user_table_name=ride_request.created_by, ride_table_id=ride_id).write_to_db()
        return Response(j.dumps({"ride_id": ride_id}), status=201, mimetype='application/json')

    elif(action == "join_ride"):
        RideUsersTable(user_table_name=body["username"], ride_table_id=body["ride_id"]).write_to_db()
        return Response(None, status=200, mimetype='application/json')
    
    elif(action == "delete_ride"):
        RideTable.read_from_db(body['ride_id']).delete_from_db()
        return Response(None, status=200, mimetype='application/json')



if __name__ == "__main__":
    e = sql.create_engine("sqlite:///{}".format(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "riders.db")))
    Base.metadata.create_all(e, checkfirst=True)    
    sf = orm.sessionmaker(bind=e)
    s = fss.flask_scoped_session(sf, app)
    app.run(debug=True)