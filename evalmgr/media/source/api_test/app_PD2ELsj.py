from flask import Flask,request, jsonify,render_template,abort, session,Response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import datetime 
import os
import re
import requests
import hashlib 
from sqlalchemy.sql import select,exists
from sqlalchemy.orm import load_only
import csv
import sys, time
#from datetime import datetime


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'rideshare.db')
db = SQLAlchemy(app)
ma = Marshmallow(app)


class User(db.Model):

    __tablename__ = "user"

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(128))
    posts = db.relationship('UserRide', backref='user', lazy='dynamic')
    ride = db.relationship('Ride', secondary= 'user_ride', backref='user')

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def serialize(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'password':self.password}


class Ride(db.Model):

    __tablename__ = "ride"

    ride_id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    created= db.Column(db.String(50), nullable=False)
    src_adr= db.Column(db.String(50), nullable=False)
    dest_adr = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.String(50))

    def serialize(self):
        #return "<Ride ride_id=%s created=%s source_adr=%s dest_adr=%s timestamp=%s>" % (self.ride_id, self.created,
        #                                        self.src_adr,self.dest_adr,self.timestamp)
        return {
        'ride_id':self.ride_id,
        'created':self.created,
        'src_adr':self.src_adr,
        'dest_adr':self.dest_adr,
        'timestamp':self.timestamp
        }

