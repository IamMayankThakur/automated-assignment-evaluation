from flask import Flask, render_template,jsonify,request,abort,Response,json
import requests
import sqlite3
import re
from datetime import datetime
import csv

app=Flask(__name__)

@app.route("/api/v1/users",methods=["PUT"])
def addUser():
    if(request.method == 'PUT'):
        try:
            username = request.get_json()["username"]
            password = request.get_json()["password"]
        except KeyError:
            return jsonify({}),400
        checkpwd = re.findall('^[0-9a-fA-Z]{40}$',password)
        if(len(checkpwd) == 0):
            return jsonify({}),400

        readresponse = requests.post("http://ec2-52-2-65-28.compute-1.amazonaws.com/api/v1/db/read",json={"OP":1,"table":"Users","where":"username","value":username})
        code = readresponse.status_code
        
        if(code == 500):
            return jsonify({}),500
        elif(code == 201):
            return jsonify({}),400
        elif(code == 204):
            detlist = [username,password]
            writeresponse = requests.post("http://ec2-52-2-65-28.compute-1.amazonaws.com/api/v1/db/write",json={"OP":1,"table":"Users","value":detlist})
            if(writeresponse.status_code == 201):
                return jsonify({}),201
            elif(writeresponse.status_code == 500):
                return jsonify({}),500
    else:
        return Response(status=405)

@app.route("/api/v1/users/<username>",methods=["DELETE"])
def removeUser(username):
    if(request.method == 'DELETE'):
        readresponse = requests.post("http://ec2-52-2-65-28.compute-1.amazonaws.com/api/v1/db/read",json={"OP":1,"table":"Users","where":"username","value":username})
        code = readresponse.status_code
        if(code == 500):
            return jsonify({}),500
        elif(code == 204):
            return jsonify({}),400
        elif(code == 201):
            writeresponse = requests.post("http://ec2-52-2-65-28.compute-1.amazonaws.com/api/v1/db/write",json={"OP":2,"table":"Users","where":"username","value":username})
            if(writeresponse.status_code == 500):
                return jsonify({}),500
            elif(writeresponse.status_code == 200):
                return jsonify({}),200
    else:
        return Response(status=405)


@app.route("/api/v1/rides",methods=["POST"])
def createRide():
    if(request.method == 'POST'):
        username = request.get_json()["created_by"]
        source = request.get_json()["source"]
        destination = request.get_json()["destination"]
        if(source == destination):
            return jsonify({}),400
        readresponse = requests.post("http://ec2-52-2-65-28.compute-1.amazonaws.com/api/v1/db/read",json={"OP":1,"table":"Users","where":"username","value":username})
        code = readresponse.status_code
        
        if(code == 500):
            return jsonify({}),500
        elif(code == 204):
            return jsonify({}),400
        elif(code == 201):
            
            time = request.get_json()["timestamp"]
            arr = time.split(':')
            dd,mm,yy = arr[0].split('-')
            ss,mi,hh = arr[1].split('-')
            try:
                newDate = datetime(int(yy),int(mm),int(dd),int(hh),int(mi),int(ss))
            except ValueError:
                return jsonify({}),400
            sdcheck = requests.post("http://ec2-52-2-65-28.compute-1.amazonaws.com/api/v1/db/read",json={"OP":4,"source":source,"destination":destination})
            if(sdcheck.status_code == 400):
                return jsonify({}),400
            writeresponse = requests.post("http://ec2-52-2-65-28.compute-1.amazonaws.com/api/v1/db/write",json={"OP":3,"username":username,"source":source,"destination":destination,"timestamp":time})
            if(writeresponse.status_code == 201):
                return jsonify({}),201
            elif(writeresponse.status_code == 500):
                return jsonify({}),500
    else:
        return Response(status=405)

@app.route("/api/v1/rides",methods=["GET"])
def listAllUpComingRides():
    if(request.method == 'GET'):
        source = request.args['source']
        destination = request.args['destination']
        if(source == destination):
            return jsonify({}),400
        readresponse = requests.post("http://ec2-52-2-65-28.compute-1.amazonaws.com/api/v1/db/read",json={"OP":3,"source":source,"destination":destination}) 
        if(readresponse.status_code == 500):
            return jsonify({}),500
        elif(readresponse.status_code == 400):
            return jsonify({}),400
        elif(readresponse.status_code == 200):
            if(len(readresponse.json()) == 0):
                return jsonify({}),204
            return jsonify(readresponse.json()),200
    else:
        return Response(status=405)


@app.route("/api/v1/rides/<rideId>",methods=["GET"])
def listRideDetails(rideId):
    if(request.method == 'GET'):
        readresponse = requests.post("http://ec2-52-2-65-28.compute-1.amazonaws.com/api/v1/db/read",json={"OP":2,"table":"Ride","where":"Ride_id","value":rideId})
        code = readresponse.status_code
        
        if(code == 500):
            return jsonify({}),500
        elif(code == 204):
            return jsonify({}),400
        elif(code == 200):
            if(len(readresponse.json()) == 0):
                return jsonify({}),204
            return jsonify(readresponse.json()),200
    else:
        return Response(status=405)

