'''
insert into rides ('user', 'src', 'dest', 'ride_id', 'timestamp', 'created_by') values('user5', 'src2', 'dest3', '1002', '23-01-2020:49-48-07', 'user3');
'''
import random
import sqlite3  
import requests
import json
import ast
from datetime import datetime
from flask import Flask, render_template,\
jsonify,request,abort, Response
app=Flask(__name__)
@app.route('/hello/<name>')
def hello_world(name):	
	return "Hello, %s !" % name
'''
format reqd:

{
"username": "userName",
"password": "3d725109c7e7c0bfb9d709836735b56d943d263f"
}
'''
import string
def is_hex(s):
     hex_digits = set(string.hexdigits)
     return all(c in hex_digits for c in s)
#1 Adding  new user to db-DONE.
@app.route('/api/v1/users', methods=["PUT"]) #ENCODING- 201, 400, 405
def add_new_user():
    if request.method != "PUT":  
        return('', 405)
    username = request.get_json()["username"]  
    password = request.get_json()["password"]
    password=password.upper()
    if(len(str(password))!=40 or is_hex(str(password))==False):
        return('Invalid Password', 400)
    user = {}
    password=password.lower()
    user["table"] = "users"
    user["columns"] = ["name","pwd"]
    user["where"] = "name='"+username+"'"
    r = json.dumps(user)
    loaded_r = json.loads(r)
    headers = {'content-type': 'application/json'}
    req_resp=requests.post("http://127.0.0.1:8000/api/v1/db/read",data = r, headers = headers)
    temp=str(req_resp.text)
    temp=json.loads(temp)
    if(bool(temp)==True): #EMPTY DICTIONARY
        return('User already exists', 400)
    else:
        add_user = {}
        add_user_j = {}
        add_user["insert"] = [str(username),str(password)]
        add_user["column"] = ["name","pwd"]
        add_user["table"] = "users"
        r = json.dumps(add_user)
        loaded_r = json.loads(r)
        headers = {'content-type': 'application/json'}
        req_resp=requests.post("http://127.0.0.1:8000/api/v1/db/write",data = r, headers = headers)
        return('', 201) #successful create


#2- Removing a particular user- DONE.
@app.route("/api/v1/users/<name>",methods = ["DELETE"])  
def removeuser(name):
    if request.method != "DELETE":  
        return('', 405)
    user = {}
    user["table"] = "users"
    user["columns"] = ["name","pwd"]
    user["where"] = "name='"+name+"'"
    r = json.dumps(user)
    loaded_r = json.loads(r)
    headers = {'content-type': 'application/json'}
    req_resp=requests.post("http://127.0.0.1:8000/api/v1/db/read",data = r, headers = headers)
    temp=str(req_resp.text)
    temp=json.loads(temp)
    if(bool(temp)==False): #EMPTY DICTIONARY
        return('Username Not Found', 400)
    else:
        con = sqlite3.connect("rideshare.db") 
        cur = con.cursor()   
        command1="delete from rides where user ="+"'"+str(name)+"'"  
        command2="delete from users where name ="+"'"+str(name)+"'"  
        cur.execute(command1) 
        cur.execute(command2) 
        con.commit()
        con.close()
        return('', 200)

     
'''
 {
"created_by" : "username",
"timestamp" : "DD-MM-YYYY:SS-MM-HH",
"source" : "source",
"destination" : "destination"
}''' 

#3 creating a new ride-201, 400, 405-DONE.
@app.route("/api/v1/rides", methods=["POST"])
def create_new_ride():
    if request.method != "POST":  
        return('', 405)
    user = request.get_json()["created_by"]  
    time_stamp = request.get_json()["timestamp"]
    time_stamp_str = str(time_stamp) 
    src = request.get_json()["source"]  
    dest = request.get_json()["destination"]
    check=str(57822)
    temp=True
    while(temp):
        #check=str(random.randint(1,100000))
        upcoming_rides = {}
        upcoming_rides["table"] = "rides"
        upcoming_rides["columns"] = ["ride_id","user","timestamp","src","dest", "created_by"]
        upcoming_rides["where"] = "ride_id='"+check+"'"
        r = json.dumps(upcoming_rides)
        loaded_r = json.loads(r)
        headers = {'content-type': 'application/json'}
        req_resp=requests.post("http://127.0.0.1:8000/api/v1/db/read",data = r, headers = headers)
        temp=str(req_resp.text)
        temp=json.loads(temp)
        if(bool(temp)==True):
            print(check,"exists")
        check=str(random.randint(1,100000))
    #########
    src = request.get_json()["source"]  
    dest = request.get_json()["destination"]
    ride_id=check
    check={}
    if(int(src)<1 or int(dest)<1 or int(src)>198 or int(dest)>198):
        return('Invalid Source/Destination', 400)
    check["table"] = "users"
    check["columns"] = ["name","pwd"]
    check["where"] = "name='"+user+"'"
    r = json.dumps(check)
    loaded_r = json.loads(r)
    headers = {'content-type': 'application/json'}
    req_resp=requests.post("http://127.0.0.1:8000/api/v1/db/read",data = r, headers = headers)
    temp=str(req_resp.text)
    temp=json.loads(temp)
    if(bool(temp)==False): #EMPTY DICTIONARY
        return('User does not exist', 400)
    else:
        add_user={}
        add_user["insert"]=[str(user), str(src), str(dest), ride_id, str(time_stamp), str(user)]
        add_user["column"]=["user", "src", "dest", "ride_id", "timestamp", "created_by"]
        add_user["table"]="rides"
        r = json.dumps(add_user)
        loaded_r = json.loads(r)
        headers = {'content-type': 'application/json'}
        req_resp=requests.post("http://127.0.0.1:8000/api/v1/db/write",data = r, headers = headers)
        return('', 201)