class UserRide(db.Model):

    __tablename__ = "user_ride"

    user_ride_id = db.Column(db.Integer,
                          autoincrement=True,
                          primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    ride_id = db.Column(db.Integer, db.ForeignKey("ride.ride_id"), nullable=False)
    ride = db.relationship('Ride', uselist=False) 


    def __repr__(self):
        s = "<UserRide user_ride_id=%s user_id=%s ride_id=%s >"
        return s % (self.user_ride_id, self.user_id, self.ride_id)

class joinRide(db.Model):
    __tablename__ = "userdetails"

   
    user_ride_id = db.Column(db.Integer,
                          autoincrement=True,
                          primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    ride_id = db.Column(db.Integer, db.ForeignKey("ride.ride_id"), nullable=False)
    ride = db.relationship('Ride', uselist=False)  

    def serialize(self):
        return {
        'user_ride_id':self.user_ride_id,
        'username':self.username,
        'ride_id':self.ride_id
        
        }

def connect_to_db(app):

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rideshare.db'
    db.app = app
    db.init_app(app)


class DataDisplay(ma.Schema):
    class Meta:
        fields = ('username','password','user_id','ride_id','created','src_adr','dest_adr','timestamp')


data_display = DataDisplay()
datas_display = DataDisplay(many=True)

def formatTheDate(s):    
    line=s.split(" ")
    yymmdd=line[0].split('-')
    hhms=line[1].split(':')
    yy=yymmdd[0]
    mm=yymmdd[1]
    dd=yymmdd[2]
    hh=hhms[0]
    m=hhms[1]
    s=str(int(float(hhms[2])))
    return(dd+'-'+mm+'-'+yy+':'+s+'-'+m+'-'+hh)
    

def is_in_format(s):
    if(re.match(r'[0-3]{2}-[0-9]{2}-[0-9]{4}:[0-5][0-9]-[0-5][0-9]-[0-5][0-9]',s) is None):
        return 0
    else:
        return 1

def checkingArea(num):
    file=open("AreaNameEnum.csv","r")
    line={}
    i=0;
    for lines in file:
        if i==0:
            i+=1
        else:
            l=lines.split(',')
            line[int(l[0])]=int(l[0])
    file.close()
    return (num in line)

def isupcoming(data1,data2):
    line1=data1.split(':')
    line2=data2.split(':')
    date1=line1[0]
    time1=line1[1]
    date2=line2[0]
    time2=line2[1]
    result=comparewithdate(date1,date2)
    if(result==1):
        return True
    elif result==0:
        return comparewithtime(time1,time2)
    else:
        return False

def comparewithtime(time1,time2):
    arg1=time1.split('-')
    arg2=time2.split('-')
    l=list(zip(arg1,arg2))
    l.reverse()
    for(j,i) in l:
        i=int(i)
        j=int(j)
        if(i>j):
            return True
        elif i<j:
            return False
def comparewithdate(date1,date2):
    ddmmyy1=date1.split('-')
    ddmmyy2=date2.split('-')
    result=-1
    l=list(zip(ddmmyy1,ddmmyy2))
    l.reverse()
    for(j,i) in l:
        i=int(i)
        j=int(j)
        if(i>j):
            result=1
            break
        elif i==j:
            result=0
        else:
            result=-1
            break
    return result

#api 1 completed 
@app.route("/api/v1/users", methods=["PUT"])
def add_user():
    if (request.method=="PUT"):
        _username = request.json['username']
        _password = request.json['password']
        result = hashlib.sha1(_password.encode()) 
        pwd=result.hexdigest()

        mydict={"table":"user","column":"username","where":"username","data":_username}
        res=requests.post(url="http://127.0.0.1:8000/api/v1/db/read", json=mydict)
        if res.status_code == 200:
            return Response(status=400)
        if res.status_code == 204:
            if(re.match(r'[0-9a-fA-F]{40}$',_password) is None):
                return jsonify({"flag":"password mismatch"}),400
            else:
                sqlquery={"insert":[_username,pwd],"table":"user","query":"insert"}
                data=requests.post(url="http://127.0.0.1:8000/api/v1/db/write", json=sqlquery)
                return jsonify({}),201
    else:
        return Response(status=405)
    
#api 2 completed
@app.route("/api/v1/users/<username>", methods=["DELETE"])
def user_delete(username):
    if(request.method=="DELETE"):
        #userr=User.query.get(username)
        mydict={"table":"user","column":"username","where":"username","data":username}
        res = requests.post(url="http://127.0.0.1:8000/api/v1/db/read", json=mydict)
        if (res.status_code==200):
            sqlquery={"insert":username,"table":"user","query":"delete"} #first ride will be deleted and then user will be removed
            result=requests.post(url="http://127.0.0.1:8000/api/v1/db/write", json=sqlquery)
            if (result.status_code==200):
            	try:
            		existing_user1 = joinRide.query.filter(joinRide.username == username).first() #to delete user who has joined existing ride
            		db.session.delete(existing_user1)
            		db.session.commit()
            	except:
            		return jsonify({}),200
            else:
                return Response(status=204)
        else:
            return Response(status=204)
    else:
        return Response(status=405)
#api 3 done completed
@app.route("/api/v1/rides",methods=["POST"])
def create_ride():
    if(request.method=="POST"):
        createdby = request.json['created_by']
        src = request.json['source']
        dest = request.json['destination']
        timestamp= request.json['timestamp']
        #date_time ="%d-%m-%Y:%S-%M-%H"
        #timeformat = datetime.strptime(timestamp, date_time)

        if (is_in_format(timestamp)):
            if((checkingArea(src)) and  (checkingArea(dest)) and (src != dest)):
                mydict={"table":"user","column":"username","where":"username","data":createdby} #checking if usr already exst
                res=requests.post(url="http://127.0.0.1:8000/api/v1/db/read", json=mydict)
                if res.status_code==200: #if exist then we create ride for particular user
                    sqlquery={"insert":[createdby,src,dest,timestamp],"query":"insert", "table":"ride"}
                    data=requests.post(url="http://127.0.0.1:8000/api/v1/db/write", json=sqlquery) 
                    if data.status_code==201:
                        return jsonify({}),201
                    else:
                        return Response(status=204)
                else: 
                    return Response(status=400)
                        
            else:
                return Response(status=400)
        else:
            return Response(status=400)
    else:
        return Response(status=405)

 
#api 4 incomplete
@app.route("/api/v1/rides",methods=["GET"])
def ride_details():
        if request.method=="GET":
            src=int(request.args.get("source"))
            dest=int(request.args.get("destination"))
            tm=formatTheDate(str(datetime.datetime.now()))
            if( (checkingArea(src)) and  (checkingArea(dest)) and (src != dest)):
                query=db.session.execute('select ride_id,created,timestamp from ride where src_adr={} and dest_adr={}'.format(src,dest))
                #res=datas_display.dump(query)
                #print(res)

                list_ = []
                for record in query:
                    recordObject = {}
                    recordObject["ride_id"]=record[0]
                    recordObject["created"]=record[1]
                    if(isupcoming(tm,record[2])):
                        recordObject["time"]=record[2]
                        list_.append(recordObject)
                if len(list_)!=0:
                    return jsonify(list_),200
                else:
                    return {},204
            
        else:
            return {},405
    


#api 5 completed
@app.route("/api/v1/rides/<rideId>",methods=["GET"])
def list_ride(rideId):
    if(request.method=="GET"):
        existing_user = Ride.query.filter(Ride.ride_id == rideId).first()
        if existing_user:
            userlist=db.session.execute('select username from userdetails where ride_id={}'.format(rideId))
            res=datas_display.dump(userlist)
            records = db.session.execute('select ride_id,created,src_adr,dest_adr,timestamp from ride where ride_id={}'.format(rideId))
            for record in records:
                recordObject = { 'ride_id':record.ride_id,
                'created_by': record.created,
                        'source': record.src_adr,
                        'users':[],
                        'destination': record.dest_adr,
                        'timestamp': record.timestamp}

            for names in res:
                recordObject["users"].append(names["username"])
            #recordObject['users'].append(user)

            return jsonify(recordObject),200
        else:
            return Response(status=204)

    else:
        return Response(status=405)

#api 6 completed
@app.route("/api/v1/rides/<rideId>",methods=["POST"])
def join_ride(rideId):
    if(request.method=="POST"):
        usern=request.json['username']
        myid={"table":"ride","column":"ride_id","where":"ride_id","data":rideId} #to check if ride exist
        num=requests.post(url="http://127.0.0.1:8000/api/v1/db/read", json=myid)
        if (num.status_code == 200):
            mydict={"table":"user","column":"username","where":"username","data":usern} #to check if user exist
            res=requests.post(url="http://127.0.0.1:8000/api/v1/db/read", json=mydict)
            if(res.status_code==200):
                createdby=db.session.execute('select created from ride where ride_id={}'.format(rideId)).first()
                
                if(createdby[0] != usern):
                    sql={"insert":[usern,rideId],"table":"userdetails", "query":"insert"}
                    req=requests.post(url="http://127.0.0.1:8000/api/v1/db/write", json=sql) #adding users to join ride
                    if (req.status_code==201):
                        return jsonify({}),201
                    else:
                        return Response(status=204)
                else:
                    return {},400
            else:
                  return Response(status=400)
        else:
            return Response(status=204)
    else:
        return Response(status=405)

#api 7 completed
@app.route("/api/v1/rides/<id>",methods=["DELETE"])
def delete_ride(id):
    if(request.method=="DELETE"):
        #rides=Ride.query.get(riid)
        mydict={"table":"ride","column":"ride_id","where":"ride_id","data":id}
        data = requests.post(url="http://127.0.0.1:8000/api/v1/db/read", json=mydict) #checks if ride exist
        if (data.status_code==200):
            sqlquery={"insert":id, "table":"ride","query":"delete"}
            res=requests.post(url="http://127.0.0.1:8000/api/v1/db/write", json=sqlquery) 
            if res.status_code==200:
            	return Response(status=200)
            else:
            	return Response(status=204)
        else:
        	return Response(status=204)   
    else:
        return Response(status=405)

#api 8 completed
@app.route("/api/v1/db/write", methods=["POST"])
def write_to_db():
    if(request.method=="POST"):
        insert=request.json['insert']
        table=request.json['table']
        query=request.json['query']
        if(query=="insert"):
            if(table=="user"):
                user="{}".format(insert[0])
                pwd="{}".format(insert[1])
                useradd = User(username=user,password=pwd)
                db.session.add(useradd)
                db.session.commit()
                return data_display.jsonify(useradd)

            if(table=="ride"):
                _createdby="{}".format(insert[0])
                src="{}".format(insert[1])
                dest="{}".format(insert[2])
                timestamp="{}".format(insert[3])
                new_ride = Ride(created=_createdby,src_adr=src,dest_adr=dest,timestamp=timestamp)
                db.session.add(new_ride)
                db.session.commit()
                return Response(status=201) 
            if(table=="userdetails"):
                usern="{}".format(insert[0])
                rideid="{}".format(insert[1])
                new_ride = joinRide(username=usern, ride_id=rideid)
                db.session.add(new_ride)
                db.session.commit()
                return Response(status=201) 
            


        if(query=="delete"):
            if(table=="user"):
                existing_user = User.query.filter(User.username == insert).first()
                if existing_user:
                	try:
                		new2=Ride.query.filter(Ride.created ==  insert).first()
                		db.session.delete(new2)
                	except:
                		db.session.delete(existing_user)
                		db.session.commit()
                		return Response(status=200)
                	else:
                		return Response(status=400)
            if(table=="ride"):
                existing_user = Ride.query.filter(Ride.ride_id == insert).first()
                if existing_user:
                    db.session.delete(existing_user)
                    db.session.commit()
                    return Response(status=200)
                else:
                    return abort(400)
            if(table=="userdetails"):
                existing_user = joinRide.query.filter(joinRide.username == insert).first()
                if existing_user:
                    db.session.delete(existing_user)
                    db.session.commit()
                    return Response(status=200)
                else:
                    return Response(status=400)
    else:
        return Response(status=405)

#api 9 completed
@app.route("/api/v1/db/read", methods=["POST"])
def read_db():
    if(request.method=="POST"):
        table=request.get_json()['table']
        column=request.get_json()['column']
        where=request.get_json()['where']
        data=request.get_json()['data']
        if (where=="*"):
            if (table == "user"):
                #sql= "select "+ column +"from "+ table 
                sql= db.session.query(User.username)
                result = datas_display.dump(sql)
                if result:
                    return jsonify(result)
                else:
                    return Response(status=204)
               
            if (table== "ride"):
                sql= Ride.query.all()
                result = datas_display.dump(sql)
                if result:
                    return jsonify(result)
                else:
                    return Response(status=204)

        if(table=="userdetails"):
            all_ride = joinRide.query.all()
            result = datas_display.dump(all_ride)
            if result:
                return jsonify(result)
            else:
                return Response(status=204)


        if (where=="ride_id"):
            if(table=="ride"):
                if data:
                    existing_user = Ride.query.filter(Ride.ride_id == data).first()
                    if existing_user:
                        return Response(status=200)
                    else:
                        return Response(status=204)
                else:
                    return Response(status=400)
        if (where == "username"):
            if data:
                existing_user = User.query.filter(User.username == data).first()
            if existing_user:
                return Response(status=200)
            else:
                return Response(status=204)
    else:
        return Respone(405)


        
if __name__ == "__main__":
    app.debug = True
    app.run()
