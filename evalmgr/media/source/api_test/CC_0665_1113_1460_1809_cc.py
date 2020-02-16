
from flask import Flask ,render_template,abort,request,jsonify
from flask_sqlalchemy import SQLAlchemy
import requests
import json
import re
from datetime import datetime
from constants import *

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqllite3'
db = SQLAlchemy(app)


class User(db.Model):
    #id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), primary_key=True)
    password = db.Column(db.String(120), nullable=False)
    def __init__(self,username,password):
       self.username=username
       self.password=password
                
    def __repr__(self):
        return '%r' % self.username

class ride(db.Model):
        id=db.Column(db.Integer, primary_key=True)
        created_by=db.Column(db.String(120),  nullable=False)
        timestamp=db.Column(db.String(120),  nullable=False)
        source=db.Column(db.String(120),  nullable=False)
        destination=db.Column(db.String(120),  nullable=False)
        def __init__(self,created_by,timestamp,source,destination):
                #self.id=id
                self.created_by=created_by
                self.source=source
                self.timestamp=timestamp
                self.destination=destination
        def __repr__(self):
                return '<ride %r>' % self.id
class share(db.Model):
        id=db.Column(db.Integer, primary_key=True)
        username=db.Column(db.String(80), primary_key=True)
        
        def __init__(self,id,username):
                self.id=id
                self.username=username
        def __repr__(self):
                return '<share %r>' % self.id

@app.route('/api/v1/users',methods=["PUT"])
def add_user():
                #check how to get input from put
                #take username check if it is unique
                #take password check if it is SHA1
                #write to the database 
        if(request.method!="PUT"):
            return jsonify({}),405
        username =request.json["username"]

        password =request.json["password"]
        pattern = re.compile(r'\b[0-9a-f]{40}\b')
        match = re.match(pattern,password)
        #print(match)
        #match.group(0)
        if(match==None):
            return jsonify({}),400
        usercheck=requests.post('http://127.0.0.1:80/api/v1/db/write',json={"table":"User","operation":"insert","values":[username,password]})
        #print(usercheck)
        #print("hepol")
        if(usercheck.status_code==201):
            return jsonify({}),201
        else:
            return jsonify({}),400
        
        
        
        
                
                
@app.route('/api/v1/users/<username>',methods=["DELETE"])
def remove_user(username):
                #got the username
                #check if it exists in database
                #then delete
        if(request.method!="DELETE"):
            return jsonify({}),405
        usercheck=requests.post('http://127.0.0.1:80/api/v1/db/read',json={"table":"User"})
        y=json.loads(usercheck.text)
        for i in range(len(y["1"])):
            #print(i)
            y["1"][i]=y["1"][i][2:len(y["1"][i])-1]
            #print(y["1"])
        #print(username)
        if(username not in y["1"]):
            print("hello")
            return jsonify({}),400
        crossride=requests.post('http://127.0.0.1:80/api/v1/db/read',json={"table":"ride"})
        
        d=json.loads(crossride.text)
        
        for i in range(len(d["created_by"])):
            #print(i)
            d["created_by"][i]=d["created_by"][i][0:len(d["created_by"][i])]
            #print(y["1"])
        if(username in d["created_by"]):
            print("hello")
            return jsonify({}),400
        remuser=requests.post('http://127.0.0.1:80/api/v1/db/write',json={"table":"User","operation":"delete","values":[username]})
        print("hello")
        if(remuser.status_code==201):
            #checking to remove the share users if a created user is deleted
            remshare=requests.post('http://localhost:80/api/v1/db/read',json={"table":"share"})
            x=json.loads(remshare.text)
            for i in range(len(x["username"])):
                #print(i)
                x["username"][i]=x["username"][i][2:len(x["username"][i])-1]

                shadel=requests.post('http://127.0.0.1:80/api/v1/db/write',json={"table":"share1","operation":"delete","values":[username]})
                if(shadel.status_code==200):
                    return jsonify({}),200
                else:
                    return jsonify({}),400
            
        else:
            return jsonify({}),400
            
        
    
        
        
