from flask import Flask, render_template, request , jsonify , Response , json
import re,requests,datetime
from sqlalchemy.exc import SQLAlchemyError
from constants import areas
import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class users(db.Model):
    __tablename__= 'users'
    username = db.Column(db.String(100),primary_key=True)
    password = db.Column(db.String(40),nullable = False)

class rides(db.Model):
    __tablename__ = 'rides'
    rideID = db.Column(db.Integer,primary_key=True,autoincrement=1)
    user_created = db.Column(db.String(100),nullable=False)
    timestamp = db.Column(db.String(120),nullable=False)
    source = db.Column(db.String(100),nullable=False)
    destination = db.Column(db.String(100),nullable=False)


class gang(db.Model):
    __tablename__='gang'
    username =db.Column(db.String(100),nullable = False)
    rideid = db.Column(db.Integer, nullable=False)
    __table_args__ = (
        db.PrimaryKeyConstraint('username', 'rideid'),
        {},
    )

def isValidSHA1(s): 
    return re.match("^[a-fA-F0-9]{40}$",s)

@app.route('/api/v1/db/write', methods = ["GET","PUT","POST","DELETE"])
def write_db():
    if request.method == "POST":
        try:
            content = request.get_json()
            c = content["column"]
            print(c,len(c))
            columns = ', '.join([item for item in c]) 
            values = content["insert"]
            print(values,len(values))
            v = ""
            for x in values:
                if type(x) == int:
                    v = v + ",{}".format(x)
                if type(x) == str:
                    v = v + ",'{}'".format(x)
            v = v.strip(",")
            print("INSERT INTO {}({}) VALUES ({})".format(content["table"],columns,v))
            status = db.engine.execute("INSERT INTO {}({}) VALUES ({})".format(content["table"],columns,v))

            where = ""

            for i in range(len(values)):
                if type(values[i]) == int:
                    where += " AND {} = {}".format(c[i],values[i])
                if type(values[i]) == str:
                    where += " AND {} = '{}'".format(c[i],values[i])

            print(where)
            where = where.strip(' AND')
            print("SELECT * FROM {}  WHERE {}".format(content["table"],where))
            result = db.engine.execute("SELECT * FROM {}  WHERE {}".format(content["table"],where))
            data = result.fetchall()
            l = []
            for i in data:
                l.append(list(i))
            print(l)
            response = app.response_class(response=json.dumps(l),status= 200 , mimetype="application/json")
            return response
        except SQLAlchemyError:
            return Response("",status=400,mimetype="/application/json")



@app.route('/api/v1/db/read', methods = ["GET","PUT","POST","DELETE"])
def read_db():
    print(request.method)
    if request.method == "POST":
        content = request.get_json()
        columns = content["column"]
        columns = ', '.join([item for item in columns])
        print("SELECT {} FROM {} WHERE {}".format(columns,content["table"],content["where"]))
        try:
            result = db.engine.execute("SELECT {} FROM {} WHERE {}".format(columns,content["table"],content["where"]))
            data = result.fetchall()
            #print("Data:-",data)
            l = []
            for i in data:
                l.append(list(i))
            print(l)
            response = app.response_class(response=json.dumps(l),status= 200 , mimetype="application/json")
            return response
        except SQLAlchemyError:
            return Response("",status=400,mimetype="/application/json")

    if request.method == "DELETE":
        content = request.get_json()
        try:
            result = db.engine.execute("DELETE FROM {} WHERE {}".format(content["table"],content["where"]))
            return Response("",status=200,mimetype="/application/json")
        except SQLAlchemyError:
            return Response("",status=400,mimetype="/application/json")

