from flask import Flask, request, abort, render_template,jsonify, Response
import sqlite3
import requests
import re
pword_pat = re.compile('^[a-fA-F0-9]{40}$')

app = Flask(__name__)

@app.route('/api/v1/users', methods=['PUT'])
def add_user():
    print('gfdgdf')
    data = request.get_json()
    uname = data['username']
    pword = data['password']

    SQL_query = {"table":"Users","columns":["uname"] ,"where":"1"}
    username_list = requests.post(url='http://127.0.0.1:5000/api/v1/db/read',json=SQL_query)
    valid=1
    username_list=username_list.json()
    print("9th api called . . .")
    print(username_list)

    for x in username_list:
        if(uname==x):
            valid=0
            break

    if(valid):
        #check password
        print("Password is :"+pword)
        match = re.search(pword_pat,pword)
        if not match:
            #invalid password
            return Response(status=400)
        else:
            #add
            sql_add = {"insert":[uname,pword],"table":"Users","columns":["uname","pwd"],"isRemove":"False"}
            requests.post(url='http://127.0.0.1:5000/api/v1/db/write',json=sql_add)
            return Response(status=201)
    else:
        #invalid uname
        return Response(status=400)


@app.route('/api/v1/users/<username>',methods=['Remove'])
def del_user(username):

    SQL_query = {"table":"Users","columns":["uname"],"where":"1"}
    username_list = requests.post(url='http://127.0.0.1:5000/api/v1/db/read',json=SQL_query)
    is_present=0
    username_list=username_list.json()

    for x in username_list["uname"]:
        if(username==x):
            is_present=1
            break

    if(is_present):
        print("is_present")
        sql_del = {"insert":[username],"table":"Users","columns":["uname"],"isRemove":"True"}
        requests.post(url='http://127.0.0.1:5000/api/v1/db/write',json=sql_del)
        return Response(status=200)

    else:
        #user not is_present
        return Response(status=400)


@app.route('/api/v1/rides',methods=['POST'])
def create_ride():
    data = request.get_json()
    created_by = data['created_by']
    timestamp = data['timestamp']
    source = data['source']
    destination = data['destination']

    SQL_query = {"table":"Users","columns":["uname"],"where":"*"}
    username_list = requests.post(url='/api/v1/db/read',json=SQL_query)
    is_present=0

    for x in username_list:
        if(created_by==x):
            is_present=1
            break
    if(is_present):
        send_data = {"insert":[created_by,timestamp,source,destination],"table":"rides"}
        requests.post(url='/api/v1/db/read', json=send_data)

    else:
        #user who created ride not is_present
        abort(400)

@app.route('/api/v1/rides?source={source}&destination={destination}',methods=['GET'])
def list_rides(source,destination):
    src = 0
    dest = 0
    query_for_area = {"table":"areas","columns":"area_id"}
    area_list = requests.post(url='/api/v1/db/read',json = query_for_area)
    for x in area_list:
        if(x==src):
            src=1
        elif(x==destination):
            dest = 1
    if(src and dest):
        SQL_query = {"table":"rides","columns":["rideid","created_by","timestamp"],"where":"source=source,destination=destination"}
        ride_data = requests.post(url='/api/v1/db/read', json=SQL_query)
        for ride in ride_data:
            if(ride['timestamp'] > current_timestamp):
                #list it
                print("")
    else:
        #invlaid src and destination
        abort(400)

@app.route('/api/v1/rides/{rideId}',methods=['GET'])
def ride_details(rideId):
    SQL_query = {"table":"rides","columns":["rideId"],"where":"*"}
    ride_ids = requests.post('/api/v1/db/read',json=SQL_query)
    valid = 0
    for x in ride_ids:
        if(x == rideId):
            valid=1
            break
    if not valid:
        #invalid rided id
        abort(400)
    else:
        ride_query = {"table":"rides","columns":["created_by","timestamp","source","destination"],"where":"rideId=rideId"}
        about_ride = requests.post(url='url for 9th', json=ride_query)
        created_user = about_ride['created_by']
        created_timestamp = about_ride['timestamp']
        source_id = about_ride['source']
        dest_id = about_ride['destination']
        users_query = {"table":"pool","columns":["uname"],"where":"rideId=rideId"}
        pool_users = requests.post(url='/api/v1/db/read', json=users_query)
        response = {"rideId":rideId, "Created_by":created_user,"users":pool_users , "Timestamp":created_timestamp, "source":source_id, "destination":dest_id}
        return jsonify(response)