@app.route("/api/v1/rides/<rideId>",methods=["POST"])
def joinRide(rideId):
    if(request.method == 'POST'):
        rideresponse = requests.post("http://ec2-52-2-65-28.compute-1.amazonaws.com/api/v1/db/read",json={"OP":2,"table":"Ride","where":"Ride_id","value":rideId})
        if(rideresponse.status_code == 500):
            return jsonify({}),500
        elif(rideresponse.status_code == 204):
            return jsonify({}),400
        elif(rideresponse.status_code == 200):
            username = request.get_json()["username"]
            created = rideresponse.json()['created_by']
            if(username == created):
                return jsonify({}),400
        
            userresponse = requests.post("http://ec2-52-2-65-28.compute-1.amazonaws.com/api/v1/db/read",json={"OP":1,"table":"Users","where":"username","value":username})
            if(userresponse.status_code == 500):
                return jsonify({}),500
            elif(userresponse.status_code == 204):
                return jsonify({}),400
            elif(userresponse.status_code == 201):
                detlist = [rideId,username]
                writeresponse = requests.post("http://ec2-52-2-65-28.compute-1.amazonaws.com/api/v1/db/write",json={"OP":1,"table":"joinRide","value":detlist})
                if(writeresponse.status_code == 500):
                    return jsonify({}),500
                elif(writeresponse.status_code == 201):
                    return jsonify({}),200
    else:
        return Response(status=405)

@app.route("/api/v1/rides/<rideId>",methods=["DELETE"])
def removeRide(rideId):
    if(request.method == 'DELETE'):
        readresponse = requests.post("http://ec2-52-2-65-28.compute-1.amazonaws.com/api/v1/db/read",json={"OP":1,"table":"Ride","where":"Ride_id","value":rideId})
        code = readresponse.status_code
        if(code == 500):
            return jsonify({}),500
        elif(code == 204):
            return jsonify({}),400
        elif(code == 201):
            writeresponse = requests.post("http://ec2-52-2-65-28.compute-1.amazonaws.com/api/v1/db/write",json={"OP":2,"table":"Ride","where":"Ride_id","value":rideId})
            if(writeresponse.status_code == 500):
                return jsonify({}),500
            elif(writeresponse.status_code == 200):
                return jsonify({}),200
    else:
        return Response(status=405)


@app.route("/api/v1/db/read",methods=["POST"])
def readDB():
    OP = request.get_json()["OP"]
    try:
        conn = sqlite3.connect("Cloud.db")
    except:
        return Response(status=500)
    
    if(OP == 3):
        source = request.get_json()['source']
        destination = request.get_json()['destination']
        cur = conn.execute("SELECT * FROM Area WHERE area_no=? or area_no=?",(source,destination))
        rows = cur.fetchall()
        if(len(rows) != 2):
            return Response(status=400)
        cur1 = conn.execute("SELECT * FROM Ride WHERE src=? and dst=?",(source,destination))
        result = cur1.fetchall()
        userdata = []
        for row in result:
            timesplit = row[2].split(" ")
            yy,mm,dd = timesplit[0].split("-")
            hh,mi,ss = timesplit[1].split(":")
            time = dd+"-"+mm+"-"+yy+":"+ss+"-"+mi+"-"+hh
            now = datetime.now()
            currentdt = now.strftime("%d/%m/%Y %H:%M:%S")
            cdd,cmm,cyy = currentdt.split(' ')[0].split('/')
            ch,cm,cs = currentdt.split(' ')[1].split(':')

            check = (datetime(int(cyy),int(cmm),int(cdd),int(ch),int(cm),int(cs)) < datetime(int(yy),int(mm),int(dd),int(hh),int(mi),int(ss)))
            if(check):
                data = {"rideId":str(row[0]),"username":row[1],"timestamp":time}
                userdata.append(data)
        
        response = app.response_class(response=json.dumps(userdata),status=200,mimetype='application/json')
        conn.close()
        return response

    elif(OP == 4):
        source = request.get_json()['source']
        destination = request.get_json()['destination']
        cur = conn.execute("SELECT * FROM Area WHERE area_no=? or area_no=?",(source,destination))
        rows = cur.fetchall()
        if(len(rows) != 2):
            return Response(status=400)
        else:
            return Response(status=201)

    else:
        table = request.get_json()["table"]
        where = request.get_json()["where"]
        value = request.get_json()['value']
        cur = conn.execute("SELECT * FROM "+table+" WHERE "+where+"=?",(value,))
        rows = cur.fetchall()
        if(len(rows) == 0):
            return Response(status=204)
        else:
            if(OP == 1):
                return Response(status=201)
            elif(OP == 2):
                cur1 = conn.execute("SELECT new_users FROM joinRide WHERE join_id=?",(value,))
                userrows = cur1.fetchall()
                conn.close()
                userdata = []
                for row in userrows:
                    userdata.append(row[0])
                timesplit = rows[0][2].split(" ")
                yy,mm,dd = timesplit[0].split("-")
                hh,mi,ss = timesplit[1].split(":")
                time = dd+"-"+mm+"-"+yy+":"+ss+"-"+mi+"-"+hh
                result = {"rideId":value,"created_by":rows[0][1],"users":userdata,"timestamp":time,"source":str(rows[0][3]),"destination":str(rows[0][4])}
                response = app.response_class(response=json.dumps(result),status=200,mimetype='application/json')
                return response


