import mysql.connector
import requests
from flask import Flask, render_template, jsonify, request, abort
import datetime 
import string
import pandas

app=Flask(__name__)

mydb = mysql.connector.connect(
      host="localhost",
      user="cloud",
      passwd="password",
      database="cloud_ass3",
    )

mycursor = mydb.cursor()


@app.route('/api/v1/db/write',methods=["POST"])
def write_db():
    to_ins = request.get_json()['insert'] # [ 'shashank', '6ae999552a0d2dca14d62e2bc8b764d377b1dd6c' ] 
    to_col = request.get_json()['column'] #  [ 'username' , 'password' ]
    to_table = request.get_json()['table'] # users

    sql_query = "INSERT INTO "+to_table+" "+str(to_col).replace('[','(').replace(']',')').replace("'","")+" values "+str(to_ins).replace('[','(').replace(']',');')

    mycursor.execute(sql_query)
    mydb.commit()
    
    return '',201


@app.route('/api/v1/db/read',methods=["POST"])
def read_db():
    
    to_col = request.get_json()['column']
    to_table = request.get_json()['table']
    to_conds = request.get_json()['where']
    
    sql_query = "SELECT " + str(to_col).replace('[',"").replace("]","").replace("'","") + " "
    sql_query += "FROM " + str(to_table) + " "
    sql_query += "WHERE " + str(to_conds).replace('[',"").replace("]","").replace("\"","").replace(","," and ") + ";"

    res = []
    mycursor.execute(sql_query)
    for i in mycursor.fetchall():
        res.append(i)

    if(not res):
        abort(400)
    return str(res),200
    

@app.route('/api/v1/users',methods=["PUT"])
def add_user():
    username = request.get_json()['username']
    password = request.get_json()['password']
    print(username)
    print(password)
    if(len(password)!=40):
        abort(400)
    else:
        for i in password:
            if(i not in string.hexdigits):
                abort(400)


    r = requests.post('http://127.0.0.1:5000/api/v1/db/read', json={"column":["username"],"table":"users","where":["username='"+str(username)+"'"]})

    if(r.status_code==400):
        requests.post('http://127.0.0.1:5000/api/v1/db/write', json={"insert":[str(username),str(password)],"column":["username","password"],"table":"users"})
        return 'Successfully created user', 201
    
    else:
        abort(400)


@app.route("/api/v1/users/<username>",methods=["DELETE"])
def remove_user(username):
    
    r = requests.post('http://127.0.0.1:5000/api/v1/db/read', json={"column":["username"],"table":"users","where":["username='"+str(username)+"'"]})
    
    if(r.status_code==400):
        abort(400)
    else:
        sql_query = "DELETE from users WHERE username='"+str(username)+"';"
        mycursor.execute(sql_query)
        mydb.commit()
        return '',204



@app.route("/api/v1/rides",methods=['POST'])
def add_ride():
    created_by = request.get_json()['created_by']
    ts = request.get_json()['timestamp']
    src = request.get_json()['source']
    dest = request.get_json()['destination']

    if(int(src) not in range(1,199) or int(dest) not in range(1,199)):
        abort(400)
    
    dateTimeObj= datetime.datetime.strptime(ts, '%d-%m-%Y:%S-%M-%H')
    time_stamp = dateTimeObj.strftime("%Y-%m-%d %H:%M:%S")

    r = requests.post('http://127.0.0.1:5000/api/v1/db/read', json={"column":["username"],"table":"users","where":["username='"+str(created_by)+"'"]})
    if(r.status_code==400):
        abort(400)

    else:
        r = requests.post('http://127.0.0.1:5000/api/v1/db/write', json={"insert":[str(created_by),str(created_by),str(src),str(dest),str(time_stamp)],"column":["created_by","users","src","dest","ts"],"table":"rides"})

    return 'Successfully created new ride',201



