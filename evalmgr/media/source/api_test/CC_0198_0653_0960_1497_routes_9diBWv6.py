from flask import Flask, request, flash, url_for, redirect, render_template
from flask import Flask, render_template,\
jsonify,request,abort
from flask import Flask, Response
import string 
import pandas as pd
import csv
import re 
import json
import datetime
import ast
from sqlalchemy import create_engine,DateTime
from sqlalchemy.exc import IntegrityError
import requests
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cc.db'
db = SQLAlchemy(app)
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])



class users_det(db.Model):
   username = db.Column('username', db.String, primary_key = True)
   password = db.Column('password',db.String(10))

   def __init__(self, username,password):
        self.username = username
        self.password = password

class ride_details(db.Model):
                created_by = db.Column('created_by',db.String, db.ForeignKey('users_det.username'))
                timestamp = db.Column('timestamp',db.String)
                source = db.Column('source',db.String)
                destination = db.Column('destination',db.String)
                rideId = db.Column('rideId',db.Integer, primary_key=True,autoincrement=True) 
                users = db.Column('users',db.String)

class areas(db.Model):
		codes=db.Column('codes',db.Integer,primary_key=True)
		area=db.Column('area',db.String)




		


db.create_all()

try:
        with open('AreaNameEnum.csv','r') as fin: 
                dr = csv.DictReader(fin) 
                for i in dr:
                        print(i)
                        execstr='INSERT INTO areas(codes,area) VALUES '+ '('+ i['Area No']+','+'"'+i['Area Name']+'"'+')'
                        print(execstr)
                        engine.execute(execstr)
                print("done")
except:
        db.session.rollback()



@app.route("/api/v1/db/write",methods=["POST"])
def insert():
        from sqlalchemy.exc import IntegrityError
        table=request.get_json()["table"]
        insert=request.get_json()["insert"]
        column=request.get_json()["column"]
        print('user_ins',insert)
        if(request.json['type']=="del_user"):
                values=db.session.query(ride_details.users).all()
                if(len(values)>=1):
                        new_res = [list(ele) for ele in values] 
                        print("new_res",new_res)
                        for i in new_res:
                                reg=re.findall(insert[0],i[0])
                                if(reg):
                                        val = re.split(',',i[0])
                                        print("vbnnm",val)
                                        if(val[0]==insert[0]):
                                                ride_details.query.filter_by(created_by=insert[0]).delete()
                                                db.session.commit()
                                                users_det.query.filter_by(username=insert[0]).delete()
                                                db.session.commit()
                                                return {},200   
                                        else:
                                                for name in val:
                                                        if(name==insert[0]):
                                                                val.remove(name)
                                                new_str = ''
                                                for i in val:
                                                        new_str+=i
                                                print('val',new_str)
                                        
                                                qry='UPDATE ride_details SET users = '+'"'+new_str+'"'+' WHERE created_by = '+'"'+val[0]+'"'
                                                print("auery",qry)
                                                engine.execute(qry)
                                                db.session.commit()
                                                return {},200
                
                else:
                        users_det.query.filter_by(username=insert[0]).delete()
                        db.session.commit()
                        return {},200
        elif(request.json['type']=="del_ride"):
                print('insert',insert)
                ride_details.query.filter_by(rideId=int(insert[0])).delete()
                                            
                db.session.commit()
                return {},200
        else:
                str1=''
                str2=''
                for i in range(len(column)):
                        str1=str1+'"'+str(insert[i])+'"'+','
                        str2=str2+str(column[i])+','
                str3 = str1.strip(',')
                str4 = str2.strip(',')
                if(column[0]=="users"):
                        execstr = 'UPDATE '+table+' SET users='+'"'+ insert[0] +'"'+' where rideId='+'"'+ insert[1] +'"'
                        print(execstr)
                        engine.execute(execstr)
                        db.session.commit()
                        return {},200
                else:
                        try:
                                execstr = 'INSERT INTO '+table+'('+str4+') VALUES'+'('+str3+')'
                                print(execstr)
                                engine.execute(execstr)
                                db.session.commit()
                                return {},201
                        except IntegrityError:
                                return {},400

        