@app.route('/api/v1/rides',methods=["POST"])
def create_newride():
    print("in")
    created_by =request.json["created_by"]
    timestamp =request.json["timestamp"]
    source =request.json["source"]
    destination =request.json["destination"]
    minn,maxx=getmax()
    try:
        timenow=datetime.now()
        
    
        temp=datetime.strptime(timestamp, '%d-%m-%Y:%S-%M-%H')
        if(temp>=timenow):
                pass
    except:
        return jsonify({}),400

    if(int(source)==int(destination)):
        return jsonify({}),400

    if(int(source)>=minn and int(source)<=maxx and int(destination)>=minn and int(destination)<=maxx):
        pass
    else:
        #print("dfsgsdfs")
        return jsonify({}),400

        
    #if(request.method!="POST"):
    #return jsonify({}),405
    
    usercheck=requests.post('http://127.0.0.1:80/api/v1/db/read',json={"table":"User"})
    #dictt=json.loads(json.loads(usercheck.decode('utf-8')))
    #print(usercheck.text)
    y=json.loads(usercheck.text)
    #print(y["1"])
    #dictt=json.loads(json.loads(usercheck.text()))
    for i in range(len(y["1"])):
        #print(i)
        y["1"][i]=y["1"][i][2:len(y["1"][i])-1]
    #print(y["1"])
    if(created_by not in y["1"]):
        return jsonify({}),400
    
    usercheck_w=requests.post('http://127.0.0.1:80/api/v1/db/write',json={"table":"ride","operation":"insert","values":[created_by,timestamp,source,destination]})

        
    if(usercheck_w.status_code==201):
            return jsonify({}),201
    else:
            return jsonify({}),400
        
        

@app.route('/api/v1/rides/<rideid>',methods=["GET"])
def details_ride(rideid):
    if(request.method!="GET"):
        return jsonify({}),405
    #print(type(rideid))
    ridecheck=requests.post('http://127.0.0.1:80/api/v1/db/read',json={"table":"ride"})
    y=json.loads(ridecheck.text)
    #print(y["rideid"])
    if(int(rideid) not in y["rideid"]):
        return jsonify({}),204
    ind=y["rideid"].index(int(rideid))
    pool=requests.post('http://127.0.0.1:80/api/v1/db/read',json={"table":"share"})
    #print(pool.text)
    users=[]
    user_pool=json.loads(pool.text)
    for i in range(len(user_pool["id"])):
        #print(len(user_pool["id"]))
        if(user_pool["id"][i]==int(rideid)):
            users.append(user_pool["username"][i])
        #print (user_pool["id"][i])
    #print(users)
    #users.append(y["created_by"][ind])      
    ans=dict()
    ans={"rideId":rideid,"created_by":y["created_by"][ind],"timestamp":y["timestamp"][ind],"source":y["source"][ind],"destination":y["destination"][ind],"users":users}
    return jsonify(ans),200


@app.route('/api/v1/rides/<rideid>',methods=["POST"])
def join_ride(rideid):
    if(request.method!="POST"):
        return jsonify({}),405
    username =request.json["username"]
    
    usercheck=requests.post('http://127.0.0.1:80/api/v1/db/read',json={"table":"User"})
    y=json.loads(usercheck.text)
    print(y["1"])
    for i in range(len(y["1"])):
        #print(i)
        y["1"][i]=y["1"][i][2:len(y["1"][i])-1]
    if(username not in y["1"]):
        return jsonify({}),204    #CHECK IF THIS IS THE CODE U SHUD RETURN
    ridecheck=requests.post('http://127.0.0.1:80/api/v1/db/read',json={"table":"ride"})
    x=json.loads(ridecheck.text)
    
                  
    #print(y["rideid"])
    if(int(rideid) not in x["rideid"]):
        return jsonify({}),204
    index=x["rideid"].index(int(rideid))
    created_by_user=x["created_by"][index]

    if(created_by_user==username):
        return jsonify({}),400
        
    vals=requests.post('http://127.0.0.1:80/api/v1/db/write',json={"table":"share","operation":"insert","values":[rideid,username]})
    if(vals.status_code==201):
        return jsonify({}),200
    else:
        return jsonify({}),400
    







@app.route('/api/v1/rides/<rideid>',methods=["DELETE"])
def remove_ride(rideid):
    if(request.method!="DELETE"):
        return jsonify({}),405
    ridecheck=requests.post('http://127.0.0.1:80/api/v1/db/read',json={"table":"ride"})
    y=json.loads(ridecheck.text)
    #print(y["rideid"])
    if(int(rideid) not in y["rideid"]):
        return jsonify({}),204
    
    ridecheck=requests.post('http://127.0.0.1:80/api/v1/db/write',json={"table":"ride","operation":"delete","values":[rideid]})
    ridecheck_1=requests.post('http://127.0.0.1:80/api/v1/db/write',json={"table":"share","operation":"delete","values":[rideid]})
    
    if(ridecheck.status_code==200 and ridecheck_1.status_code==200):
        return jsonify({}),200
    else:
        return jsonify({}),400
    
    
    
    