#STATUS CODES-FINISH 400 and check API route-IMPORT CSV
#@app.route('/api/v1/rides/<source>/<destination>',methods=["GET"]) #200, 204, 400, 405

@app.route('/api/v1/rides')
def list_upcoming_rides():
    source = request.args.get('source', default="1",type=str)
    print(type(source))
    destination = request.args.get('destination', default="1", type=str)
    if request.method != "GET":  
        return('', 405)
    if(int(source)<1 or int(destination)<1 or int(source)>198 or int(destination)>198):
        return('Invalid Source/Destination', 400)
    timestamp_now = datetime.now()
    datetimeobject = datetime.strptime(str(timestamp_now)[0:18],'%Y-%m-%d %H:%M:%S')
    timestamp_new = datetimeobject.strftime('%d-%m-%Y:%S-%M-%H')
    timestamp_final = datetime.strptime(timestamp_new,'%d-%m-%Y:%S-%M-%H')
    upcoming_rides = {}
    upcoming_rides["table"] = "rides"
    upcoming_rides["columns"] = ["ride_id","user","timestamp","src","dest", "created_by"]
    upcoming_rides["where"] = "src ="+ "'"+ source +"'"+" and "+"dest="+ "'"+ destination + "'" 
    r = json.dumps(upcoming_rides)
    loaded_r = json.loads(r)
    headers = {'content-type': 'application/json'}
    req_resp=requests.post("http://127.0.0.1:8000/api/v1/db/read",data = r, headers = headers)
    temp=str(req_resp.text)
    temp=json.loads(temp)
    final = []
    border=[]
    for i in temp:
        notfinal={}
        temp_date = temp[i]["timestamp"][0:19]
        temp_date_final = datetime.strptime(temp_date,'%d-%m-%Y:%S-%M-%H')
        if temp_date_final>timestamp_final:
            if(temp[i]["rideId"] not in border):
                notfinal["rideId"]=temp[i]["rideId"]
                notfinal["username"]=temp[i]["created_by"]
                notfinal["timestamp"]=temp[i]["timestamp"]
                final.append(notfinal)
                border.append(temp[i]["rideId"])
    if(bool(temp)==False): #EMPTY DICTIONARY
        return('No Upcoming Rides', 204)
    return(json.dumps(final),200)



#5- list all details of a ride-DONE.  
@app.route("/api/v1/rides/<rideid>")
def display_ride_details(rideid): #200, 204, 405
    if request.method != "GET":  
        return('', 405)
    upcoming_rides = {}
    upcoming_rides["table"] = "rides"
    upcoming_rides["columns"] = ["ride_id","user","timestamp","src","dest", "created_by"]
    upcoming_rides["where"] = "ride_id='"+rideid+"'"
    r = json.dumps(upcoming_rides)
    loaded_r = json.loads(r)
    headers = {'content-type': 'application/json'}
    req_resp=requests.post("http://127.0.0.1:8000/api/v1/db/read",data = r, headers = headers)
    temp=str(req_resp.text)
    temp=json.loads(temp)
    if(bool(temp)==False):
        return Response(status = 204)
    final={}
    final["rideId"]=temp["0"]["rideId"] #all timestamps should be same, also send source and dest in the response object then we done
    final["Created_by"]=temp["0"]["created_by"]
    final["Timestamp"]=temp["0"]["timestamp"]
    final["source"]=temp["0"]["src"]
    final["destination"]=temp["0"]["dest"]
    templ=[]
    for i in temp:
        templ.append(str(temp[i][u'username']))
    #print(templ)
    final["users"]=templ
    return(jsonify(final), 200)
    