@app.route("/api/v1/db/read",methods=["POST"])
def read():
        table=request.get_json()["table"]
        where=request.get_json()["where"]
        columns=request.get_json()["columns"]
        str1=''
        str2=''
        print(where)
        new_where=where.split('=')
        print('new where',new_where)
        if(len(new_where)>2):
                a=list()
                b=new_where[1].split("and ")
                a.append(new_where[0])
                print(len(b))
                for i in range(len(b)):
                        
                        if(i==0):
                                a.append(b[i].strip())
                        else:
                                a.append(b[i])
                a.append(new_where[2])
                print('a',a)
                new_where=a
        print('ab',new_where)		
        for i in range(len(columns)):
                str2=str2+str(columns[i])+','
        str4 = str2.strip(',')

        if(new_where[0]=="username"): 
            if(users_det.query.filter_by(username=new_where[1]).first()):
                execstr = 'SELECT '+str4+ ' FROM ' +table + ' WHERE '+new_where[0]+' = ' +'"'+ new_where[1] +'"'
                print(execstr)
                engine.execute(execstr)
                return {},200
        elif(new_where[0]=="password"):
            if(users_det.query.filter_by(password=new_where[1]).first()):
                execstr = 'SELECT '+str4+ ' FROM ' +table + ' WHERE '+new_where[0]+' = ' +'"'+ new_where[1] +'"'
                print(execstr)
                engine.execute(execstr)
                return {},200

        elif(new_where[0]=="codes"):
            if(areas.query.filter_by(codes=new_where[1]).first()):
                execstr = 'SELECT '+str4+ ' FROM ' +table + ' WHERE '+new_where[0]+' = ' +'"'+ new_where[1] +'"'
                print(execstr)
                engine.execute(execstr)
                return {},200

        elif(new_where[0]=="rideId"):
                if(ride_details.query.filter_by(rideId=new_where[1]).first()):
                        execstr = 'SELECT '+str4+ ' FROM ' +table + ' WHERE '+new_where[0]+' = ' +'"'+ new_where[1] +'"'
                        print(execstr)
                        l=db.engine.execute(execstr)
                        d, a = {}, []
                        for rowproxy in l:
                                print("proxy")
                                for column, value in rowproxy.items():
                                        d = {**d, **{column: value}}
                                        print(d)
                                a.append(d)
                        
                        print("hakbc",a)
                        return jsonify(a)
        
        elif(new_where[0]=="source" and new_where[2]=="destination"):
                print("yes")
                
                now=datetime.datetime.now()
                present=now.strftime("%d-%m-%Y:%S-%M-%H")
                pres=datetime.datetime.strptime(present,"%d-%m-%Y:%S-%M-%H")
                if(ride_details.query.filter_by(source=new_where[1]).filter_by(destination=new_where[3])):
                        print("huchhh")
                        execstr = 'SELECT '+str4+ ' FROM ' +table + ' WHERE '+new_where[0]+' = ' +'"'+ new_where[1] +'"'+' AND '+new_where[2]+'='+'"'+new_where[3]+'"'
                        print(execstr)
                        l=db.engine.execute(execstr)
                        d, a = {}, []
                        for rowproxy in l:
                                for column, value in rowproxy.items():
                                        d = {**d, **{column: value}}
                                        print(d)
                                a.append(d)
                        new_dict=[]
                        for k in a:
                                time=datetime.datetime.strptime(k['timestamp'],"%d-%m-%Y:%S-%M-%H")
                                if(time>pres):
                                        new_dict.append(k)

                        print('a',a)
                        print('new',new_dict)
                        return jsonify(new_dict)
				             
        return {},400

@app.route("/api/v1/users",methods=["PUT"])
def adduser():
        
        user=request.get_json()["username"]
        pin=request.get_json()["password"]
        if(len(pin)==40 and re.findall("^[0-9a-fA-F]+$",pin)):
                response=requests.post('http://127.0.0.1:5000/api/v1/db/write',json={"table":"users_det","column":["username","password"],"insert":[user,pin],"type":''})
                return {},response.status_code
        else:
                return {},400
               
@app.route("/api/v1/users/<string:name>",methods=["DELETE"])
def removeuser(name):
        print(name)
        type="del_user"
        response=requests.post('http://127.0.0.1:5000/api/v1/db/read',json={"table":"users_det","columns":["username","password"],"where":'username='+name})
        if(response.status_code == 200):
                resp=requests.post('http://127.0.0.1:5000/api/v1/db/write',json={"table":"users_det","column":["username"],"insert":[name],"type":type})

                
                if(resp.status_code==400):
                        return {},400
                else:
                        return {},200
                
                
        elif(response.status_code==400):
                resp=requests.post('http://127.0.0.1:5000/api/v1/db/write',json={"table":"ride_details","column":["users"],"insert":[name],"type":type})
                if(resp.status_code==200):
                        return {},200
        else:
                return {},400


