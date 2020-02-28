from flask import Flask, render_template,\
jsonify,request,abort
import requests
from datetime import datetime
from flask_mysqldb import MySQL
app=Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB'] = 'rideshare'
mysql = MySQL(app)

def is_sha1(maybe_sha):
    if len(maybe_sha) != 40:
        return False
    try:
        sha_int = int(maybe_sha, 16)
    except ValueError:
        return False
    return True
@app.route("/api/v1/users",methods=["PUT"])
def add_user():
    if(request.method =="PUT"):
        dic={}
        username=request.get_json()["username"]
        password=request.get_json()["password"]
        if(is_sha1(password)):
            dic["flag"]=1
            dic["username"]=username
            dic["password"]=password
            x=requests.post("http://34.195.180.229/api/v1/db/write",json=dic)
            result=x.json()["result"]
            if result==1:
                return " ",201
            else:
                return " ",400
        else:
            return " ",400
    else:
        return " ",405

@app.route("/api/v1/users/<username>",methods=["DELETE"])
def delete_user(username):
    if(request.method == "DELETE"):
        dic={}
        dic["flag"]=2
        dic["username"]=username
        x=requests.post("http://34.195.180.229/api/v1/db/read",json=dic)
        result=x.json()["value"]
        if(result==0):
            return " ",400
        else:
            x=requests.post("http://34.195.180.229/api/v1/db/write",json=dic)
            status=x.json()["result"]
            if(status):
              return " ", 200
    else:
        return " ",405
        

@app.route("/api/v1/db/write",methods=["POST"])
def write_to_db():
    flag=request.get_json()["flag"]
    if(flag == 1):
        username=request.get_json()["username"]
        password=request.get_json()["password"]
        cursor = mysql.connection.cursor()
        try:
            cursor.execute("INSERT INTO users (Name,Password) values (%s,%s)", (username,password))
            dic={}
            dic["result"]=1
            mysql.connection.commit()
            cursor.close()
            return dic
        except:
            dic={}
            dic["result"]=2
            mysql.connection.commit()
            cursor.close()
            return dic
    if(flag==2):
        username=request.get_json()["username"]
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM users WHERE Name=%s",(username,))
        dic={}
        dic["result"]=1
        mysql.connection.commit()
        cursor.close()
        return dic
    if(flag==3):
        dic={}
        source=request.get_json()["source"]
        destination=request.get_json()["destination"]
        username=request.get_json()["created_by"]
        timestamp=request.get_json()["timestamp"]
        cursor= mysql.connection.cursor()
        src=int(source)
        dst=int(destination)
        if src < 0 or dst > 198 :
            dic["result"] = -1
            return dic
        if(source == destination):
            dic["result"]=0
            return dic 
        else:
            cursor.execute("INSERT INTO ride(Source,Destination,Created_by,timestamp) values (%s,%s,%s,%s)",(source,destination,username,timestamp))
            dic["result"]=1
            mysql.connection.commit()
            mysql.connection.commit()
            cursor.close()
        return dic
    if(flag==4):
        username=request.get_json()["username"]
        rideid=request.get_json()["rideid"]
        cursor=mysql.connection.cursor()
        cursor.execute("INSERT INTO ridetable(ID,Username) values(%s,%s)",(rideid,username));
        mysql.connection.commit()
        cursor.close()
        dic={}
        dic["result"]=1
        return dic
    if(flag==6):
        dic={}
        rideid=request.get_json()["rideid"]
        cursor=mysql.connection.cursor()
        cursor.execute("DELETE FROM ride WHERE ID=%s",rideid)
        mysql.connection.commit()
        cursor.close()
        dic["result"]=1
        return dic

@app.route("/api/v1/db/read",methods=["POST"])
def read_from_db():
    flag=request.get_json()["flag"]
    if flag==1:
        source=request.get_json()["source"]
        destination=request.get_json()["destination"]
        time=datetime.now()
        if source==destination:
            dic={}
            dic["value"]= -1
            return dic
        src=int(source)
        dst=int(destination)
        if src < 0 or dst > 198 :
            dic={}
            dic["value"] = -2
            return dic
        cursor =mysql.connection.cursor()
        cursor.execute("SELECT * FROM ride WHERE source = %s and destination= %s",(source,destination))
        row=cursor.fetchall()
        if(len(row)==0):
            dic={}
            dic["value"]=0
            return dic
        else:
            dic={}
            dic["value"]= -3    
            li=[]
            for x in row:
                di={}
                timestamp=str(x[4])
                #print(timestamp)
                datetime_object = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                if(datetime_object > time):
                    di={}
                    dic["value"]=1
                    timestamp=datetime_object.strftime("%d-%m-%Y %S:%M:%H")
                    di["ID"]=x[0]
                    di["created_by"]=x[3]
                    #datetime_object = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                    timestamp=datetime_object.strftime("%d-%m-%Y %S:%M:%H")
                    di["timestamp"]=timestamp
                    li.append(di)
                    
            dic["1"]=li
            return dic


    if flag==4:
        dic={}
        rideid=request.get_json()["rideid"]
        username=request.get_json()["username"]
        cursor=mysql.connection.cursor()
        cursor.execute("SELECT * from users where Name=%s",(username,))
        a=cursor.fetchone()
        if(len(a)==0):
          dic["1"]=0
        else:
          dic["1"]=1
        cursor.execute("SELECT * from ride where ID=%s",(rideid,))
        a=cursor.fetchone()
        if(len(a)==0):
          dic["2"]=0
        else:
          dic["2"]=1
          cursor.close()
        return dic

    if flag==5:
        dic={}
        dic["1"]=0
        rideid=request.get_json()["rideid"]
        cursor=mysql.connection.cursor()
        cursor.execute("SELECT * FROM ride WHERE ID=%s",(rideid,))
        a=cursor.fetchone()
        if(len(a)==0):
            dic["1"]=1
            return dic
        else:
            dic["rideId"]=rideid
            cursor.execute("SELECT * FROM ride WHERE ID=%s",(rideid,))
            a=cursor.fetchone()
            dic["Created_by"]=a[3]
            cursor.execute("SELECT * FROM ridetable WHERE ID=%s",(rideid,))
            a=cursor.fetchall()
            li=[]
            for row in a :
                li.append(row[1])
            dic["users"]=li
            cursor.execute("SELECT * FROM ride WHERE ID=%s",(rideid,))
            a=cursor.fetchone()
            timestamp=str(a[4])
            datetime_object = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
            timestamp=datetime_object.strftime("%d-%m-%Y %S:%M:%H")
            dic["timestamp"]=timestamp
            dic["source"]=a[1]
            dic["destination"]=a[2]
            return dic
    if flag==6:
        rideid=request.get_json()["rideid"]
        cursor=mysql.connection.cursor()
        cursor.execute("SELECT * FROM ride WHERE ID=%s",(rideid,))
        a=cursor.fetchall()
        dic={}
        if len(a)==0:
            dic["1"]=1
        else:
            dic["1"]=0
        return dic


    else:
        username=request.get_json()["username"]
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE Name=%s", (username,))
        a=cursor.fetchall()
        if len(a)==0:
            dic={}
            dic["value"]=0
            cursor.close()
            return dic
        else :
            dic={}
            dic["value"]=1
            cursor.close()
            return dic