"""
 {
"username" : "{username}"
}
"""
#6-JOIN AN EXISTING RIDE
@app.route("/api/v1/rides/<rideid>", methods=["POST"])
def join_existing_ride(rideid):
    if request.method != "POST":  
        return('', 405)
    user = request.get_json()["username"] 
    rides = {}
    rides["table"] = "rides"
    rides["columns"] = ["ride_id","user","timestamp","src","dest", "created_by"]
    rides["where"] = "ride_id='"+rideid+"'"
    r = json.dumps(rides)
    loaded_r = json.loads(r)
    headers = {'content-type': 'application/json'}
    req_resp=requests.post("http://127.0.0.1:8000/api/v1/db/read",data = r, headers = headers)
    temp=str(req_resp.text)
    temp=json.loads(temp)
    if(bool(temp)==False): #NO RIDE EXISTS
        return('', 204) 
    check={}
    check["table"] = "users"
    check["columns"] = ["name","pwd"]
    check["where"] = "name='"+user+"'"
    r = json.dumps(check)
    loaded_r = json.loads(r)
    headers = {'content-type': 'application/json'}
    req_resp=requests.post("http://127.0.0.1:8000/api/v1/db/read",data = r, headers = headers)
    tempnew=str(req_resp.text)
    tempnew=json.loads(tempnew)
    if(bool(tempnew)==False): #EMPTY DICTIONARY
        return('User does not exist', 400)
    else:    
        ride_id=temp["0"]["rideId"] #all timestamps should be same, also send source and dest in the response object then we done
        time_stamp=temp["0"]["timestamp"]
        src=temp["0"]["src"]
        dest=temp["0"]["dest"]
        created_by=temp["0"]["username"]
        add_user={}
        add_user["insert"]=[str(user), str(src), str(dest), ride_id, str(time_stamp), created_by]
        add_user["column"]=["user", "src", "dest", "ride_id", "timestamp", "created_by"]
        add_user["table"]="rides"
        r = json.dumps(add_user)
        loaded_r = json.loads(r)
        headers = {'content-type': 'application/json'}
        requests.post("http://127.0.0.1:8000/api/v1/db/write",data = r, headers = headers)
        return('', 200)


#7- delete a ride-DONE.
@app.route("/api/v1/rides/<rideid>",methods = ["DELETE"])  
def deleteride(rideid):
    if request.method != "DELETE":  
        return('', 405)
    rides = {}
    rides["table"] = "rides"
    rides["columns"] = ["ride_id","user","timestamp","src","dest", "created_by"]
    rides["where"] = "ride_id='"+rideid+"'"
    r = json.dumps(rides)
    loaded_r = json.loads(r)
    headers = {'content-type': 'application/json'}
    req_resp=requests.post("http://127.0.0.1:8000/api/v1/db/read",data = r, headers = headers)
    temp=str(req_resp.text)
    temp=json.loads(temp)
    if(bool(temp)==False): #EMPTY DICTIONARY
        return('', 400)
    else:
        con = sqlite3.connect("rideshare.db") 
        cur = con.cursor()   
        command1="delete from rides where ride_id ="+"'"+str(rideid)+"'"  
        cur.execute(command1) 
        con.commit()
        con.close()
        return ('', 200)

#8- reading from a db
@app.route("/api/v1/db/read",methods = ["POST"])  
def view():  
    con = sqlite3.connect("rideshare.db") 
    table = request.get_json()["table"]  
    columns = request.get_json()["columns"]
    string=""
    for i in columns:
        string+=", "+i
    string=string[1::]
    whr = request.get_json()["where"]   
    cur = con.cursor() 
    command="select "+string+" from "+table+" where "+whr  
    cur.execute(command)  

    final={}
    rows = cur.fetchall() 
    if(table=="rides"):
        for i in range(len(rows)):
            final[i]={
                "rideId":str(rows[i][0]),
                "username":str(rows[i][1]),
                "timestamp":str(rows[i][2]),
                "src":str(rows[i][3]),
                "dest":str(rows[i][4]),
                "created_by":str(rows[i][5])
            }
    elif(table=="users"):
        for i in range(len(rows)):
            final[i]={
                "username":str(rows[i][0]),
                "password":str(rows[i][1]),
            }
    return(final)
    #return(command)



#9-writing into db
@app.route("/api/v1/db/write",methods = ["POST"])  
def write(): 
    con = sqlite3.connect("rideshare.db") 
    table = request.get_json()["table"]
    column = request.get_json()["column"]
    insert = request.get_json()["insert"]
    #[u'username', u'source', u'destination', u'1001', u'DD-MM-YYYY:SS-MM-HH']
    cur = con.cursor()  
    finalstr=''
    # if table=="rides": 
    #     checksrc=str(insert[1])
    #     checkdest=str(insert[2])
    #     #print(finalstr) #prints 0 if exists, prints 1 if doesnt exist
    #     actualcreatedby=''
    #     actualrideid=''
    #     actualtimestamp=''
    #     insert.append(insert[0])
    stringcol=""
    stringinsert=""
    for i in column:
        stringcol+=", "+str(i)
    stringcol=stringcol[1::] 
    for i in insert:
        stringinsert+=", "+"'"+str(i)+"'"
    stringinsert=stringinsert[1::]   
    command="insert into "+ table+" "+"("+stringcol+")"+" values "+"("+stringinsert+")"
    cur.execute(command)  
    con.commit()   
    con.close()
    return('', 200)
"""
{"insert" : ["name4", "place1", "place2", "1237", "2019-10-23 09:09:52"],
"column" : ["user","src","dest", "ride_id", "timestamp"],
"table" : "rides"
}"""
if __name__ == '__main__':	
	app.debug=True
	app.run()