@app.route("/api/v1/rides",methods=["POST"])
def new_ride():
        created_by=request.get_json()["created_by"]
        timestamp=request.get_json()["timestamp"]
        source=request.get_json()["source"]
        destination=request.get_json()["destination"]
        now=datetime.datetime.now()
        present=now.strftime("%d-%m-%Y:%S-%M-%H")
        pres=datetime.datetime.strptime(present,"%d-%m-%Y:%S-%M-%H")
        time=datetime.datetime.strptime(timestamp,"%d-%m-%Y:%S-%M-%H")
        print('now',type(pres))
        print('time',type(time))
        print(timestamp)
        if(time > pres) :
            print("yes")
            response_check=requests.post("http://127.0.0.1:5000/api/v1/db/read",json={"table":"users_det","columns":["username","password"],"where":'username='+created_by})
            
            
            if(response_check.status_code==200):
                    leng=db.session.query(areas).all()
                    print('len',len(leng))
                    print('db',len(db.session.query(ride_details).all()))
                    if(int(source)>=1 and int(source)<=len(leng) and int(destination)>=1 and int(destination)<=len(leng) and int(source)!=int(destination)):
                        print("len")
                        if(len(db.session.query(ride_details).all())==0):
                                response=requests.post("http://127.0.0.1:5000/api/v1/db/write",json={"table":"ride_details","column":["created_by","timestamp","source","destination","rideId","users"],"insert":[created_by,timestamp,source,destination,len(db.session.query(ride_details).all())+1,created_by],"type":''})
                                return {},response.status_code
                        else:
                                response=requests.post("http://127.0.0.1:5000/api/v1/db/write",json={"table":"ride_details","column":["created_by","timestamp","source","destination","rideId","users"],"insert":[created_by,timestamp,source,destination,(db.session.query(db.func.max(ride_details.rideId)).scalar())+1,created_by],"type":''})
                                return {},response.status_code 
                    else:
                        return {},400
            else:
                    return {},400
        else:
            return {},400

@app.route("/api/v1/rides/<string:name>",methods=["DELETE"])
def deleteride(name):
                if(response.method!="DELETE"):
                    return {},405
                id=int(name)
                type="del_ride"
                response=requests.post('http://127.0.0.1:5000/api/v1/db/read',json={"table":"ride_details","columns":["created_by","timestamp","source","destination","rideId"],"where":'rideId='+str(id)})
                #print(response.status_code)
                d, a = {}, []
                for rowproxy in response.json():
                        for column, value in rowproxy.items():
                                d = {**d, **{column: value}}
                                print(d)
                        a.append(d)
                if(len(a)>0):
                        res=requests.post('http://127.0.0.1:5000/api/v1/db/write',json={"table":"ride_details","column":["rideId"],"insert":[str(id)],"type":type})
                        if(res.status_code==200):
                                return {},200
                else:
                        return {},400

@app.route("/api/v1/rides",methods=["GET"])
def list_upcoming():
                source=request.args['source']
                destination=request.args['destination']
                response_check=requests.post("http://127.0.0.1:5000/api/v1/db/read",json={"table":"ride_details","columns":["created_by","timestamp","source","destination","rideId"],"where":'source='+source+' and destination='+destination})
                print("typ",type(response_check))
                leng=len(db.session.query(areas).all())
                print('leng upcoming',leng)
                if(int(source)>=1 and int(source)<=leng and int(destination)>=1 and int(destination)<=leng and int(source)!=int(destination)):
                        d, a = {}, []
                        for i in response_check.json():
                                        for column, value in i.items():
                                                d = {**d, **{column: value}}
                                                print(d)
                                        a.append(d)
                        if(len(a)>0):
                                return jsonify(a),200
                        else:
                                return jsonify(a),204
                else:
                        return {},400


                
@app.route("/api/v1/rides/<string:id>",methods=["POST"])
def join_ride(id):
        id=int(id)
        username=request.get_json()["username"]
        response=requests.post('http://127.0.0.1:5000/api/v1/db/read',json={"table":"ride_details","columns":["created_by","timestamp","source","destination","rideId","users"],"where":'rideId='+str(id)})
        d, a = {}, []
        for rowproxy in response.json():
                for column, value in rowproxy.items():
                                d = {**d, **{column: value}}
                                print(d)
                a.append(d)
        if(len(a)>0):
                u=a[0]["users"]+','+username

                response=requests.post("http://127.0.0.1:5000/api/v1/db/write",json={"table":"ride_details","column":["users","rideId"],"insert":[u,str(id)],"type":''})
                if(response.status_code == 200):

                
                        return {},200
        else:
                return {},400


@app.route("/api/v1/rides/<string:id>",methods=["GET"])
def get_details(id):
        id=int(id)
        response=requests.post('http://127.0.0.1:5000/api/v1/db/read',json={"table":"ride_details","columns":["created_by","timestamp","source","destination","rideId","users"],"where":'rideId='+str(id)})
        d, a = {}, []
        for rowproxy in response.json():
                for column, value in rowproxy.items():
                                d = {**d, **{column: value}}
                                print(d)
                a.append(d)
        if(len(a)>0):
                for i in a:
                        i['users']=re.split(',',i['users'])[1:]
                        print('uuu',i['users'])

                return jsonify(a),200
        else:
                return jsonify(a),204

        
                
        
	
               



if __name__ == '__main__':  
    app.debug=True
    app.run()
