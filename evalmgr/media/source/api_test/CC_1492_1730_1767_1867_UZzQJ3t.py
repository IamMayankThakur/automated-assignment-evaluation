from flask import Flask, request, abort, render_template,jsonify, Response
import sqlite3
import requests
import re
import datetime
import json
pword_pat = re.compile('^[a-fA-F0-9]{40}$')

app = Flask(__name__)


#1st api
@app.route('/api/v1/users', methods=['PUT'])
def add_user():
    print('gfdgdf')
    data = request.get_json()
    uname = data['username']
    pword = data['password']
    

    query = {"table":"Users","columns":["uname"] ,"where":"1"}

    uname_list = requests.post(url='http://127.0.0.1:5000/api/v1/db/read',json=query)
    valid=1
    
    print("9th api called . . .")
    
    uname_list=uname_list.json()

    print(uname_list)

    

    for x in uname_list["uname"]:
        if(uname==x):
            print("duplicate")
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
            sql_add = {"insert":[uname,pword],"table":"Users","columns":["uname","pwd"],"isDelete":"False"}
            requests.post(url='http://127.0.0.1:5000/api/v1/db/write',json=sql_add)
            return Response(status=201)
    else:
        #invalid uname
        return Response(status=400)



#2nd api
@app.route('/api/v1/users/<username>',methods=['DELETE'])
def del_user(username):
    query = {"table":"Users","columns":["uname"] ,"where":"1"}

    uname_list = requests.post(url='http://127.0.0.1:5000/api/v1/db/read',json=query)
    present=0
    
    print("9th api called . . .")
    
    uname_list=uname_list.json()

    print(uname_list)
    print(username)
    

    for x in uname_list["uname"]:
        if(username == x):
            print("duplicate")
            present=1
            break
    if(present):
        print("present")
        sql_del = {"insert":[username],"table":"Users","columns":["uname"],"isDelete":"True"}
        requests.post(url='http://127.0.0.1:5000/api/v1/db/write',json=sql_del)
        return Response(status=200)

    else:
        #user not present
        return Response(status=400)


#3rd api
@app.route('/api/v1/rides',methods=['POST'])
def create_ride():
    print("Creating RIde . . .")
    data = request.get_json()
    created_by = data['created_by']
    timestamp = data['timestamp']
    source = data['source']
    dest = data['destination']

    query = {"table":"Users","columns":["uname"],"where":"1"}
    try:
        uname_list = requests.post(url='http://127.0.0.1:5000/api/v1/db/read',json=query)
    except:
        return Response(status=400)
    present=0
    uname_list=uname_list.json()

    for x in uname_list["uname"]:
        if(created_by==x):
            present=1
            break
    if(present):
        send_data = {"insert":[created_by,timestamp,source,dest],"table":"rides","columns":["uname","timestamp","source","destination"],"isDelete":"False"}
        try:
            requests.post(url='http://127.0.0.1:5000/api/v1/db/write', json=send_data)
            return Response(status=201)
        except:
            return Response(status=400)

    else:
        #user who created ride not present
        return Response(status=400)


#4th api
@app.route('/api/v1/rides',methods=['GET'])
def list_rides():
    source = request.args.get('source')
    destination = request.args.get('destination')
    src = 0
    dest = 0
    query_for_area = {"table":"Areas","columns":["area_id"], "where":"1"}
    area_list = requests.post(url='http://127.0.0.1:5000/api/v1/db/read',json = query_for_area)

    area_list = area_list.json()['area_id']

    #print(type(source))

    for x in area_list:
        if(x==int(source)):
            src=1
        elif(x==int(destination)):
            dest = 1
    print(src , dest)
    if(src and dest):
        condition = "source="+str(source)+" and destination="+str(destination)
        query = {"table":"rides","columns":["rideId","uname","timestamp"],"where":condition} 
        ride_data = requests.post(url='http://127.0.0.1:5000/api/v1/db/read', json=query)

        print(ride_data)

        ride_data = ride_data.json()
        response = []
        
        print(ride_data)

        for x in range(ride_data['count']):
            timestamp1 = ride_data['timestamp'][x]
            timestamp2 = datetime.datetime.now().strftime("%d-%m-%Y:%S-%M-%H")

            t1 = datetime.datetime.strptime(str(timestamp1), "%d-%m-%Y:%S-%M-%H")
            t2 = datetime.datetime.strptime(str(timestamp2), "%d-%m-%Y:%S-%M-%H")

            print(t1,t2)
            
            if(t1 > t2):
                #list it
                ds = {}
                ds["rideId"] = ride_data['rideId'][x]
                ds["username"] = ride_data['uname'][x]
                ds["timestamp"] = ride_data['timestamp'][x]
                response.append(json.dumps(ds))
            return jsonify(response)     
    else:
        print('invlaid src and destination')
        abort(400)


