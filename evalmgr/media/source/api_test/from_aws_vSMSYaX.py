from flask import Flask, jsonify, request, abort, make_response
from flask_sqlalchemy import SQLAlchemy
from random import randint
from datetime import datetime
from datetime import date
import time
import json

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/dpk/Desktop/SEM6/CC/a1/rideshare.db'
db = SQLAlchemy(app)


class user_details(db.Model):
    username = db.Column(db.String(80), primary_key=True)
    password = db.Column(db.String(80))

class ride_details(db.Model):
    rideid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    timestamp = db.Column(db.String(80))
    source = db.Column(db.Integer)
    destination = db.Column(db.Integer)
class join_user(db.Model):
    srn= db.Column(db.Integer,primary_key=True)
    rideid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80),primary_key=True)

db.create_all()

###############################################TASK 1################################################

cps =['1','0','2','3','4','5','6','7','8','9','a','b','c','d','e','f','A','B','C','D','E','F']

@app.route("/api/v1/users",methods=["PUT"])
def add_user():
    un = request.get_json()["username"]
    ps = request.get_json()["password"]
    c = app.test_client()
    para1 = {
    "table"  : "user_details",
	"column" : ["username","password"],
	"where" :  "username = "+ un
    }
    response = c.post('/api/v1/db/read',json=para1,follow_redirects=True)
    if(response.get_json()): 
        return "Key exists",400
    if len(ps)!=40:
        #return jsonify("Password is not of type SHA1 hash hex"),400
        return make_response("Password not SHA1",400)
        
    else:
        for i in ps:
            if(i not in cps):
               # return jsonify("Password is not of type SHA1 hash hex"),400
                return make_response("Password not SHA1",400)
    c = app.test_client()
    para = {
    "table"  : "user_details",
	"column" : ["username","password"],
	"insert" : [un,ps]
    }
    response = c.post('/api/v1/db/write',json=para,follow_redirects=True)
    return make_response("{}", 201)

###############################################TASK 2################################################

@app.route("/api/v1/users/<user>",methods=["DELETE"])
def delete_user(user):
    c = app.test_client()
    para1 = {
    "table"  : "user_details",
	"column" : ["username"],
	"where" :  "username = "+ user
    }
    response = c.post('/api/v1/db/read',json=para1,follow_redirects=True)
    #user1= user_details.query.filter_by(username = user).first()
    if(response.get_json()): 
        user_details.query.filter(user_details.username == user).delete() 
        db.session.commit()
    else:
        return make_response("Username does not exist",400)
    return make_response("{}",200)

###############################################TASK 3################################################

@app.route("/api/v1/rides",methods=["POST"])
def add_ride():
    un = request.get_json()["created_by"]
    ts = request.get_json()["timestamp"]
    src =int(request.get_json()["source"])
    dest =int( request.get_json()["destination"])
    c = app.test_client()
    para1 = {
    "table"  : "user_details",
	"column" : ["username","password"],
	"where" :  "username = "+ un
    }
    resp1 = c.post('/api/v1/db/read',json=para1,follow_redirects=True)
    print(resp1.get_json())
    if(resp1.get_json()): 
        rid = randint(0,9999)
        if((src>0)and(src<199)):
            if((dest>0)and(dest<199)):
                c = app.test_client()
                para2 = {
                        "table"  : "ride_details",
	                    "column" : ["rideid","username","timestamp","source","destination"],
	                    "insert" : [rid,un,ts,src,dest]
                }
                resp2 = c.post('/api/v1/db/write',json=para2,follow_redirects=True)
                
                para3 = {
                    "table": "ride_details",
                    "column":["rideid"],
                    "where":"username = "+un
                }
                
                resp3 = c.post('/api/v1/db/read',json=para3,follow_redirects=True)
                
                obj = resp3.get_json()
                # print "-----------", obj
                for elem in obj["rideid"]:
                    rid = randint(9999,99999)
                    
                    para4 = {
                        "table" :"join_user",
                        "column" : ["srn","rideid","username"],
                        "insert"  : [rid,elem, un]
                    }
                    resp4 = c.post('/api/v1/db/write',json=para4,follow_redirects=True)
            else:
                return make_response("Destination does not exist", 400)
        else:
            return make_response("Source doesnot exist", 400)
    else:
        return make_response("Username doesnot exist", 400)
    return make_response( "{}",201)

###############################################TASK 4################################################

@app.route('/api/v1/rides', methods=["GET"]) 
# if (type(request.args) = int):
def upcoming_ride():
    results={}
    res=[]
    final=[]
    if 'source' in request.args:
        src=str(request.args['source'])
    if 'destination' in request.args:    
        dest=str(request.args['destination'])
    else:
        return make_response("Please mention source and destination",405)
    
    curr_time=datetime.now().strftime("%d-%m-%Y:%S-%M-%H")
    
    c = app.test_client()
    para1 = {
    "table"  : "ride_details",
	"column" : ["rideid","username","timestamp"],
	"where" :  "source = "+ src+" AND destination = "+dest
    }
    response = c.post('/api/v1/db/read',json=para1,follow_redirects=True)

    obj = response.get_json()
    if(obj): 
        i = 0
        for i in range(len(obj['username'])):
            results = {}
            for key in obj:
                if(key == "rideid"):
                    results["rideId"] = obj[key][i]
                else:
                    results[key] = obj[key][i]
            res.append(results)
        for record in res:
            tdelta= datetime.strptime(record['timestamp'],'%d-%m-%Y:%S-%M-%H')\
                 - datetime.strptime(curr_time,'%d-%m-%Y:%S-%M-%H')
            if(tdelta.days >-1 and tdelta.seconds>0):
                final.append(record)
        return json.dumps(final)
    else:
        return make_response("Ride Id does not exist", 405)


