from flask import Flask, Request, jsonify,request ,  Response,json , url_for
from collections import defaultdict
import csv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.attributes import flag_modified
#from sqlalchemy.types import *
from flask_marshmallow import Marshmallow
from sqlalchemy import PickleType
#import os
#from crud import *
import datetime
import requests
import tldextract
import re
from datetime import datetime
from datetime import date
app = Flask(__name__)
#basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///CC_0024_0162_1618_1640_app.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
dab = SQLAlchemy(app)
ma = Marshmallow(app)


class User(dab.Model):
    #id = dab.Column(dab.Integer, primary_key=True)
    username = dab.Column(dab.String(),primary_key=True)
    password = dab.Column(dab.String())

    def __init__(self, username, password):
        self.username = username
        self.password = password

class UserSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('username', 'password')


user_schema = UserSchema()
users_schema = UserSchema(many=True)


class Ride(dab.Model):
    rideId=dab.Column(dab.Integer(),primary_key=True)
    created_by=dab.Column(dab.String())
    source=dab.Column(dab.Integer())
    destination=dab.Column(dab.Integer())
    timestamp=dab.Column(dab.String())
    riders=dab.Column(dab.PickleType())
    #users = dab.Column(dab.String())

    def __init__(self,created_by,source,destination,timestamp,riders=[]):
        self.created_by=created_by
        self.source=source
        self.destination=destination
        self.timestamp=timestamp
        self.riders=riders
        #self.users=users

class RideSchema(ma.Schema):
    class Meta:
        fields=('created_by','source','destination','timestamp','riders')

ride_schema=RideSchema()
rides_schema=RideSchema(many=True)

dab.create_all()

'''def myconverter(o):
    if isinstance(o, datetime):
        return o.__str__()'''
def check(number1,number2):
    lis=[]
    for i in range(1,199):
        lis.append(i)
    if int(number1) in lis and  int(number2) in lis:
        return True
    else:
        return False

def converter(string):
    arr=string.split(',')
    arr1=arr[0].split('/')
    arr2=arr[1].split(':')
    date=arr1[1]+"-"+arr1[0]+"-"+arr1[2]+":"+arr2[2]+"-"+arr2[1]+"-"+(arr2[0]).strip(" ") 
    return str(date)

@app.route("/api/v1/users" ,methods=["PUT"])
def add_user():
    dic = {}
    dictt={}
    dictt["some"] = "adduser"
    dictt['username'] = request.json['username']
    url="http://0.0.0.0:80/api/v1/db/read"
    #data = {'username':"gagana","password":"dskjf85u6i"}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(url, json = dictt, headers=headers)
    #return r.text
    password = request.json['password']
    pattren = re.compile('^[0-9a-f]{40}$')
    matches = pattren.match(password)
    if r.text != "None":
        return jsonify({}),400
    if not re.match(pattren,password):
        return jsonify({}),400
    else:
        dic["username"] = request.json['username']
        dic["password"] = request.json['password']
        username = request.json['username']
        dic["some"] = "user"
        url="http://0.0.0.0:80/api/v1/db/write"
        #data = {'username':"gagana","password":"dskjf85u6i"}
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = requests.post(url, json = dic, headers=headers)
        return jsonify({}),201
@app.route("/api/v1/users/<username>", methods=["DELETE"])
def user_delete(username):
    dictt={}
    dictt["some"] = "adduser"
    dictt['username'] = username
    url="http://0.0.0.0:80/api/v1/db/read"
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(url, json = dictt, headers=headers)
    if r.text=="None":
        return jsonify({}),400
    else:
        url="http://0.0.0.0:80/api/v1/db/write"
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        res = requests.post(url, json = dictt, headers=headers)
        return jsonify({}),200