#Should remove rides and gang if user is removed
@app.route('/api/v1/users/<username>' , methods = ["GET","PUT","POST","DELETE"])
def remove_user(username):
    print("Username ",username)
    print(request.method)
    if request.method == "DELETE":
        if username != "":
            url = "http://localhost:5000/api/v1/db/read"
            data1 = {"table":"users","where":"username='{}'".format(username),"column":["username","password"]}
            r1 = requests.post(url = url , json = data1)
            if len(r1.json()) == 0:
                return Response("",status=400,mimetype="/application/json")

            data = {"table":"users","where":"username='{}'".format(username)}
            
            r = requests.delete(url= url,json = data)
            if r.status_code != 200:
                return Response("",status=400,mimetype="/application/json")
            
            data = {"table":"rides","where":"user_created='{}'".format(username)}
            r = requests.delete(url= url,json = data)

            if r.status_code != 200:
                return Response("",status=400,mimetype="/application/json")

            data = {"table":"gang","where":"username='{}'".format(username)}
            r = requests.delete(url= url,json = data)

            if r.status_code == 200:
                return Response("",status=200,mimetype="/application/json")
            else:
                return Response("",status=400,mimetype="/application/json")     

        else:
            return Response("",status=400,mimetype="/application/json")
    else:
        return Response("",status=405,mimetype="/application/json")

#Completed
@app.route('/api/v1/users', methods = ["GET","PUT","POST","DELETE"])
def add_user():
    if request.method == "PUT":
        try:
            content=request.get_json()
            username= content["username"]
            password = content["password"]
            if isValidSHA1(password) and username != "" and password != "":
                data = {"table":"users","column":["username","password"],"insert":[username,password]}
                url ="http://localhost:5000/api/v1/db/write"
                r = requests.post(url = url, json = data)
                print(r.status_code)
                if r.status_code == 200:
                    return Response("",status=200,mimetype="/application/json")
                else:
                    return Response("",status=400,mimetype="/application/json")
            else:
                return Response("",status=400,mimetype="/application/json")
        except Exception:
            return Response("",status=400,mimetype="/application/json")
    else:
        return Response("",status=405,mimetype="/application/json")


        
#Completed
#Completed get details
@app.route('/api/v1/rides/<rideid>',methods = ["GET","PUT","POST","DELETE"])
def remove_ride(rideid):
    if request.method == "DELETE":
        try:
            url = "http://localhost:5000/api/v1/db/read"
            data1 = {"table":"rides","where":"rideID='{}'".format(rideid),"column":["rideID","source"]}
            r1 = requests.post(url = url , json = data1)
            print(r1.json())
            if len(r1.json()) == 0:
                return Response("",status=400,mimetype="/application/json")

            data = {"table":"rides","where":"rideID='{}'".format(rideid)}
            
            r = requests.delete(url= url,json = data)
            if r.status_code != 200:
                return Response("",status=400,mimetype="/application/json")
            
            data = {"table":"gang","where":"rideID='{}'".format(rideid)}
            r = requests.delete(url= url,json = data)

            if r.status_code == 200:
                    return Response("",status=200,mimetype="/application/json")
            else:
                    return Response("",status=400,mimetype="/application/json")
            

        except SQLAlchemyError:
            return Response("",status=400,mimetype="/application/json")

    if request.method == "GET":
        url = "http://localhost:5000/api/v1/db/read"
        data = {"table":"rides","where":"rideID='{}'".format(rideid),"column":["rideID","user_created","source","destination","timestamp"]}
        r1 = requests.post(url =url , json=data)
        if r1.status_code != 200 or len(r1.json()) == 0:
             return Response("",status=400,mimetype="/application/json")

        x=r1.json()[0]
        result = dict()
        creator= x[1]
        rideid = x[0]
        source = int(x[2])
        destination = int(x[3])
        timestamp = x[4]
        result["rideId"] = rideid
        result["created_by"] = creator
        result["users"] = []
        result["timestamp"] = timestamp
        result["source"] = source
        result["destination"] = destination 
        data1= {"table":"gang","where":"rideid='{}'".format(rideid),"column":["username","rideid"]}
        r2 = requests.post(url=url,json= data1)
        x1= r2.json()
        for i in x1:
            result["users"].append(i[0])
        
        response = app.response_class(response=json.dumps(result),status= 200 , mimetype="application/json")
        return response
    
    #Join rides
    if request.method == "POST":
        #Checking if ride exsists
        content = request.get_json()
        username = content["username"]
        url = "http://localhost:5000/api/v1/db/read"
        data = {"table":"rides","where":"rideID='{}'".format(rideid),"column":["rideID","user_created","source","destination","timestamp"]}
        r1 = requests.post(url =url , json=data)
        if r1.status_code != 200 or len(r1.json()) == 0:
             return Response("",status=400,mimetype="/application/json")

        #Checking is user exsists
        url = "http://localhost:5000/api/v1/db/read"
        data1 = {"table":"users","where":"username='{}'".format(username),"column":["username","password"]}
        r1 = requests.post(url = url , json = data1)
        if len(r1.json()) == 0 or r1.status_code != 200:
            return Response("",status=400,mimetype="/application/json")
        
        data = {"table":"gang","column":["username","rideid"],"insert":[username,rideid]}
        url ="http://localhost:5000/api/v1/db/write"
        r = requests.post(url = url, json = data)
        if r.status_code == 200:
                    return Response("",status=200,mimetype="/application/json")
        else:
                    return Response("",status=400,mimetype="/application/json")

    
    else:
        return Response("",status=405,mimetype="/application/json")


      
