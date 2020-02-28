from flask import Flask,render_template,jsonify,request,abort
import pandas as pd
import sqlite3
from sqlite3 import Error
from flask_sqlalchemy import SQLAlchemy
import datetime
import os
import sys
import hashlib
import requests
import json

app=Flask(__name__)

basedir=os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///rideshare1.db'
app.config['SQLALCHEMY_TRACK_MODIFICATION']=False
db=SQLAlchemy(app)
  
class usertable(db.Model):
    username=db.Column(db.Text(),unique=True,nullable=False,primary_key=True)
    password=db.Column(db.Text(), nullable=False)

    def __init__(self,username,password):
        self.username=username
        self.password=password

class ridetable(db.Model):
    rideid=db.Column(db.Integer(),nullable=False,primary_key=True,autoincrement=True)
    username=db.Column(db.Text(),nullable=False)
    timestamp=db.Column(db.Text(),nullable=False)
    source=db.Column(db.Text(),nullable=False)
    destination=db.Column(db.Text(),nullable=False)

    def __init__(self,username,timestamp,source,destination,rideid):
        self.rideid=rideid
        self.username=username
        self.timestamp=timestamp
        self.source=source
        self.destination=destination

class sharetable(db.Model):
    rowid=db.Column(db.Integer(),nullable=False,primary_key=True)
    rideid=db.Column(db.Text(),nullable=False)
    username=db.Column(db.Text(),nullable=False)

    def __init__(self,rideid,username,rowid):
        self.rowid=rowid
        self.rideid=rideid
        self.username=username


db.create_all()
       

@app.route('/api/v1/db/write',methods=["POST"])
def writedb():
    info=request.get_json()
    table=info["table"]
    cond_f= info["cond_f"]
    if cond_f==0:
        if(table=="usertable" or table=="sharetable" ):
            colname=info["column"]
            values=info["insert"]
            z=''
            for i in values:
                z+="'"+i+"',"
            z=z[:-1]
            x=''
            for j in colname:
                x+=j+','
            x=x[:-1]
            
            query='INSERT INTO '+table+" ("+x+") VALUES ("+z+")"
            #print(query)
            try:
                conn=sqlite3.connect('rideshare1.db')
                c=conn.cursor()
                c.execute(query)
                conn.commit()
                conn.close()
                return jsonify({}),200
            
            except Exception as err: 
                print(err)
                return jsonify({}),400

        elif(table=="ridetable"):
            colname=info["column"]
            values=info["insert"]
            source=info["place1"]
            destination=info["place2"]
            z=''
            for i in values:
                z+="'"+i+"',"
            z=z[:-1]
            x=''
            for j in colname:
                x+=j+','
            x=x[:-1]

            query='INSERT INTO ridetable ('+x+") VALUES ("+z+","+str(source)+","+str(destination)+")"
            #print(query)

            try:
                conn=sqlite3.connect('rideshare1.db')
                c=conn.cursor()
                c.execute(query)
                conn.commit()
                conn.close()
                return jsonify({}),200
            
            except Exception as err:
                print(err)
                return jsonify({}),400


   
    elif cond_f==1:
        if (table=="usertable"):
            condition=info["username"]
            query='DELETE FROM '+table+' WHERE username = "'+condition+'"'
        elif (table=="ridetable"):
            condition=info["rideId"]
            query='DELETE FROM '+table+' WHERE rowid = "'+condition+'"'
        #print(query)
        try:
            conn=sqlite3.connect('rideshare1.db')
            c=conn.cursor()
            c.execute(query)
            conn.commit()
            conn.close()
            return jsonify({}),200
        
        except Exception as err:
            print(err)
            return jsonify({}),400
 