@app.route("/api/v1/db/write",methods=["POST"])
def writeDB():
    OP = request.get_json()["OP"]
    try:
        conn = sqlite3.connect("Cloud.db")
    except:
        return Response(status=500)

    if(OP == 1):
        table = request.get_json()['table']
        value = request.get_json()['value']
        try:
            conn.execute("PRAGMA foreign_keys = on")
            conn.execute("INSERT INTO "+table+" VALUES(?,?)", (value[0],value[1]))
            conn.commit()
            conn.close()
            return Response(status=201)
        
        except:
            return Response(status=500) #Not Final

    elif(OP == 2):
        table = request.get_json()["table"]
        where = request.get_json()["where"]
        value = request.get_json()['value']
        try:
            conn.execute("PRAGMA foreign_keys = on")
            conn.execute("DELETE FROM "+table+" WHERE "+where+"=?",(value,))
            conn.commit()
            conn.close()
            return Response(status=200)
        except:
            return Response(status=500) #Not Final

    elif(OP == 3):
        username = request.get_json()["username"]
        source = request.get_json()["source"]
        destination = request.get_json()["destination"]
        time = request.get_json()["timestamp"]
        arr = time.split(':')
        dd,mm,yy = arr[0].split('-')
        ss,mi,hh = arr[1].split('-')
        time = yy+"-"+mm+"-"+dd+" "+hh+":"+mi+":"+ss

        try:
            conn.execute("PRAGMA foreign_keys = on")
            conn.execute("INSERT INTO Ride(Time_stamp,src,dst,created_by) VALUES(?,?,?,?)", (time,int(source),int(destination),username))
            conn.commit()
            conn.close()
            return Response(status=201)
        except:
            return Response(status=500)
    

if __name__ == '__main__': 
    
    conn = sqlite3.connect("Cloud.db")
    usertable = "CREATE TABLE IF NOT EXISTS Users(username VARCHAR(20) NOT NULL PRIMARY KEY,password VARCHAR(20) NOT NULL);"
    areatable = "CREATE TABLE IF NOT EXISTS Area(area_no INTEGER NOT NULL PRIMARY KEY,area_name VARCHAR(50) NOT NULL);"
    ridetable = '''CREATE TABLE IF NOT EXISTS Ride(
	            Ride_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	            created_by VARCHAR(20) NOT NULL,
	            Time_stamp DATETIME NOT NULL,
                src INTEGER NOT NULL,
                dst INTEGER NOT NULL,
                
                CONSTRAINT RIDEFK FOREIGN KEY(created_by) REFERENCES Users(username) ON DELETE CASCADE ON UPDATE CASCADE,
                CONSTRAINT SRCFK FOREIGN KEY(src) REFERENCES Area(area_no) ON DELETE CASCADE ON UPDATE CASCADE,
                CONSTRAINT DSTFK FOREIGN KEY(dst) REFERENCES Area(area_no) ON DELETE CASCADE ON UPDATE CASCADE
	            );
                '''
    
    jointable = '''CREATE TABLE IF NOT EXISTS joinRide(
                join_id INTEGER NOT NULL, 
                new_users VARCHAR(20) NOT NULL,
                
                CONSTRAINT JFK FOREIGN KEY(join_id) REFERENCES Ride(Ride_id) ON DELETE CASCADE ON UPDATE CASCADE,
                CONSTRAINT JOINFK FOREIGN KEY(new_users) REFERENCES Users(username) ON DELETE CASCADE ON UPDATE CASCADE
                );
                '''
    conn.execute(usertable)
    conn.execute(areatable)
    conn.execute(ridetable)
    conn.execute(jointable)

    with open('AreaNameEnum.csv','r') as csv_file:
        csvreader = csv.reader(csv_file,delimiter=',')
        l = False
        for row in csvreader:
            if(l):
                try:
                    conn.execute("INSERT INTO Area VALUES(?,?)",(int(row[0]),row[1]))
                    conn.commit()
                except sqlite3.IntegrityError:
                    break
            else:
                l = True
    conn.close()
    app.run(host='0.0.0.0',debug=True)