@app.route("/api/v1/rides")
def list_rides():
    src = request.args.get('source', default = 1, type = int)
    dest = request.args.get('destination', default = 1, type = int)

    if(int(src) not in range(1,199) or int(dest) not in range(1,199)):
        abort(400)

    cur_ts=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    r = requests.post('http://127.0.0.1:5000/api/v1/db/read', json={"column":["rideid","created_by","users","ts"],"table":"rides","where":["src='"+str(src)+"'","dest='"+str(dest)+"'","ts>'"+str(cur_ts)+"'"]})

    if(r.status_code==400):
        return '',204
    
    else:
        x= eval(r.text)
        res=[]
        for i in x:
            if(i[1]==i[2]):
                d={}
                d["rideId"]=i[0]
                d["username"]=i[1]
                d["timestamp"]=i[3].strftime("%d-%m-%Y:%S-%M-%H")

                res.append(d)

        
        return jsonify(res),200


@app.route("/api/v1/rides/<rideId>")
def list_details(rideId):

    r = requests.post('http://127.0.0.1:5000/api/v1/db/read', json={"column":["rideid","created_by","users","ts","src","dest"],"table":"rides","where":["rideid='"+str(rideId)+"'"]})
    flag=0
    if(r.status_code==400):
        abort(400)
    else:
        x= eval(r.text)
        d={}
        
        d["rideId"]=x[0][0]
        d["created_by"]=x[0][1]
        d["users"]=[]
        d["timestamp"]=x[0][3].strftime("%d-%m-%Y:%S-%M-%H")
        d["source"]=x[0][4]
        d["destination"]=x[0][5]
        
        data= pandas.read_csv('AreaNameEnum.csv')

#        d["source"]=data.loc[data['Area No']==int(x[0][4])][['Area Name']].values[0][0]
 #       d["destination"]=data.loc[data['Area No']==int(x[0][5])][['Area Name']].values[0][0]

        for i in x:
            if(i[2]!=d["created_by"]):
                d["users"].append(i[2])
                

        
        return jsonify(d),200


@app.route("/api/v1/rides/<rideId>", methods=["POST"])
def join_ride(rideId):

    username = request.get_json()['username']

    r = requests.post('http://127.0.0.1:5000/api/v1/db/read', json={"column":["rideid","created_by","ts","src","dest"],"table":"rides","where":["rideid='"+str(rideId)+"'"]})
    r1= requests.post('http://127.0.0.1:5000/api/v1/db/read', json={"column":["username"],"table":"users","where":["username='"+str(username)+"'"]})
    r2= requests.post('http://127.0.0.1:5000/api/v1/db/read', json={"column":["rideid","created_by"],"table":"rides","where":["rideid='"+str(rideId)+"'", "created_by='"+str(username)+"'"]})
    

    if(r.status_code==400 or r1.status_code==400 or r2.status_code!=400):
        abort(400)
    else:
        x= eval(r.text)
        dateTimeObj = x[0][2]
     
        time_stamp = dateTimeObj.strftime("%Y-%m-%d %H:%M:%S")
        created_by = x[0][1]
        src=x[0][3]
        dest=x[0][4]
        r = requests.post('http://127.0.0.1:5000/api/v1/db/write', json={"insert":[str(rideId),str(created_by),str(username),str(src),str(dest),str(time_stamp)],"column":["rideid","created_by","users","src","dest","ts"],"table":"rides"})
        return '',200


@app.route("/api/v1/rides/<rideId>", methods=["DELETE"])
def delete_ride(rideId):

    r = requests.post('http://127.0.0.1:5000/api/v1/db/read', json={"column":["rideid"],"table":"rides","where":["rideid='"+str(rideId)+"'"]})
    
    if(r.status_code==400):
        abort(400)
    else:
        sql_query = "DELETE from rides WHERE rideid='"+str(rideId)+"';"
        mycursor.execute(sql_query)
        mydb.commit()
        return '',200


if __name__ == '__main__':	
	app.run()


