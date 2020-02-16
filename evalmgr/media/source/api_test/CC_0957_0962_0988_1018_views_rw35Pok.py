from flask import Flask,render_template,jsonify,request,abort
from flask_sqlalchemy import SQLAlchemy
import re
import requests
import datetime
from constants import Place

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///rideShare.db'
db=SQLAlchemy(app)
db.session.execute('pragma foreign_keys=on')
db.session.execute("create table if not exists user(username varchar(200) not null,\
                                                    password varchar(40) not null,\
                                                    primary key(username));")
db.session.execute("create table if not exists ride(rideId integer not null,\
                                                    created_by varchar(200) not null,\
                                                    timeStamp varchar(200) not null,\
                                                    source varchar(20) not null,\
                                                    destination varchar(20) not null,\
                                                    primary key(rideId),\
                                                    foreign key(created_by) references user(username) on delete cascade);")
db.session.execute("create table if not exists participant(rideId integer not null,\
                                                           username varchar(200) not null,\
                                                           primary key(rideId,username),\
                                                           foreign key(rideId) references ride(rideId) on delete cascade,\
                                                           foreign key(username) references user(username) on delete cascade);")

db.session.commit()
def date_validate(timestamp):
    date_format = '%d-%m-%Y:%S-%M-%H'
    try:
        date_obj = datetime.datetime.strptime(timestamp, date_format)
        return 1
    except ValueError:
        return 0

#databse write operation
@app.route("/api/v1/db/write",methods=["POST"])
def write():
    data=request.get_json()["insert"]
    column=request.get_json()["column"]
    table=request.get_json()["table"]
    data1=[]
    for i in data:
        if type(i) is str:
            print(type(i))
            data1.append("\'"+i+"\'")
        else:
            data1.append(str(i))
    #data=list(map(lambda x:'\''+x+'\'' if isinstance(x,str),data))	#inserting single qoute '' to data
    column=",".join(column)	#combining column with join
    data1=",".join(data1)#combining data with join
    db.session.execute('pragma foreign_keys=on')
    try:
    	qry="insert into "+table+"("+column+") values("+data1+");"
    	db.session.execute(qry)
    	db.session.commit()
    	return {}
    except Exception as e:
    	print(e)
    	abort(400)

@app.route("/api/v1/db/read",methods=["POST","DELETE"])
def read():
    if request.method=="POST":	#to read from data
        a={}
        table=request.get_json()["table"]
        column=request.get_json()["columns"]
        where=request.get_json()["where"]
        column=",".join(column)
        qry="select "+column+" from "+table+ " where "+where+ ";"
        print(qry)
        db.session.execute('pragma foreign_keys=on')
        try:
            result=db.session.execute(qry)
            count=0
            for i in result:
                a[count]=list(i)
                count+=1
            return jsonify(a)
        except Exception as e:
            print(e)
            abort(400)
    elif request.method=="DELETE":	#to delete from table
        table=request.get_json()["table"]
        where=request.get_json()["where"]
        qry="delete from "+table+" where "+where+";"
        db.session.execute('pragma foreign_keys=on')        
        try:
            db.session.execute(qry)
            db.session.commit()
            return {}
        except Exception as e:
            print(e)
            abort(400)

#1st task inserting user to the table
@app.route("/api/v1/users",methods=["PUT"])
def addUser():
    if request.method=="PUT":
        try:
            username=request.get_json()["username"]
            password=request.get_json()["password"]
            crrt=re.search("[0-9|a-f|A-F]{40}",password)
            if(crrt and len(password)==40):
                a={"insert":[username,password],"column":["username","password"],"table":"user"} #making json format
                resp=requests.post("http://34.206.70.57/api/v1/db/write",json=a)    #send post request to database url  to wite to database
                #resp.status_code, .json()
                if resp.status_code==200:       #resp.json() gives passed json
                    return {},201
                elif resp.status_code==400:
                    return {},400
                else:
                    abort(resp.status_code)
        except Exception as e:
            print(e)
            abort(400)
    else:
        abort(405)
@app.route("/api/v1/users/<username>",methods=["DELETE"])
def removeUser(username):
    a={"table":"user","columns":["username"],"where":"username='"+username+"'"}
    resp=requests.post("http://34.206.70.57/api/v1/db/read",json=a)
    if(len(resp.json())>0):	#if exist delete
        resp=requests.delete("http://34.206.70.57/api/v1/db/read",json=a)
        if resp.status_code==200:
           # b={"table":"participant","columns":["username"],"where":"username='"+username+"'"}
            #resp1=requests.delete("http://34.206.70.57/api/v1/db/read",json=b)
            #if resp1.status_code==200:
                return {}
            #else:
               # {},400
        else:
            abort(resp.status_code)
    else:
    	abort(400)
        