@app.route('/api/v1/rides',methods=["GET"])
def list_upcoming_rides():
        #if(request.method!="GET"):
        #return jsonify({}),405
        source=request.args.get("source")
        destination=request.args.get("destination")
        print("hi")
        rides=requests.post('http://127.0.0.1:80/api/v1/db/read',json={"table":"ride"})
        y=json.loads(rides.text)
        ans=[]
        minn,maxx=getmax()
        if(int(source)>=minn and int(source)<=maxx and int(destination)>=minn and int(destination)<=maxx):
            
            pass
        else:
            #print("dfsgsdfs")
            return jsonify({}),400
        timenow=datetime.now()
        for i in range(len(y["rideid"])):
            timestamp=y["timestamp"][i]

            temp=datetime.strptime(timestamp, '%d-%m-%Y:%S-%M-%H')
            if(temp>=timenow and source == y["source"][i] and destination == y["destination"][i]):
                a=dict()
                a["rideid"]=y["rideid"][i]
                a["created_by"]=y["created_by"][i]
                a["timestamp"]=y["timestamp"][i]
                ans.append(a)
        if(ans==[]):
            return jsonify({}),204
        return jsonify(ans),200
                
                
                
                
                
                
      
    
    
    

     
@app.route('/api/v1/db/read',methods=["POST"])
def readd():
        
        
        table_name=request.json["table"]
        #columns=request.json["columns"]
        #where=request.json["where"]

        if(table_name=='User'):
            #print("hellllllo\n")
            out=db.session.query(User).all()
            nm=list()
            for i in out:
                nm.append(str(i))
            #valdict[nm]=ps
            #for i in out:
                #valdict[str(i)]=str(i.password)
                #print(i)
            #print(valdict)
            return json.dumps({'1':nm}),200
        elif(table_name=='ride'):
            out=db.session.query(ride).all()
            
            rd=dict()
            rd={"rideid":[],"created_by":[],"users":[],"timestamp":[],"source":[],"destination":[]}
            for i in out:
                rd["rideid"].append(i.id)
                rd["created_by"].append(i.created_by)
                #rd["users"].append(i.users)
                rd["timestamp"].append(i.timestamp)
                rd["source"].append(i.source)
                rd["destination"].append(i.destination)
            return json.dumps(rd),200
            
        elif(table_name=='share'):
            out=db.session.query(share).all()
            rd=dict()
            rd={"id":[],"username":[]}
            for i in out:
                rd["id"].append(i.id)
                rd["username"].append(i.username)
            return json.dumps(rd),200
                
                
                
        elif(table_name=='share'):
                        out=db.session.query(share).all()
            
                    
        return ""
    
        #table_name.query.filter_by(username='peter').all()
        #request_books.append((book_name,author))
        #return  str(table_name)+str(columns)+str(where)
    
        
        
@app.route('/api/v1/db/write',methods=["POST"])
def write():
        #operation,table,values
    operation=request.json["operation"]
    values=request.json["values"]
    table=request.json["table"]
    try:
        if(operation=="insert"):
                if(table=="User"):
                    a=User(username=values[0],password=values[1])
                    db.session.add(a)
                    db.session.commit()
                elif(table=="ride"):
                    b=ride(created_by=values[0],timestamp=values[1],source=values[2],destination=values[3])
                    db.session.add(b)
                    db.session.commit()
                elif(table=="share"):
                    c=share(id=values[0],username=values[1])
                    db.session.add(c)
                    db.session.commit()
        elif(operation=="delete"):
                if(table=="User"):
                    #a=User(username=values[0])
                    User.query.filter(User.username==values[0]).delete()
                    #db.session.add(a)
                    db.session.commit()
                    return "done",201
                elif(table=="ride"):
                    ride.query.filter(ride.id==values[0]).delete()
                    db.session.commit()
                    return "done",200
                elif(table=="share"):
                    share.query.filter(share.id==values[0]).delete()
                    db.session.commit()
                    return "done",200
                elif(table=="share1"):
                    share.query.filter(share.username==values[0]).delete()
                    db.session.commit()
                    return "done",200
    
                    
                                        

                    
        
        
        return "done",201
    except:
        return "user already exists",400
                        
                        
                        
        #user=User()
        #db.session.add(user)
        #db.session.commit()
        
        #return 



if __name__ == '__main__':      
        app.debug = True
        app.run()
                

  
                