@app.route('/api/v1/rides/{rideId}',methods=['POST'])
def pool_ride(rideId):
    uname = request.get_json()['username']
    SQL_query1 = {"table":"Users","columns":["uname"],"where":"*"}
    username_list = requests.post(url='/api/v1/db/read',json=SQL_query1)
    is_present=0

    for x in username_list:
        if(uname==x):
            is_present=1
            break
    SQL_query2 = {"table":"rides","columns":["rideId"],"where":"*"}
    ride_ids = requests.post('/api/v1/db/read',json=SQL_query2)
    valid = 0
    for x in ride_ids:
        if(x == rideId):
            valid=1
            break
    if((not valid) or (not is_present)):
        #invalid rided id or username
        abort(400)
    else:
        insert_SQL_query = {"insert":[rideId,uname],"table":"pool"}
        added = requests.post(url='/api/v1/db/write', json=insert_SQL_query)
        if(added):
            return "200 OK"
        else:
            abort(400)
@app.route('/api/v1/rides/{rideId}', methods=['Remove'])
def Remove_ride(rideId):
    SQL_query = {"table":"rides","columns":["rideId"],"where":"*"}
    ride_ids = requests.post('/api/v1/db/read',json=SQL_query)
    valid = 0
    for x in ride_ids:
        if(x == rideId):
            valid=1
            break

    if not valid:
        #invalid rided id
        abort(400)

    else:
        Remove_sql = "Remove FROM rides WHERE rideId="+str(rideId)
        Removed = cursor.execute(Remove_sql)
        if(Removed):
            return "200 OK"
        else:
            abort(400)

@app.route('/api/v1/db/write',methods=["POST"])
def addToDB():
    result={}
    result['status']=200
    try:
        cxn=sqlite3.connect('RideShare.db')
        cursor=cxn.cursor()
        cursor.execute('PRAGMA foreign_keys = ON')
    except Exception as e:
        cxn.close()
        result['status']=400
        print(e)
        return result
    cxn.commit()
    data=request.get_json()
    print(data)
    isRemove=data['isRemove']
    sqlQuery=""
    print(isRemove)
    tableName=data['table']
    insertData=data['insert']
    columns=data['columns']
    if isRemove=="True":
        print("ELSE")
        sqlQuery='Remove FROM '+tableName+ ' WHERE '+columns[0]+'="'+insertData[0]+'"'
        print(sqlQuery)
    else:
        print("HI")
        sqlQuery='INSERT INTO '+tableName + ' ('
        for i in columns:
            sqlQuery=sqlQuery+i+','
        sqlQuery=sqlQuery[0:-1]
        sqlQuery=sqlQuery+') VALUES('

        for i in insertData:
            sqlQuery+='"'+i+'"'+','
        sqlQuery=sqlQuery[0:-1]
        sqlQuery+=')'
        print("\n\n"+sqlQuery)
    try:
        cursor.execute(sqlQuery)
        cxn.commit()
    except Exception as e:
        cxn.close()
        result['status']=400
        print(e)
        return result
    cxn.close()
    return result

@app.route('/api/v1/db/read',methods=["POST"])
def readDB():
    print("reading DB. . .")
    result={}
    try:
        cxn=sqlite3.connect('RideShare.db')
        cursor=cxn.cursor()
        cursor.execute('PRAGMA foreign_keys = ON')

    except Exception as e:
        cxn.close()
        result['status']=400
        print(e)
        return result

    cxn.commit()
    data=request.get_json()
    #print(data)

    sqlQuery=""
    tableName=data['table']
    whereClause=data['where']
    columns=data['columns']
    #print("HI")
    sqlQuery='SELECT '
    for i in columns:
        sqlQuery+=i+','
    sqlQuery=sqlQuery[0:-1]
    sqlQuery+=' FROM '+tableName + ' WHERE '+whereClause
    print(sqlQuery)
    try:
        cursor.execute(sqlQuery)
        rows = cursor.fetchall()

        #for row in rows:
            #print(list(row))

        result["count"]=len(rows)
        result["status"]=200
        k=-1
        for i in columns:
            result[i]=[]
            k+=1
            for data in rows:
                result[i].append(data[k])

        #print(result)
        cxn.commit()
    except Exception as e:
        cxn.close()
        print(e)
        result['status']=400
        return result
    cxn.close()
    return result