@app.route('/api/v1/rides', methods = ["GET","PUT","POST","DELETE"])
def add_ride():
    if request.method == "POST":
        try:
            content=request.get_json()
            username= content["created_by"]
            source = content["source"]
            destination = content["destination"]
            #datum = datetime.datetime.strptime(content["timestamp"],'%d-%m-%Y:%S-%M-%H')
            datum= content["timestamp"]
            #Error Checkiing
            #Created by in users table
            #source and destination in Area Enum csv
            #Time stamp is in correct format

            #Created by in users table
            url = "http://localhost:5000/api/v1/db/read"
            data1 = {"table":"users","where":"username='{}'".format(username),"column":["username","password"]}
            r1 = requests.post(url = url , json = data1)
            if len(r1.json()) == 0:
                print("user false")
                return Response("",status=400,mimetype="/application/json")
            
            #source and destination in Area Enum csv
            #print (areas.keys())
            if str(source) not in areas.keys() or str(destination) not in areas.keys():
                print("Source false")
                return Response("",status=400,mimetype="/application/json")

            url ="http://localhost:5000/api/v1/db/write"
            data = {"table":"rides","column":["user_created","timestamp","source","destination"],"insert":[username,datum,source,destination]}
            r = requests.post(url = url, json = data)
            x = r.json()
            ride_id = x[0][0]
            print(ride_id)
            
            if r.status_code == 200:
                        return Response("",status=200,mimetype="/application/json")
            else:
                        return Response("",status=400,mimetype="/application/json")


            
        except Exception:
            return Response("",status=400,mimetype="application/json") #For checking all the parameters

    
    elif request.method == "GET":
        print("Inside Get")
        source = request.args.get('source')
        destination = request.args.get('destination')
        if(source != "" and destination != ""):
            if(source == destination):
                return Response("",status=400,mimetype="/application/json")
            url = "http://localhost:5000/api/v1/db/read"
            if str(source) not in areas.keys() or str(destination) not in areas.keys():
                print("Source false")
                return Response("",status=400,mimetype="/application/json")
            data = {"table":"rides","where":"source='{}' AND destination='{}'".format(source,destination),"column":["rideID","user_created","timestamp"]}
            response = requests.post(url = url , json = data).json()
            if len(response) == 0:
                    return Response("",status=204,mimetype="/application/json")
            print(response)
            rides = []
            for ride in response:
                datum = datetime.datetime.strptime(ride[2],'%d-%m-%Y:%S-%M-%H')
                now = datetime.datetime.strptime(datetime.datetime.now().strftime("%d-%m-%Y:%S-%M-%H"),'%d-%m-%Y:%S-%M-%H')
                if(datum > now):
                    temp = dict()
                    temp['rideID'] = ride[0]
                    temp['username'] = ride[1]
                    temp['timestamp'] = ride[2]
                    rides.append(temp)
            return app.response_class(response=json.dumps(rides),status= 200 , mimetype="application/json")
        else:
            return Response("",status=400,mimetype="/application/json")
    else:
        return Response("",status=405,mimetype="/application/json")


    
if __name__ == '__main__':
    db.init_app(app)
    db.create_all()
    app.run(debug=True)