###############################################TASK 5################################################
@app.route('/api/v1/rides/<int:task_id>', methods=["GET"])
def get_task(task_id):             

    c = app.test_client()
    # ride= ride_details.query.filter_by(rideid = task_id).first()
    para1 = {
    "table"  : "ride_details",
	"column" : ["rideid","username","timestamp","source","destination"],
	"where" :  "rideid = "+ str(task_id)
    }
    resp1= c.post('/api/v1/db/read',json=para1,follow_redirects=True)
    ride_obj = resp1.get_json()
#    print "~~~~~~~~~", ride_obj

    ride_dict = {}
    for key in ride_obj:
        ride_dict[key] = ride_obj[key][0]

    # ride1= join_user.query.filter(join_user.rideid == task_id).all()
    para2 = {
    "table"  : "join_user",
	"column" : ["rideid","username"],
	"where" :  "rideid = "+ str(task_id)
    }

    resp2 = c.post('/api/v1/db/read',json=para2,follow_redirects=True)
    ride1_obj = resp2.get_json()
#    print "---------", ride1_obj
    
    res= ride1_obj["username"]

    if(not ride_obj):
        return make_response("Ride id does not exist",405)
    else: 
        return make_response(jsonify({"rideid":ride_dict["rideid"],"created By":ride_dict["username"],\
            "users":res,"timestamp":ride_dict["timestamp"],"source":ride_dict["source"],\
                "destination":ride_dict["destination"]}),200)
    #    return make_response("ok", 200)
    

###############################################TASK 6################################################
@app.route('/api/v1/rides/<int:task_id>', methods=['POST'])
def join_ride(task_id):
    un = request.get_json()["username"]

    c = app.test_client()
    # user1= user_details.query.filter_by(username = un).first()
    para1 = {
    "table"  : "user_details",
	"column" : ["username"],
	"where" :  "username = "+ un
    }
    resp1= c.post('/api/v1/db/read',json=para1,follow_redirects=True)
    user1_obj = resp1.get_json()

    # rideid1=ride_details.query.filter_by(rideid =task_id).first()
    para2 = {
    "table"  : "ride_details",
	"column" : ["username"],
	"where" :  "rideid= "+ str(task_id)
    }
    resp2= c.post('/api/v1/db/read',json=para1,follow_redirects=True)
    rideid1_obj = resp2.get_json()
    if(user1_obj): 
        if(rideid1_obj):
            rid = randint(0,9999)
            para3 = {
                "table"  : "join_user",
	            "column" : ["srn","rideid","username"],
	            "insert" : [rid,task_id,un]
            }
            resp2= c.post('/api/v1/db/write',json=para3,follow_redirects=True)
            return make_response("OK",200)

            # ride1=join_user(srn =rid,rideid = task_id, username = un)
            # db.session.add(ride1)
            # db.session.commit()
        else:
            return make_response("rideid does not exist",405)
    else:
        return make_response("Username does not exist", 405)   
###############################################TASK 7################################################

@app.route("/api/v1/rides/<rid>",methods=["DELETE"])
def delete_ride(rid):
    c = app.test_client()
    para1 = {
    "table"  : "ride_details",
	"column" : ["rideid"],
	"where" :  "rideid = "+ rid
    }
    response = c.post('/api/v1/db/read',json=para1,follow_redirects=True)
    if(response.get_json()): 
        ride_details.query.filter(ride_details.rideid == rid).delete() 
        db.session.commit()
    else:
        return make_response("Ride ID does not exist",400)
    return make_response("{}",200)

###############################################TASK 8################################################

@app.route("/api/v1/db/write",methods=["POST"])
def write_db():
    data = request.get_json()["insert"]
    cn = request.get_json()["column"]
    tn = request.get_json()["table"]
    tn=eval(tn) 
    new_user=tn()
    for i in range(len(data)):
        data1 = data[i]
        c1 = cn[i]
        setattr(new_user, c1, data1)
    db.session.add(new_user)
    db.session.commit()
    return {},200

###############################################TASK 9################################################
    
@app.route("/api/v1/db/read",methods=["POST"])
def read_db():
    data = request.get_json()["where"]
    cn = request.get_json()["column"]
    tn = request.get_json()["table"]
    tn=eval(tn) 
    new_user=tn()
    result = data.find('AND') 
    if(result==-1):
        ind = data.find('=')
        att = data[:ind-1]
        val = data[ind+2:]
        x = getattr(tn, att)
        user1= tn.query.filter((x == val)).all()
        d = {}
        for i in user1:
            cnt = 0
            for j in cn:
                if j not in d:
                    d[j] =[]
                    cnt =cnt+1
                a = getattr(i, j)
                d[j].append(a)
        return jsonify(d)
        return {}

    else:
        q1 = data[:result-1]
        q2 = data[result+4:]
        i1 = q1.find('=')
        a1 = q1[:i1-1]
        v1 = q1[i1+2:]
        x1 = getattr(tn, a1)
        i2 = q1.find('=')
        a2 = q1[:i2-1]
        v2 = q1[i2+2:]
        x2 = getattr(tn, a2)
        user1= tn.query.filter((x1 == v1)&(x2 == v2)).all()
        d = {}
        for i in user1:
            cnt = 0
            for j in cn:
                if j not in d:
                    d[j] =[]
                    cnt =cnt+1
                a = getattr(i, j)
                d[j].append(a)
        return jsonify(d)
        return {}


if __name__ == "__main__":
    app.debug=True
    app.run()