@app.route("/api/v1/rides",methods=["POST"])
def create_ride():
    if(request.method == "POST"):
        dic={}
        dic['flag']=3
        dic['created_by']=request.get_json()["created_by"]
        dic['source']=request.get_json()["source"]
        dic['destination']=request.get_json()["destination"]
        timestamp=request.get_json()["timestamp"]
        datetime_object = datetime.strptime(timestamp, '%d-%m-%Y %S:%M:%H')
        timestamp=datetime_object.strftime("%Y-%m-%d %H:%M:%S")
        dic['timestamp']=timestamp
        dic1={}
        dic1["flag"]=3
        dic1["username"]=request.get_json()["created_by"]
        x=requests.post("http://34.195.180.229/api/v1/db/read",json=dic1)
        status=x.json()["value"]
        if(status == 0):
            return "User does not exist",400
        else:
            x=requests.post("http://34.195.180.229/api/v1/db/write",json=dic)
            status=x.json()["result"]
            if(status == -1):
                return "Invalid Source/Destination",400
            if(status==0):
                return "Invalid Source/Destination",400
            if(status ==1):
                return " ",201
    else: 
        return " ",405

@app.route("/api/v1/rides",methods=["GET"])
def list_rides():
    if(request.method == "GET"):
        source = request.args['source']
        destination = request.args['destination']
        dic={}
        dic["flag"]=1
        dic["source"]=source
        dic["destination"]=destination
        x=requests.post("http://34.195.180.229/api/v1/db/read",json=dic)
        status=x.json()["value"]
        if(status==0):
            return " ",204
        elif(status == -1):
            return "Invalid Source/Destination",400
        elif(status == -2):
            return "Invalid Source/Destination",400
        elif(status == -3):
            return " ",204
        else:
            dic=x.json()
            lis=dic["1"]
            return str(lis),200
    else:
        return " ",405

@app.route("/api/v1/rides/<rideid>",methods=["POST"])
def join_ride(rideid):
    if(request.method=="POST"):
        username=request.get_json()["username"]
        dic={}
        dic["flag"]=4
        dic["rideid"]=rideid
        dic["username"]=username
        x=requests.post("http://34.195.180.229/api/v1/db/read",json=dic)
        dic1=x.json()
        a=dic1["1"]
        b=dic1["2"]
        if(a==0 and b==1):
          return " ",204
        elif(a==1 and b==0):
          return " ",204
        elif(a==0 and b==0):
          return " ",204
        else:
          x=requests.post("http://34.195.180.229/api/v1/db/write",json=dic)
          status=x.json()["result"]
          if(status):
            return " ",200
          else:
            return " ",204
    else:
        return " ",405

@app.route("/api/v1/rides/<rideid>",methods=["GET"])
def list_ride_details(rideid):
    if(request.method=="GET"):
        dic={}
        dic["rideid"]=rideid
        dic["flag"]=5 
        x=requests.post("http://34.195.180.229/api/v1/db/read",json=dic)
        a=x.json()["1"]
        if(a):
            return " ",204
        else:
            di={}
            di=x.json()
            del di["1"]
            return di,200
    else:
        return " ",405

@app.route("/api/v1/rides/<rideid>",methods=["DELETE"])
def delete_ride(rideid):
    if(request.method=="DELETE"):
        dic={}
        dic["flag"]=6
        dic["rideid"]=rideid
        x=requests.post("http://34.195.180.229/api/v1/db/read",json=dic)
        a=x.json()["1"]
        if(a):
            return "Ride does not exist",400
        x=requests.post("http://34.195.180.229/api/v1/db/write",json=dic)
        a=x.json()["result"]
        if(a):
            return " ",200
    else:
        return " ",405

if __name__ == '__main__':  
    app.debug=True
    app.run()