@app.route('/api/v1/db/read',methods=["POST"])
def readdb():
    data=request.get_json()
    cond_f=data["cond_f"]
    if cond_f==0:
        table=data["table"]
        colname=data["columns"]
        where=data["where"]
        z=''
        for i in where:
            z+="'"+i+"',"
        z=z[:-1]
        x=''
        for j in colname:
            x+=j+','
        x=x[:-1]
        t=len(where)
        query='SELECT '+x+' FROM '+table+' WHERE '
        for o in range(t):
            query+=colname[o]+' = "'+where[o]+'" AND '
        query=query[:-5] 
        """if(table=='usertable'):
            query='SELECT username FROM '+table+' WHERE username = '+z
        elif(table=='ridetable'):
            query='SELECT rowid FROM '+table+' WHERE rowid = '+z  """
        #print(query)
        try:
                conn=sqlite3.connect('rideshare1.db')
                c=conn.cursor()
                c.execute(query)
                res=c.fetchone()
                if res:
                    return jsonify({}),400
                conn.close()
                return jsonify({}),200
            
        except Exception as err:
            print(err)
            return jsonify({}),400
    elif cond_f==1:
        source=data["source"]
        destination=data["destination"]
        query='SELECT rideid,username,timestamp from ridetable where source = "'+str(source)+'" AND destination = "'+str(destination)+'"'#AND s[rowid] >"'+ str(datetime.datetime.now())+'"'
        #print(query)
        try:
            conn=sqlite3.connect('rideshare1.db')
            conn.row_factory=sqlite3.Row
            c=conn.cursor()
            
            rows=c.execute(query).fetchall()
            conn.commit()
            conn.close()
            #print(rows)
            #print(json.dumps([dict(ix) for ix in rows]))

            l=len(rows)
            res={}
            for i in range(l):
                res[str(i)]= dict(rows[i])

            res["count"]=l
            #print(res)
            return (json.dumps(res)),200

            #return rows
        except Exception as err:
            print(err)
            return jsonify({}),400
            

    elif cond_f==2:
        rideid=data["rideid"]
        query='SELECT * from ridetable where rowid = "'+str(rideid)+'"'
        query1='SELECT username from sharetable where rideid = "'+str(rideid)+'"'
        #print(query)
        #print(query1)
        try:
            conn=sqlite3.connect('rideshare1.db')
            conn.row_factory=sqlite3.Row
            c=conn.cursor()

            rows=c.execute(query).fetchall()
            rows1=c.execute(query1).fetchall()
            conn.commit()
            conn.close()
            for i in rows1:
                rows.append(i)
            l=len(rows)
            #print(rows)
            res={}
            for i in range(l):
                res[str(i)]= dict(rows[i])

            #print(res)
            p=[]
            for i in range(1,l):
                p.append(res[str(i)]["username"])
            #print(p)
            d1={'users':p}
            res["0"].update(d1)
            #print(json.dumps(res))
            return (json.dumps(res))
            

        except Exception as err:
            print(err)
            return jsonify({}),400

@app.route('/api/v1/users',methods=["PUT"])
def adduser():
    if(request.method!="PUT"):
        return jsonify({}),405
    username=request.get_json()["username"]
    password=request.get_json()["password"]
    #if(re.match("^[a-fA-F0-9]{40}$",password,flags=0)==0 or len(password)!=40):
    #    return jsonify({}),400
    if(len(password)!=40):
        return jsonify({}),400
    try:
        sha_int = int(password,16)
    except ValueError:
        return jsonify({}),400
    if(requests.post("http://127.0.0.1:5000/api/v1/db/read",
        json={
            "table":"usertable",
            "columns":["username"],
            "where":[username],
            "cond_f":0
        }).status_code==400):
        return jsonify({}),400
    t=requests.post("http://127.0.0.1:5000/api/v1/db/write",
    json={
        "table":"usertable",
        "column":["username","password"],
        "insert":[username,password],
        "cond_f":0
    })
    return jsonify({}),201

@app.route('/api/v1/users/<user_name>',methods=["DELETE"])
def removeuser(user_name):
    if(request.method!="DELETE"):
        return jsonify({}),405
    if(requests.post("http://127.0.0.1:5000/api/v1/db/read",
        json={
            "table":"usertable",
            "columns":["username"],
            "where":[user_name],
            "cond_f":0
        }).status_code==200):
        return jsonify({}),400
    t=requests.post("http://127.0.0.1:5000/api/v1/db/write",
    json={
        "table":"usertable",
        "username":user_name,
        "cond_f":1
    })
    return jsonify({}),200