@app.route("/api/v1/rides",methods=["POST","GET"])
def newRide():
    ride_list=[]
    if request.method=="POST":

        try:
            created_by=request.get_json()["created_by"]
            timeStamp=request.get_json()["timestamp"]
            source=request.get_json()["source"]
            destination=request.get_json()["destination"]
            if(int(source) in Place._value2member_map_ and int(destination) in Place._value2member_map_):
                if(date_validate(timeStamp)):
                    a={"insert":[created_by,timeStamp,source,destination],\
                        "column":["created_by","timestamp","source","destination"],"table":"ride"}
                    resp=requests.post("http://34.206.70.57/api/v1/db/write",json=a)
                    if resp.status_code==200:
                        a={"columns":["rideId"],"table":"ride","where":"timestamp='"+timeStamp+"' and created_by='"+created_by+"'"}
                        rides=requests.post("http://34.206.70.57/api/v1/db/read",json=a)
                        rides=rides.json()
                        i=list(rides.keys())[-1]
                        i = rides[i]
                        b={"insert":[created_by,str(i[0])],\
                        "column":["username","rideId"],"table":"participant"}
                        print(b)
                        resp=requests.post("http://34.206.70.57/api/v1/db/write",json=b)
                        if resp.status_code==200:
                            return {},201
                        else:
                            abort(resp.status_code)
                    else:
                        abort(resp.status_code)
                else:
                    abort(400)
            else:
                abort(400)
        except Exception as e:
    	    print(e)
    	    abort(400)
    elif request.method=="GET":
        try:
            source=request.args.get('source')
            destination=request.args.get('destination')
            a={"columns":["*"],"table":"ride","where":"source='"+source+"' and destination='"+destination+"'"}
            rides=requests.post("http://34.206.70.57/api/v1/db/read",json=a)
            if rides.status_code==200:
                rides=rides.json()
                for ride in rides:
                    ptime=datetime.datetime.now().strftime('%Y-%m-%d:%H-%M-%S')
                    user_time=rides[ride][2]
                    user_time=datetime.datetime.strptime(user_time,\
                        '%d-%m-%Y:%S-%M-%H').strftime('%Y-%m-%d:%H-%M-%S')
                    a={}
                    if(ptime<user_time):
                        a["rideId"]=rides[ride][0]
                        a["username"]=rides[ride][1]
                        a["timestamp"]=rides[ride][2]
                        ride_list.append(a)
                if(len(ride_list)==0):
                    return jsonify(ride_list),204
                return jsonify(ride_list)               
            else:
                abort(resp.status_code)

        except Exception as e:
            print(e)
            abort(400)

@app.route("/api/v1/rides/<rideid>",methods=["DELETE","GET","POST"])
def Ridemodify(rideid):
    if request.method=="GET":
        try:
            a={"table":"ride","columns":["rideId","created_by","timeStamp","source","destination"],"where":"rideId="+rideid}
            resp1=requests.post("http://34.206.70.57/api/v1/db/read",json=a)
            print(type(resp1.json()),len(resp1.json()))
            if(len(resp1.json())>0):
                b={"table":"participant","columns":["username"],"where":"rideId="+rideid}
                resp2=requests.post("http://34.206.70.57/api/v1/db/read",json=b)
                gresp1=list(resp1.json().values())
                gresp2=list(resp2.json().values())
                gresp3=list()
                for i in range(len(gresp2)):
                    gresp3.append(gresp2[i][0])
                gresp2=gresp3
                gresp=[('rideId',gresp1[0][0]),('created_by',gresp1[0][1]),('users',gresp2),('Timestamp',gresp1[0][2]),('source',gresp1[0][3]),('destination',gresp1[0][4])]
                resp=dict(gresp)
                return jsonify(resp)
            else:
                return {},204
        except Exception as e:
            print(e)
            abort(400)
    elif request.method=="POST":
        try:
            user_name=request.get_json()['username']
            rideid=int(rideid)
            c={"insert":[rideid,user_name],"column":["rideId","username"],"table":"participant"}
            resp=requests.post("http://34.206.70.57/api/v1/db/write",json=c)
            if(resp.status_code==200):
                return {}
            else:
                abort(400)
        except Exception as e:
            print(e)
            abort(400)
    elif request.method=="DELETE":
        try:
            a={"table":"ride","columns":["rideId"],"where":"rideId="+rideid}
            resp=requests.post("http://34.206.70.57/api/v1/db/read",json=a)
            if resp.status_code==200:
                resp1=requests.delete("http://34.206.70.57/api/v1/db/read",json=a)
                if(resp1.status_code==200):
                    return {}
                    #b={"table":"participant","columns":["rideId"],"where":"rideId="+rideid}
                    #resp2=requests.delete("http://34.206.70.57/api/v1/db/read",json=b)
                    #if resp2.status_code==200:
                        
                    #else:
                        #abort(resp2.status_code)
                else:
                    print("here1")
                    abort(resp1.status_code)
            else:
                print("here2")
                abort(resp.status_code)
        except Exception as e:
            print(e)
            abort(400)

if __name__=="__main__":
      app.debug=True #one parameter ip and  port
      app.run()