#5th api
@app.route('/api/v1/rides/<rideId>',methods=['GET'])
def ride_details(rideId):
    print("rideId:",rideId)

    query = {"table":"Rides","columns":["rideId"],"where":"1"}
    ride_ids = requests.post(url='http://127.0.0.1:5000/api/v1/db/read', json=query)
    ride_ids = ride_ids.json()['rideId']
    print("ride_ids:",ride_ids)

    valid = 0
    for x in ride_ids:
        if(x == int(rideId)):
            valid=1
            break
    print(valid)
    if not valid:
        #invalid rided id
        abort(400)   #############################################################################
    else:
        wherecond = "rideId="+str(rideId)
        ride_query = {"table":"rides","columns":["uname","timestamp","source","destination"],"where":wherecond} 
        about_ride = requests.post(url='http://127.0.0.1:5000/api/v1/db/read', json=ride_query)

        about_ride = about_ride.json()
        print(about_ride)

        created_user = about_ride['uname']
        created_timestamp = about_ride['timestamp']
        source_id = about_ride['source']
        dest_id = about_ride['destination']

        users_query = {"table":"joinedRides","columns":["uname"],"where":wherecond} 

        print(users_query)

        pool_users = requests.post(url='http://127.0.0.1:5000/api/v1/db/read', json=users_query)
        pool_users = pool_users.json()['uname']
        response = {"rideId":rideId, "Created_by":created_user,"users":pool_users , "Timestamp":created_timestamp, "source":source_id, "destination":dest_id}
        return jsonify(response)


#6th api
@app.route('/api/v1/rides/<rideId>',methods=['POST'])
def pool_ride(rideId):
    uname = request.get_json()['username']
    query1 = {"table":"Users","columns":["uname"] ,"where":"1"}

    uname_list = requests.post(url='http://127.0.0.1:5000/api/v1/db/read',json=query1)
    present=0
    
    uname_list=uname_list.json()    

    for x in uname_list["uname"]:
        if(uname==x):
            print("duplicate")
            present=1
            break

    query2 = {"table":"Rides","columns":["rideId"],"where":"1"}
    ride_ids = requests.post(url='http://127.0.0.1:5000/api/v1/db/read', json=query2)
    ride_ids = ride_ids.json()['rideId']
    print("ride_ids:",ride_ids)

    valid = 0
    for x in ride_ids:
        if(x == int(rideId)):
            valid=1
            break

    if((not valid) or (not present)):
        #invalid rided id or username
        abort(400)

    else:
        insert_query = {"insert":[rideId,uname],"table":"joinedRides","columns":["rideID","uname"],"isDelete":"False"}
        added = requests.post(url='http://127.0.0.1:5000/api/v1/db/write', json=insert_query)
        added = added.json()
        print(added)
        if(added['status'] == 200):
            return Response(status=200)   
        else:
            abort(400)


#7th api
@app.route('/api/v1/rides/<rideId>', methods=['DELETE'])
def delete_ride(rideId):
    query = {"table":"rides","columns":["rideID"],"where":"1"}
    ride_ids = requests.post('http://127.0.0.1:5000/api/v1/db/read',json=query)
    valid = 0
    ride_ids=ride_ids.json()
    
    for x in ride_ids["rideID"]:
        # print(type(x),end=" ")
        # print(type(rideId))
        if(x == int(rideId)):
            valid=1
            break
    
    
    if valid:
        #invalid rided id 
        # delete_sql = "DELETE FROM rides WHERE rideId="+str(rideId)
        # deleted = cursor.execute(delete_sql)
        # if(deleted):
        #     return 200
        # else:
        #     abort(400) '
        print("deleting . . ")
        send_data = {"insert":[rideId],"table":"rides","columns":["rideID"],"isDelete":"True"}
        try:
            requests.post(url='http://127.0.0.1:5000/api/v1/db/write', json=send_data)
            return Response(status=200)
        except:
            return Response(status=405)

    else:
        print("No Ride Exists")
        return Response(status=400)
        


#8th api
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
    
    isDelete=data['isDelete']
    
    
    sqlQuery=""
    print(isDelete)
    tableName=data['table']
    insertData=data['insert']
    columns=data['columns']
    
    if isDelete=="True":
        print("ELSE")
        sqlQuery='DELETE FROM '+tableName+ ' WHERE '+columns[0]+'="'+insertData[0]+'"'
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
        print("sql write error:",e)
        cxn.close()
        result['status']=400
        print(e)
        return result
    cxn.close()
    print(result)
    return jsonify(result)


#9th api
@app.route('/api/v1/db/read',methods=["POST"])
def readDB():
    print("reading DB. . .")
    result={}

    try:
        cxn=sqlite3.connect('RideShare.db')
        cursor=cxn.cursor()
        cursor.execute('PRAGMA foreign_keys = ON')
        print("Connected")
        
    except Exception as e:
        cxn.close()
        result['status']=400
        print(result)
        return jsonify(result)


    cxn.commit()
    data = request.get_json()
    print(data)

    sqlQuery=""
    tableName=data['table']
    whereClause=data['where']
    columns=data['columns']
    
    
    print("HI")
    sqlQuery='SELECT '
    for i in columns:
        sqlQuery+=i+','
    sqlQuery=sqlQuery[0:-1]
    sqlQuery+=' FROM '+tableName + ' WHERE '+whereClause
    
    print(sqlQuery)
    
    try:
        print("abc2")
        cursor.execute(sqlQuery)
        print("abc23")
        rows = cursor.fetchall()
        print("abc24")
 

        result["count"]=len(rows)
        result["status"]=200
        k=-1
        for i in columns:
            result[i]=[]
            k+=1
            for data in rows:
                result[i].append(data[k])
        
        cxn.commit()
    except Exception as e:
        print("abc")
        cxn.close()
        print(e)
        result['status']=400
        print(result)
        return result
    cxn.close()
    print(result)
    return jsonify(result)


if __name__ == '__main__':
    app.debug=True
    app.run()