from flask_sqlalchemy import SQLAlchemy
from flask import Flask,request,session,jsonify,abort
import json
import sqlite3
from sqlalchemy import Column, String, Integer
from datetime import datetime as dt
import requests
app = Flask(__name__)


db=SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer,autoincrement=True, primary_key = True)
    username = db.Column(db.String(32),index=True)
    password = db.Column(db.String(40))
    def __repr__(self):
        return self.username

class Ride(db.Model):
    __tablename__ = "rides"
    ride_id = db.Column(db.Integer,autoincrement=True, primary_key = True)
    created_by = db.Column(db.String(32),index=True)
    timestamp = db.Column(db.String(50))
    source = db.Column(db.String(40))
    destination = db.Column(db.String(40))
    def __repr__(self):
        return (self.created_by,
                self.timestamp,
                self.source,
                self.destination)

class JoinRide(db.Model):
    __tablename__="joinride"
    joinid = db.Column(db.Integer,autoincrement=True,primary_key=True)
    ride_id = db.Column(db.Integer,index=True)
    username = db.Column(db.String(32),index=True)
    def __repr__(self):
        (self.username,
        self.ride_id)


def connect_to_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rideshare.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] =False
    db.app = app
    db.init_app(app)


    
    
def sha(passwo):
    if len(passwo) != 40:
        return False
    try:
        sha1 = int(passwo,16)
    except ValueError:
        return False
    return True

@app.route('/api/v1/db/write',methods = ['POST'])
def write_to_db():
    op=request.get_json()["op"]
    if int(op)==1:  
        username = request.get_json()["username"]
        password = request.get_json()["password"]
        add_user = User(username=username,password=password)
        db.session.add(add_user)
        db.session.commit()
        s={}
        res=User.query.filter_by(username=username).first()
        if res == None:
            return "No"
        s["username"]=res.username
        return jsonify(s)
    if int(op)==2:
        created_by = request.get_json()["created_by"]
        timestamp = request.get_json()["timestamp"]
        source = request.get_json()["source"]
        destination = request.get_json()["destination"]
        add_ride = Ride(created_by=created_by,timestamp=timestamp,source=source,destination=destination)
        db.session.add(add_ride)
        db.session.commit()
        s={}
        res=Ride.query.filter_by(created_by=created_by).first()
        if res == None:
            return "No"
        s["created_by"]=res.created_by
        return jsonify(s)
    if int(op)==3:
        db.delete()
        db.session.commit()
    if int(op)==4:
        delete_ride.delete()
        delete_ride.session.commit()

    
    
@app.route('/api/v1/users', methods = ['PUT'])
def new_user():
    if (request.method=='PUT'):
        username=request.get_json()["username"]
        password=request.get_json()["password"]
        user_in_db = db.session.query(User).filter(User.username==username).all()
        if not user_in_db:
            check = sha(password)
            if check:
                query={"op":1,"username":username,"password":password}
                user = requests.post('http://0.0.0.0:80/api/v1/db/write',json=query)
                return jsonify({}),201
                
            else:
                return jsonify({}),400
        else:
            return jsonify({}),400
    else:
        return jsonify({}),405


@app.route('/api/v1/users', methods=['DELETE'])
def del_user():
    if (request.method=='DELETE'):
        username = request.args['username']
       
        user_in_db = db.session.query(User).filter(User.username==username)
        if str(user_in_db.first()) == username:
            user_in_db.delete()
            user_in_db.session.commit()
            return jsonify({}),200
        else:
            return jsonify({}),400
    else:
        return jsonify({}),405


@app.route('/api/v1/rides', methods = ['POST'])
def create_ride():
    if (request.method == 'POST'):
        created_by = request.get_json()["created_by"]
        timestamp = request.get_json()["timestamp"]
        source = request.get_json()["source"]
        destination = request.get_json()["destination"]
        user_in_db = db.session.query(User).filter(User.username==created_by).all()
        if user_in_db==None:
            return jsonify({}),400
        else:
            if source!=destination:
                query={"op":2,"created_by":created_by,"timestamp":timestamp,"source":source,"destination":destination}
                ride = requests.post('http://0.0.0.0:80/api/v1/db/write',json=query)
                return jsonify({}),201
            else:
                return jsonify({}),400
    else:
        return jsonify({}),405
    
@app.route('/api/v1/rides/<int:ride_id>', methods=['DELETE'])
def del_ride(ride_id):
    if(request.method=='DELETE'):
        delete_ride = db.session.query(Ride).filter(Ride.ride_id==ride_id)
        query = {"op":4}
        del_user = requests.post('http://0.0.0.0:80/api/v1/db/write',json={"query":query})
        return jsonify({}),200
    else:
            return jsonify({}),400

@app.route('/api/v1/rides/<int:ride_id>', methods=['GET'])
def details_ride(ride_id):
    if(request.method=='GET'):

        ride_details = db.session.query(Ride).filter_by(ride_id=ride_id).first()
        if ride_details==None:
            return jsonify({}),204
        else:
            s={}
            s["created_by"] = ride_details.created_by
            s["timestamp"] = ride_details.timestamp
            s["source"] = ride_details.source
            s["destination"] = ride_details.destination
            return jsonify(s),200
   
        
    else:
        return jsonify({}),405

@app.route('/api/v1/rides/<int:ride_id>',methods = ['POST'])
def join_ride(ride_id):
    if (request.method=='POST'):
        rideid_in_db = db.session.query(Ride).filter(Ride.ride_id==ride_id)
        if rideid_in_db==None:
            return jsonify({}),204
        else:
            username = request.get_json()["username"]
            user_in_db = db.session.query(User).filter(User.username==username).all()
            if not user_in_db:
                return jsonify({}),204
            else:
                new_user_ride = JoinRide(ride_id=ride_id,username=username)
                if JoinRide.joinid==ride_id:
                    return jsonify({}),400
                else:
                    db.session.add(new_user_ride)
                    db.session.commit()
                    s={}
                    res=JoinRide.query.filter_by(username=username).first()
                    if res == None:
                        return "No"
                    s["username"]=res.username
                    
                    return jsonify(s)
                    return jsonify({}),201
    else:
        return jsonify({}),405

@app.route('/api/v1/rides', methods=['GET'])
def upcoming_rides():
    if(request.method=='GET'):  
        args = request.args
        source=args['source']
        destination=args['destination']
        sd_in_db=db.session.query(Ride).filter(Ride.source==source and Ride.destination==destination).all()
        
        
        d=[]
        for i in sd_in_db:
            dt_time=dt.strptime(i.timestamp,"%d-%m-%Y:%S-%M-%H")
            if(dt_time>dt.now()):
                d.append({"ride_id":i.ride_id,"created_by":i.created_by,"timestamp":i.timestamp})
        return jsonify(d)








if __name__ == "__main__":

    #from server import app
    connect_to_db(app)
    db.create_all()
    print("connected to db")
    
    app.debug=True
    app.run(port=80,"0.0.0.0")