'''@app.route("/api/v1/rides", methods=["POST"])
def new_ride():
    dic = {}
    dictt={}
    dictt["some"] = "adduser"
    dictt['username'] = request.json['created_by']
    url="http://0.0.0.0:80/read"
    #data = {'username':"gagana","password":"dskjf85u6i"}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(url, json = dictt, headers=headers)
    #return r.text
    if r.text=="None":
        return jsonify({}),404
    else:
        num1=request.get_json()["source"]
        num2=request.get_json()["destination"]
        if(check(num1,num2)):
            
            dic["created_by"]=request.get_json()["created_by"]
            dic["source"]=request.get_json()["source"]
            dic["destination"]=request.get_json()["destination"]
            dic["timestamp"]=request.get_json()["timestamp"]
            dic["some"] = "rides"
            dic['riders'] = request.get_json()['riders']
            url="http://0.0.0.0:80/write"
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            r = requests.post(url, json = dic, headers=headers)
            return r.text
        elif num1==num2:
            return jsonify({}),202
            
        else:
            return jsonify({}),400

'''

'''def myconverter(o):
    if isinstance(o, datetime):
        return o.__str__()'''
@app.route("/api/v1/rides", methods=["POST"])
def new_ride():
    dic = {}
    dictt={}
    dictt["some"] = "adduser"
    url="http://0.0.0.0:80/api/v1/db/read"
    s = request.get_json()["created_by"]
    dictt['username'] = s
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(url, json = dictt, headers=headers)
    if r.text=="None":
        return jsonify({"f":"first"}),400
    else:
        num1=request.get_json()["source"]
        num2=request.get_json()["destination"]
        if num1==num2:
            return jsonify({"s":"d"}),400
        elif(check(num1,num2)):
	    
            dic["created_by"]=request.get_json()["created_by"]
            dic["source"]=request.get_json()["source"]
            dic["destination"]=request.get_json()["destination"]
            time = request.get_json()["timestamp"]   
            arr=time.split(":")
            da=[]
            for i in arr:
                da.append(i.split('-'))
            pa = re.compile("^[0-9][0-9]\-[0-9][0-9]\-[0-9][0-9][0-9][0-9]\:[0-9][0-9]\-[0-9][0-9]\-[0-9][0-9]$")
            #pattre=re.compile(r'^\d{2}-\d{2}-\d{4}:\d{2}-\d{2}-\d{2}+$')
            #matches = pa.match(time)
            try:
                if re.match(pa,time):
                    d  = datetime(int(da[0][2]),int(da[0][1]),int(da[0][0]),int(da[1][2]),int(da[1][1]),int(da[1][0])) 
                    dtime = d.strftime("%m/%d/%Y, %H:%M:%S")
                    dic['timestamp'] = dtime
                    #dic["timestamp"]= json.dumps(d, default = myconverter)
                    dic["some"] = "rides"
                    dic['riders'] = []
                    #dictt=json.dumps(dic, default = myconverter)
                    url="http://0.0.0.0:80/api/v1/db/write"
                    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
                    r = requests.post(url, json = dic, headers=headers)
                    return jsonify({}),201 
                else:
                    return jsonify({"f":"df"}),400       
            except ValueError:
                return jsonify({"f":"fdf"}),400
        else:
            return jsonify({"h":"a"}),400


@app.route("/api/v1/rides", methods=["GET"])
def list_details():
    source = request.args.get('source')
    destination = request.args.get('destination')
    if(source==destination):
        return jsonify({}),400
    elif(check(source,destination)):
        dicto ={}
        dicto['source']  = source
        dicto['destination'] = destination
        dicto['some'] = 'list'
        url="http://0.0.0.0:80/api/v1/db/read"
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = requests.post(url,json = dicto ,headers = headers)
        if r.text=="None":
            return jsonify({}),204
        else:
            return r.text
    else:
        return jsonify({}),400
        


@app.route("/api/v1/rides/<rideId>",methods=["GET"])
def get_details(rideId):
    #rideid = request.args.get('rideId')
    #ride=Ride.query.get(rideId)
    #if(ride):
    data = {}
    data['rideId'] = rideId
    data['some'] = 'ridesid'
    url="http://0.0.0.0:80/api/v1/db/read"
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(url,json=data,headers = headers)
    #return r.text
    x=r.json()
    if(not x):
        return jsonify({}),204
    else:
        dumb={}
        dit={}
        dit["some"]="get_details"
        dit["riders"]=r.json()["riders"]
        url="http://0.0.0.0:80/api/v1/db/read"
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        res = requests.post(url,json=dit,headers = headers)
        dumb["rideId"]=rideId
        dumb["created_by"]=r.json()["created_by"]
        li=r.json()["riders"]
        dumb["users"]=res.json()
        dumb["timestamp"]=converter(r.json()["timestamp"])
        dumb["source"]=str(r.json()["source"])
        dumb["destination"]=str(r.json()["destination"])
        return dumb
        #return res.text
