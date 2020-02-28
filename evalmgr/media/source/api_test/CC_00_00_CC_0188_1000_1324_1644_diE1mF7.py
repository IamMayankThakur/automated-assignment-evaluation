from flask import Flask, render_template, request, jsonify
import json
import requests
import sqlite3
import string
import datetime
app = Flask(__name__)

def validate(date_text):
    try:
        datetime.datetime.strptime(date_text, '%d-%m-%Y:%S-%M-%H')
        return True
    except ValueError:
        return False

def if_hex(s):
    try:
        int(s, 16)
        return True
    except ValueError:
        return False
        

#8
@app.route('/api/v1/db/write', methods=['POST'])
def write_db():
    conn = sqlite3.connect('Rideshare.db')
    c = conn.cursor()
    data = request.json['insert']
    column = request.json['column']
    table = request.json['table']
    what = request.json['what']
    if(what == "delete"):
        print("deleting")
        print(data)
        query = "DELETE FROM "+table+" where "+data
    else:
        print("inserting")
        query = "INSERT INTO "+table+" ("+column+") "+"VALUES ("+data+")"
    c.execute(query)
    conn.commit()
    conn.close()
    res = jsonify()
    return res, 201

#9
@app.route('/api/v1/db/read', methods=['POST'])
def read():
    conn = sqlite3.connect('Rideshare.db')
    c = conn.cursor()
    table = request.json['table']
    columns = request.json['columns']
    where = request.json['where']
    query = "SELECT "+columns+" FROM "+table+" WHERE "+where
    c.execute(query)
    rows = c.fetchall()
    conn.commit()
    conn.close()
    return json.dumps(rows)

@app.route('/api/v1/users', methods=['PUT'])
def add():
    try:
        name = request.json['username']
        password = request.json['password']
        insert = "'"+name+"','"+password+"'"
        names = requests.post('http://127.0.0.1:5000/api/v1/db/read', json={"table": "users","columns":"username","where":"username!='hdughuhuhfguihufdhuidhgfuhduhgiu'"})
        names = names.json()
        l = []
        for i in names:
            l.append(i[0])
        names = l
        if(len(password) == 40 and if_hex(password) and name not in names):
            requests.post('http://127.0.0.1:5000/api/v1/db/write', json={"insert": insert,"column":"username,password","table":"users","what":"insert"})
            res = jsonify()
            #res.statuscode = 201
            return res, 201
        else:
            res = jsonify()
            #res.statuscode = 400
            return res, 400
    except Exception as e:
        print(e)
        res = jsonify()
        # res.statuscode = 500
        return res, 500



@app.route('/api/v1/users/<string:name>', methods=['DELETE'])
def delete(name):
    try:
        name = str(name)
        names = requests.post('http://127.0.0.1:5000/api/v1/db/read', json={"table": "users","columns":"username","where":"username!='hdughuhuhfguihufdhuidhgfuhduhgiu'"})
        names = names.json()
        l = []
        for i in names:
            l.append(i[0])
        names = l
        # print(name)
        # print(names)
        if(name in names):
            # print("username='"+name+"'")
            requests.post('http://127.0.0.1:5000/api/v1/db/write', json={"insert": "username='"+name+"'","column":"","table":"users","what":"delete"})
            res = jsonify()
            # res.statuscode = 201
            return res, 200
        else:
            res = jsonify()
            # res.statuscode = 400
            return res, 400
    except Exception as e:
        print(e)
        res = jsonify()
        # res.statuscode = 500
        return res, 500

@app.route('/api/v1/rides', methods=['GET','POST'])
def upcoming_ride():
    try:
        if request.method == "GET":
            source = request.args.get('source')
            destination = request.args.get('destination')
            # print(source)
            # print(destination)
            areanames = requests.post('http://127.0.0.1:5000/api/v1/db/read', json={"table": "Areaname","columns":"Area_no","where":"Area_name!='hdughuhuhfguihufdhuidhgfuhduhgiu'"})
            l = []
            areanames = areanames.json()
            for i in areanames:
                l.append(i[0])
            areanames = l
            print(source)
            print(destination)

            if(not source or not destination or source == destination):
                return jsonify(), 400
            # print(areanames)
            # print(int(source) in areanames and int(destination) in areanames)
            if(int(source) in areanames and int(destination) in areanames):
                names = requests.post('http://127.0.0.1:5000/api/v1/db/read', json={"table": "ride","columns":"ride_id,created_by,timestamp","where":"source='"+source+"' and destination='"+destination+"'"})
                names = names.json()
                l = []
                for i in names:
                    dict = {
                        "rideId":i[0],
                        "username":i[1],
                        "timestamp":i[2]
                    }
                    l.append(dict)
                if(len(l) == 0):
                    return jsonify(l),204
                else:
                    return jsonify(l), 200
            else:
                res = jsonify()
                # res.statuscode = 400
                return res, 400
        if request.method == 'POST':
            created_by = request.json['created_by']
            timestamp = request.json['timestamp']
            source = request.json['source']
            destination = request.json['destination']
            name = created_by
            names = requests.post('http://127.0.0.1:5000/api/v1/db/read', json={"table": "users","columns":"username","where":"username!='hdughuhuhfguihufdhuidhgfuhduhgiu'"})
            names = names.json()
            areanames = requests.post('http://127.0.0.1:5000/api/v1/db/read', json={"table": "Areaname","columns":"Area_no","where":"Area_name!='hdughuhuhfguihufdhuidhgfuhduhgiu'"})
            areanames =areanames.json()
        # print(areanames)
            l = []
            for i in names:
                l.append(i[0])
            names = l
            l = []
        # print(names)
            for i in areanames:
                l.append(i[0])
            areanames = l
            if(not created_by or not timestamp or not source or not destination):
                return jsonify(), 400
            print(areanames)
            print(source in areanames)
        # print(source,destination)
            if(name in names and validate(timestamp) and int(source) in areanames and int(destination) in areanames):
                print("inside ")
                insert = "'"+created_by+"',"+"'"+timestamp+"',"+"'"+source+"','"+destination+"'"
                print(insert)
                r = requests.post('http://127.0.0.1:5000/api/v1/db/write', json={"insert": insert,"column":"created_by,timestamp,source,destination","table":"ride","what":"insert"})
                res = jsonify()
            # res.statuscode = 201
                return res, 201
            else:
                res = jsonify()
            # res.statuscode = 400
                return res, 400            
    except Exception as e:
        print(e)
        res = jsonify()
        # res.statuscode = 500
        return res, 405