@app.route('/api/v1/rides',methods=["POST"])
def newride():
    if(request.method!="POST"):
        return jsonify({}),405
    username=request.get_json()["created_by"]
    timestamp=request.get_json()["timestamp"]
    source=request.get_json()["source"]
    destination=request.get_json()["destination"]
    if(check_place(int(source),int(destination))==-1):
        return jsonify({}),400
    if(requests.post("http://127.0.0.1:5000/api/v1/db/read",
        json={
            "table":"usertable",
            "columns":["username"],
            "where":[username],
            "cond_f":0
        }).status_code==200):
        return jsonify({}),400
    t=requests.post("http://127.0.0.1:5000/api/v1/db/write",
        json={
            "table":"ridetable",
            "column":["username","timestamp","source","destination"],
            "insert":[username,timestamp],
            "place1":source,
            "place2":destination,
            "cond_f":0
    })
    return jsonify({}),201

@app.route('/api/v1/rides',methods=["GET"])
def avlrides():
    if(request.method!="GET"):
        return jsonify({}),405
    source=request.args.get("source")
    destination=request.args.get("destination")
    if(check_place(int(source),int(destination))==-1):
        return jsonify({}),400
    if(requests.post("http://127.0.0.1:5000/api/v1/db/read",
        json={
            "cond_f":0,
            "table":"ridetable",
            "columns":["source","destination"],
            "where":[source,destination]
        }).status_code==200):
        return jsonify({}),204

    t=requests.post("http://127.0.0.1:5000/api/v1/db/read",
        json={
            "cond_f":1,
            "source":source,
            "destination":destination
        })
    count=t.json().get("count")
    res=[]
    #tim= t.json().get("timestamp")
    #print(tim)

    def change(e):
        y=str(e)
        t=""
        t=(y[6:10])
        t+='-'
        t+=(y[3:5])
        t+='-'
        t+=(y[0:2])
        t+=' '
        t+=(y[17:19])
        t+=':'
        t+=(y[14:16])
        t+=':'
        t+=(y[11:13])
        #print(t)
        return datetime.datetime.strptime(t,'%Y-%m-%d %H:%M:%S')
    for i in range(count):
        new= t.json().get(str(i))
        tim= new["timestamp"]
        tim= change(tim)
        if tim>datetime.datetime.now():
            res.append(new)

    #res={}
    

    return json.dumps(res),200
    
@app.route('/api/v1/rides/<rideId>',methods=["GET"])
def details(rideId):
    if(request.method!="GET"):
        return jsonify({}),405
    if(requests.post("http://127.0.0.1:5000/api/v1/db/read",
        json={
            "table":"ridetable",
            "columns":["rideid"],
            "where":[rideId],
            "cond_f":0
        }).status_code==200):
        return jsonify({}),400
    t= requests.post("http://127.0.0.1:5000/api/v1/db/read",
        json={
            "cond_f":2,
            "rideid":rideId
        })
    x=t.json().get(str(0))
    return json.dumps(x),200
   
@app.route('/api/v1/rides/<rideId>',methods=["POST"])
def shareride(rideId):
    if(request.method!="POST"):
        return jsonify({}),405
    username=request.get_json()["username"]
    if(requests.post("http://127.0.0.1:5000/api/v1/db/read",
        json={
            "table":"usertable",
            "columns":["username"],
            "where":[username],
            "cond_f":0
        }).status_code==200):
        return jsonify({}),204
    
    if(requests.post("http://127.0.0.1:5000/api/v1/db/read",
        json={
            "table":"ridetable",
            "columns":["rideid"],
            "where":[rideId],
            "cond_f":0
        }).status_code==200):
        return jsonify({}),204
    
    t=requests.post("http://127.0.0.1:5000/api/v1/db/write",
    json={
        "table":"sharetable",
        "column":["rideid","username"],
        "insert":[rideId,username],
        "cond_f":0
    })
    return jsonify({}),200

@app.route('/api/v1/rides/<rideId>',methods=["DELETE"])
def removeride(rideId):
    if(request.method!="DELETE"):
        return jsonify({}),405
    if(requests.post("http://127.0.0.1:5000/api/v1/db/read",
        json={
            "table":"ridetable",
            "columns":["rideid"],
            "where":[rideId],
            "cond_f":0
        }).status_code==200):
        return jsonify({}),400
    t=requests.post("http://127.0.0.1:5000/api/v1/db/write",
    json={
        "table":"ridetable",
        "rideId":rideId,
        "cond_f":1
    })
    return jsonify({}),200

def check_place(src,dst):
    df=pd.read_csv("AreaNameEnum.csv")
    area_no=list(df['Area No'])
    if(src not in area_no or dst not in area_no):
        return -1
    else:
        return 1

if __name__=='__main__':
    app.debug=True
    app.run()