@app.route("/api/v1/rides/<rideId>",methods=["POST"])
def join_ride(rideId):
    data = {}
    dic={}
    #ride=Ride.query.get(rideId)
    
    username = request.json['username']    
    dic['username'] = username
    dic['rideId'] = rideId
    dic['some'] = "join_ride"
    url="http://0.0.0.0:80/api/v1/db/read"
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(url,json = dic ,headers = headers)
    #return str(type(r.text))
    x=r.json()
    if(str(x["exists"])=="None" or str(x["user_exists"])=="None"):
        return jsonify({}),400
    else:
        data['some'] = 'join_rides'
        data['rideId'] = rideId
        data['username'] = username
        url="http://0.0.0.0:80/api/v1/db/write"
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = requests.post(url,json = data ,headers = headers)   
        if(r.text=="creator" or r.text=="already added"):
            return jsonify({}),400
        else:
            return jsonify({}),200
          


@app.route("/api/v1/rides/<rideId>", methods=["DELETE"])
def ride_delete(rideId):
    dic = {}
    dic['rideId'] = rideId
    dic['some'] = "delete_ride"
    url="http://0.0.0.0:80/api/v1/db/read"
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(url,json = dic ,headers = headers)
    #return r.json
    x = r.json()
    if str(x['exists'])=="None":
        return jsonify({}),400
    else:
        url="http://0.0.0.0:80/api/v1/db/write"
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        res = requests.post(url, json = dic, headers=headers)
        return jsonify({}),200
        #return res.text

@app.route("/api/v1/db/write", methods=["POST"])
def write_dab():
    content = ""
    #ext = tldextract.extract("http://0.0.0.0:80/user")
    if (request.json['some'] == "user"):
        content = request.json
        username = content["username"]
        password = content["password"]
        new_user = User(username, password)
        dab.session.add(new_user)
        dab.session.commit()
        return content
    if (request.json['some'] == "rides"):
        content = request.json
        created_by = content['created_by']
        source = content['source']
        destination = content['destination']
        timestamp = content['timestamp']
        riders = content['riders']
        #riders.append(created_by)
        new_ride = Ride(created_by,source,destination,timestamp,riders )
        dab.session.add(new_ride)
        dab.session.commit()
        return content
        #return ride_schema.jsonify(new_ride)
        #return str(new_ride)
        # return ride_schema.jsonify(new_ride )
    #return content
    elif (request.json['some'] == 'join_rides'):
        content = request.json
        rideId = content['rideId']
        username = content['username']
        #ride=Ride.query.get(rideId)
        #ride.riders.append(username)
        ride=Ride.query.filter_by(rideId=rideId).first()
        #ride=dab.session.query.filter_by(rideId=rideId)
        #ride.riders.append(username)
        x=ride.riders
        if ride.created_by == username:
            #return jsonify({"message":"creator of the ride cannot join the ride"}),400
            return "creator"
        elif (username not in x):
            x.append(username)
            ride.riders=x
            flag_modified(ride,"riders")
            dab.session.merge(ride)
            dab.session.flush()
            dab.session.commit()
            return ride_schema.jsonify(ride)
        else:
            #return jsonify({}),400
            return "already added"
    
        
        #return str(ride.riders)
    elif (request.json['some'] == 'adduser'):
        content = request.json
        username = content['username']
        user=User.query.get(username)
        dab.session.delete(user)
        dab.session.commit()
        return user_schema.jsonify(user)
    elif (request.json['some'] == 'delete_ride'):
        content = request.json
        rideId = content['rideId']
        ride=Ride.query.get(rideId)
        dab.session.delete(ride)
        dab.session.commit()
        return ride_schema.jsonify(ride)
        