@app.route('/api/v1/rides/<string:ride_id>', methods=['GET'])
def list_rides(ride_id):
    try:
        ride_id = str(ride_id)  
        ride_ids = requests.post('http://127.0.0.1:5000/api/v1/db/read', json={"table": "ride","columns":"ride_id","where":"source!='hasdfuhuhasujdhjkh'"})
        ride_ids = ride_ids.json()

        l = []
        for i in ride_ids:
            l.append(str(i[0]))
        ride_ids = l
        # print(ride_id)
        # print(ride_ids)
        if(not ride_id):
            return jsonify, 400
        if(ride_id in ride_ids):
            result = requests.post('http://127.0.0.1:5000/api/v1/db/read', json={"table": "ride","columns":"ride_id,created_by,timestamp,source,destination","where":"ride_id='"+ride_id+"'"})
            result1 = requests.post('http://127.0.0.1:5000/api/v1/db/read', json={"table": "join_ride","columns":"username","where":"ride_id='"+ride_id+"'"})
            result1 = result1.json()
            result = result.json()
            l = []
            for i in result1:
                l.append(i[0])
            result1 = l
            dict = {
                "rideId":result[0][0],
                "Created_by":result[0][1],
                "users":result1,
                "Timestamp":result[0][2],
                "source":result[0][3],
                "destination":result[0][4]
            }
            if(len(dict) == 0):
                return jsonify(dict), 204
            else:
                return jsonify(dict), 200
        else:
            res = jsonify()
            # res.statuscode = 400
            return res, 400
    except Exception as e:
        print(e)
        res = jsonify()
        # res.statuscode = 500
        return res, 500

@app.route('/api/v1/rides/<string:ride_id>', methods=['POST'])
def join_rides(ride_id):
    try:
        ride_id = str(ride_id)
        ride_ids = requests.post('http://127.0.0.1:5000/api/v1/db/read', json={"table": "ride","columns":"ride_id","where":"ride_id!='2341356'"})
        ride_ids = ride_ids.json()
        names = requests.post('http://127.0.0.1:5000/api/v1/db/read', json={"table":"users","columns":"username","where":"username!='sdjhfjsdhfjkhfjksdhfjksfhkjdshfjksdh'"})
        names = names.json()
        l = []
        for i in ride_ids:
            l.append(i[0])
        ride_ids = l
        l = []
        for i in names:
            l.append(i[0])
        names = l
        username = request.json['username']
        username = str(username)
        users_already_in_ride = requests.post('http://127.0.0.1:5000/api/v1/db/read', json={"table":"join_ride","columns":"username","where":"ride_id='"+ride_id+"'"})
        users_already_in_ride = users_already_in_ride.json()
        l = []
        for i in users_already_in_ride:
            l.append(i[0])
        users_already_in_ride = l
        created_by = requests.post('http://127.0.0.1:5000/api/v1/db/read', json={"table": "ride","columns":"created_by","where":"ride_id='"+ride_id+"'"})
        created_by = created_by.json()
        created_by = created_by[0][0]
        if(not ride_id):
            return jsonify(), 204
        print(created_by)
        print(username)
        if((username in users_already_in_ride) or (username == created_by)):
            return jsonify(),400
        if((username in names) and (int(ride_id) in ride_ids)):
            insert = "'"+ride_id+"','"+username+"'"
            requests.post('http://127.0.0.1:5000/api/v1/db/write', json={"insert": insert,"column":"ride_id,username","table":"join_ride","what":"insert"})
            res = jsonify()
            # res.statuscode = 201
            return res, 200
        else:
            res = jsonify()
            # res.statuscode = 400
            return res, 204
    except Exception as e:
        print(e)
        res = jsonify()
        # res.statuscode = 500
        return res, 500


@app.route('/api/v1/rides/<string:ride_id>', methods=['DELETE'])
def delete_ride(ride_id):
    try:
        ride_id = str(ride_id)
        ride_ids = requests.post('http://127.0.0.1:5000/api/v1/db/read', json={"table": "ride","columns":"ride_id","where":"ride_id!='2341356'"})
        ride_ids = ride_ids.json()
        l = []
        for i in ride_ids:
            l.append(i[0])
        ride_ids = l
        print(ride_ids)
        print(ride_id)
        if(int(ride_id) in ride_ids):
            requests.post('http://127.0.0.1:5000/api/v1/db/write', json={"insert": "ride_id='"+ride_id+"'","column":"username,password","table":"ride","what":"delete"})
            res = jsonify()
            # res.statuscode = 201
            return res, 200
        else:
            res = jsonify()
            # res.statuscode = 400
            return res, 405
    except Exception as e:
        print(e)
        res = jsonify()
        # res.statuscode = 500
        return res, 500

if __name__ == '__main__':
    app.run()
    # app.run(host="172.31.84.76")