@app.route('/api/v1/db/read',methods=['POST'])
def read_dab():
    content = ''
    if (request.json['some'] == 'ridesid'):
        content = request.json
        rideId = content['rideId']
        ride=Ride.query.get(rideId)
        
        #dum["Created_by"]="{".
        #li = ride_schema.jsonify(ride)
        return ride_schema.jsonify(ride)
    elif request.json['some'] == 'adduser':
        content = request.json
        username = content['username']
        user=User.query.get(username)
       # return user_schema.jsonify(user)
        return str(user)
    elif request.json['some'] == "join_ride":
        content = request.json
        username=content['username']
        rideId=content['rideId']
        exists=dab.session.query(Ride.rideId).filter_by(rideId=rideId).scalar()
        user_exists=dab.session.query(User.username).filter_by(username=username).scalar()
        dic={}
        dic['exists'] = exists
        dic['user_exists'] = user_exists
        #li = (exists,user_exists)
        return dic
        #x=jsonify(exists)
        #y=jsonify(user_exists)
        #h=(x,y)
        #return jsonify(exists,user_exists)
    elif(request.json['some']=='delete_ride'):
        content = request.json
        rideId = content['rideId']
        exists=dab.session.query(Ride.rideId).filter_by(rideId=rideId).scalar()
        dic = {}
        dic['exists'] = exists
        return dic
    elif (request.json['some'] == 'list'):     
        content1 = request.json
        source = content1['source']
        destination = content1['destination']    
        ride_id=dab.session.query(Ride.rideId).filter(Ride.source==source,Ride.destination==destination).all()
        s=str(ride_id)
        lis=[]
        x=map(int,re.findall(r'\d+',s))
        for i in list(x):
            ride=Ride.query.get(i)
            dumb={}
            dumb["rideId"]=ride.rideId
            dumb["username"]=ride.created_by
            username = ride.created_by
            #dumb["timestamp"]=ride.timestamp
            timestamp = ride.timestamp
            now = datetime.now()
            #d1 = d.strftime("%m/%d/%Y, %H:%M:%S")
            #now=datetime.strptime(d1, '%m/%d/%y %H:%M:%S')
            timestamp = datetime.strptime(timestamp, '%m/%d/%Y, %H:%M:%S')
            ex = dab.session.query(User.username).filter_by(username=username).scalar()
            #return str(ex)           
            if str(ex)=="None":
                pass       
            elif now > timestamp:
                pass
            else:
                dumb["timestamp"]=converter(ride.timestamp)
                lis.append(dumb)
        if(len(lis)==0):
            return "None"
        else:
            return jsonify(lis)
        
        '''content=list(jsonify(ride_id))
        lis = []
        for i in content:
            for j in i:
                try :
                    lis.append(int(j))
                    if int(j)>0: 
                        ride=Ride.query.get(j)
                        dumb={}
                        dumb["rideId"]=ride.rideId
                        dumb["username"]=ride.created_by
                        username = ride.created_by
                        #dumb["timestamp"]=ride.timestamp
                        timestamp = ride.timestamp
                        now = datetime.now()
                        #d1 = d.strftime("%m/%d/%Y, %H:%M:%S")
                        #now=datetime.strptime(d1, '%m/%d/%y %H:%M:%S')
                        timestamp = datetime.strptime(timestamp, '%m/%d/%Y, %H:%M:%S')
                        ex = dab.session.query(User.username).filter_by(username=username).scalar()
                        #return str(ex)           
                        if str(ex)=="None":
                            pass
                       
                        elif now > timestamp:
                            pass
                        else:
                            dumb["timestamp"]=converter(ride.timestamp)
                            lis.append(dumb)

               except ValueError:
                    pass
        if(len(lis)==0):
            return "None"
        else:
            return jsonify(lis)'''
        
   
    elif (request.json['some'] == 'get_details'):
        content=request.json
        riders=content['riders']
        new_riders=[]
        for rider in riders:
            user_exists=dab.session.query(User.username).filter_by(username=rider).scalar()
            if(str(user_exists)!="None"):
                new_riders.append(rider)
            else:
                pass
        return jsonify(new_riders)
            
            
if __name__ == '__main__':
    app.run(debug=True)
