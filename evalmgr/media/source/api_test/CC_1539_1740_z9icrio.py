from flask import Flask,  request,  jsonify, abort, Response, json
import requests
import string
import datetime
import sqlalchemy as db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base,User, Ride2
from sqlalchemy.sql.expression import func
import pandas as pd
from sqlalchemy import create_engine
from database import Base,User, Ride2, Join


app = Flask(__name__)

    

# Connect to Database and create database session
engine = create_engine('sqlite:///assignment.db?check_same_thread=False')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


#writing to a database with this function api 
@app.route('/')
@app.route("/api/v1/db/write",methods=["POST"])
def write_db():
    #access book name sent as JSON object 
    #in POST request body
    data=request.get_json()
    try:
        if(data['table']=='User' and data['action']=='New_user'):
            new_user = User(user_name=data['user_data'][0], password=data['user_data'][1])
            session.add(new_user)
            session.commit()
            respose_ = Response(status =200)
            return respose_ # change it to response()
        elif(data['table']=='Ride' and data['action']=='New_ride'):            
            #Create a new ride id for each ride
            timestamp = data['user_data'][1]
            timestamp=timestamp.split(':')
            time =timestamp[1].split('-')
            date =timestamp[0].split('-')
            Datetime = datetime.datetime(int(date[2]),int(date[1]),int(date[0]),int(time[2]),int(time[1]),int(time[0]))
            new_ride = Ride2(ride_id=data['user_data'][-1],user_name=data['user_data'][0],source=data['user_data'][2],destination=data['user_data'][3],stamp=Datetime)
            session.add(new_ride)
            session.commit()
            respose_ = Response(status =200)
            return respose_ # change it to response()
        elif(data['table']=='User' and data['action']=='delete_user'):
            user_name = data['user_data'][0]
            # user = session.query(User).get(user_name)
            # session.delete(user)
            session.query(User).filter(User.user_name==user_name).delete(synchronize_session=False)
            session.commit()
            respose_ = Response(status = 200)
            return respose_
        elif(data['table']=="Ride" and data['action']=='delete_ride'):
            ride_id = data['ride_id']
            # ride = session.query(Ride2).get(ride_id)
            # session.delete(ride)
            session.query(Ride2).filter(Ride2.ride_id==ride_id).delete(synchronize_session=False)
            session.commit()
            respose_ = Response(status = 200)
            return respose_
        elif(data['table']=="Join" and data['action']=='ride_status'):#joining a ride 
            rideid = data['ride_id']
            username = data['user_name']
            joinride =Join(ride_id=rideid,user_name=username)
            session.add(joinride)
            session.commit()
            respose_ = Response(status = 200)
            return respose_
        else:
             # change it to response()
            respose_ = Response(status = 400)
            return respose_

    except KeyError:
        respose_ = Response(status = 400)
        return respose_




@app.route('/')
@app.route("/api/v1/db/read",methods=["POST"])
def read_db():
    data = request.get_json()
    if(data['action']=='New_user' or data['action']=='delete_user'):
        user_name = data['user_data'][0]
        user_db = session.query(User).get(user_name)
        if(user_db==None):
            #return "ok"
            response = Response(status = 400) # returns 400 when a user is not present 
            return response
            #    return "ok"
        else:
            response = Response(status = 200) # returns 200 when a user is present 
            return response
            #return "ok"
    elif(data['action']=='New_ride'):
        user_name = data['user_data'][0]
        user_db = session.query(User).get(user_name)
        if(user_db==None):
            response = Response(status = 400) # returns 400 when a user is not present 
            return response
        else:
            response = Response(status = 200) # returns 200 when a user is present 
            return response
    elif(data['action']=='upcoming_rides'):
        source = data['user_data'][0]
        destination = data['user_data'][1]
        connection = engine.connect()
        query = db.select([Ride2]).where(db.and_(Ride2.source==source,Ride2.destination==destination))
        results = connection.execute(query).fetchall()
        ret=str(results)
        response_ = Response(response=ret,status=200)
        return response_
    elif(data['action']=='get_max_ride_id'):
        max_id =session.query(func.max(Ride2.ride_id)).scalar()
        if(max_id ==None):
            response_ = Response(response=str(0),status=200)
            return response_
        else:
            response_ = Response(response=str(max_id),status=200)
            return response_
    elif(data['action']=='check_ride'):
        ride_id = data['ride_id']
        user_name = data['user_name']
        user_status = session.query(User).get(user_name)
        ride_status = session.query(Ride2).get(ride_id)
        if(ride_status==None or user_status==None):
            response = Response(status = 400) # returns 400 when a ride is not present 
            return response
        else:
            response = Response(status = 200) # returns 200 when a ride is present 
            return response
    elif(data['action']=='delete_ride'):
        ride_id = data['ride_id']
        ride_status = session.query(Ride2).get(ride_id)
        if(ride_status==None ):
            response = Response(status = 400) # returns 400 when a ride is not present 
            return response
        else:
            response = Response(status = 200) # returns 200 when a ride is present 
            return response
    elif(data['action']=='ride_status'):
        ride_id = data['ride_id']
        user_name = data['user_name']
        status = session.query(Join).get({'ride_id':ride_id,'user_name':user_name})        
        if(status==None ):
            response = Response(status = 400) # returns 400 when a ride is not present 
            return response
        else:
            response = Response(status = 200) # returns 200 when a ride is present 
            return response
    elif(data['action']=='check_ride_detail'):
        ride_id = data['ride_id']       
        ride_status = session.query(Ride2).get(ride_id)
        if(ride_status==None ):
            response = Response(status = 400) # returns 400 when a ride is not present 
            return response
        else:
            response = Response(status = 200) # returns 200 when a ride is present 
            return response
    elif(data['action']=='check_ride_detail1'):
        ride_id = data['ride_id']
        connection = engine.connect()
        query = db.select([Ride2]).where(Ride2.ride_id == ride_id)
        results = connection.execute(query).fetchall()
        query1 = db.select([Join]).where(Join.ride_id == ride_id)
        results1 = connection.execute(query1).fetchall()
        ret=str(results) + "&"+str(results1)
        response_ = Response(response=ret,status=200)
        return response_        
    elif(data['action']=='ride_present'):
        user_name = data['user_data'][0]
        # present_date = data['user_data'][1]
        connection = engine.connect()
        query = db.select([Ride2]).where(Ride2.user_name == user_name)
        results = connection.execute(query).fetchall()
        ret = str(results)
        response_ = Response(response=ret,status=200)
        return response_  
    else:
        response_ = Response(response=ret,status=400)
        return response_

        


@app.route('/')
@app.route("/api/v1/users",methods=["PUT"])
def add_user():
    data=request.get_json()
    if(len(data)==2):
        user_name = data['username']
        password = data['password']
        pas= check_password(password)
        if(pas>0):
            myobj ={"table":"User","action":"New_user","user_data":[user_name,password]}
            check_user = requests.post("http://ec2-35-172-90-20.compute-1.amazonaws.com/api/v1/db/read",json = myobj)            
            if(str(check_user.status_code)=="400"):
                response = requests.post("http://ec2-35-172-90-20.compute-1.amazonaws.com/api/v1/db/write",json = myobj)
                new_response = Response(status=201)
                return new_response
            else:
                new_response = Response(status=400)
                return new_response # username already taken
        else:
            new_response = Response(status=400)
            return new_response # wrong password format
    else:
        new_response = Response(status=405)
        return new_response # Bad request

    
def check_password(password):
    if(len(password)!=40):
        return -1
    for letter in password:
        if letter not in string.hexdigits:
            return -1
    return 1


@app.route('/')
@app.route("/api/v1/users/<username>",methods=["DELETE"])
def remove_user(username):
    user_name = username
    present_date =datetime.datetime.now()
    myobj ={"table":"User","action":"delete_user","user_data":[user_name]}
    check_user = requests.post("http://ec2-35-172-90-20.compute-1.amazonaws.com/api/v1/db/read",json = myobj)
    #Add code to check if the user has a future,if he has return 400 status  
    if(str(check_user.status_code)=="200"):
        ride_present = {"table":"User","action":"ride_present","user_data":[user_name]}
        ride_status = requests.post("http://ec2-35-172-90-20.compute-1.amazonaws.com/api/v1/db/read",json = ride_present)
        my_str1 = str(ride_status.text)
        
        if(len(my_str1)==2):
            response = requests.post("http://ec2-35-172-90-20.compute-1.amazonaws.com/api/v1/db/write",json = myobj)
            if(str(response.status_code)=="200"):
                response_ = Response(status=200)
                return response_ #User deleted successfully
            else:
                response_ = Response(status=500)
                return response_ #internal server error
        else:
            my_str  = my_str1.split("'),")
            temp= []
            for i in my_str:
                temp.append(i[2:].split(','))
            for i in temp:
                i[3]=i[3][-4:]
                i[-2]=i[-2][:-1]
            temp[-1][-1]=temp[-1][-1][:-3]
            ret = []
            for my_lis in temp:
                user_name = my_lis[-1][2:]
                ride_id = int(my_lis[0])
                date=my_lis[5][1:]+'-'+my_lis[4][1:]+'-'+my_lis[3][-4:]+':'+my_lis[8][1:]+'-'+my_lis[7][1:]+'-'+my_lis[6][1:]
                x = datetime.datetime(int(my_lis[3][-4:]),int(my_lis[4][1:]),int(my_lis[5][1:]),int(my_lis[6][1:]),int(my_lis[7][1:]),int(my_lis[8][1:]))
                y=datetime.datetime.now()
                if(x>y):
                    # ret_dict={"rideId":ride_id,"username":user_name,"timestamp":date}
                    ret.append(x)
            if(len(ret)!=0):
                response_ = Response(status=400)
                return response_
            else:
                response = requests.post("http://ec2-35-172-90-20.compute-1.amazonaws.com/api/v1/db/write",json = myobj)
                if(str(response.status_code)=="200"):
                    response_ = Response(status=200)
                    return response_ #User deleted successfully
                else:
                    response_ = Response(status=500)
                    return response_ #internal server error 
    else:
        response_ = Response(status=400)
        return response_


@app.route('/')
@app.route("/api/v1/rides",methods=["POST"])
def new_ride():
    data = request.get_json()
    user_name = data['created_by']
    timestamp = data['timestamp']
    source = data['source']
    destination = data['destination']
    valid_place = check_place(source,destination)
    if(valid_place<0):
        response_ = Response(status=400)
        return response_
    ride_obj = {"action":"get_max_ride_id"}
    max_id = requests.post("http://ec2-35-172-90-20.compute-1.amazonaws.com/api/v1/db/read",json = ride_obj)
    ride_id=int(max_id.text)+1
    myobj ={"table":"Ride","action":"New_ride","user_data":[user_name,timestamp,source,destination,ride_id]}     
    check_user = requests.post("http://ec2-35-172-90-20.compute-1.amazonaws.com/api/v1/db/read",json = myobj)
    if(str(check_user.status_code)=="200"):
        response = requests.post("http://ec2-35-172-90-20.compute-1.amazonaws.com/api/v1/db/write",json = myobj)
        # return str(response.status_code)
        if(str(response.status_code)=="200"):
            response_ = Response(status=201)
            return response_
        else:
            response_ = Response(status=500)
            return response_
    else:
        response_ = Response(status=400)#User doesnot exit
        return response_



@app.route('/')
@app.route("/api/v1/rides",methods=["GET"])
def list_ride():
    source = request.args.get("source")
    destination = request.args.get("destination")
    # query = db.select([Ride2]).where(db.and_(Ride2.source==source,Ride2.destination==destination))
    # results1 = connection.execute(query).fetchall()
    # return str(source)
    place_present = check_place(int(source),int(destination))
    # return str(place_present)
    if(place_present==1):
        myobj ={"table":"Ride","action":"upcoming_rides","user_data":[source,destination]}
        # return myobj
        list_ride = requests.post("http://ec2-35-172-90-20.compute-1.amazonaws.com/api/v1/db/read",json = myobj)
        # return list_ride.text
        my_str1 = list_ride.text
        if(len(my_str1)==2):
            response_ = Response(status=204)
            return response_ #no rides found just return []

        my_str  = my_str1.split("'),")
        temp= []
        for i in my_str:
            temp.append(i[2:].split(','))
        for i in temp:
            i[3]=i[3][-4:]
            i[-2]=i[-2][:-1]
        temp[-1][-1]=temp[-1][-1][:-3]
        ret = []
        for my_lis in temp:
            user_name = my_lis[-1][2:]
            ride_id = int(my_lis[0])
            date=my_lis[5][1:]+'-'+my_lis[4][1:]+'-'+my_lis[3][-4:]+':'+my_lis[8][1:]+'-'+my_lis[7][1:]+'-'+my_lis[6][1:]
            x = datetime.datetime(int(my_lis[3][-4:]),int(my_lis[4][1:]),int(my_lis[5][1:]),int(my_lis[6][1:]),int(my_lis[7][1:]),int(my_lis[8][1:]))
            y=datetime.datetime.now()
            if(x>y):
                ret_dict={"rideId":ride_id,"username":user_name,"timestamp":date}
                ret.append(ret_dict)
        # response_  = Response(response = jsonify(ret),status=200)
        # return response_
        return jsonify(ret)
        #return "ok"        
        
    else:
        response_ = Response(status=400)#wrong src n dst
        return response_


@app.route('/')
@app.route("/api/v1/rides/<rideId>",methods=["POST"])
def join_ride(rideId):
    data = request.get_json()
    user_name = data['username']
    rideobj = {"action":"check_ride","ride_id":rideId,"user_name":user_name}
    check_ride = requests.post("http://ec2-35-172-90-20.compute-1.amazonaws.com/api/v1/db/read",json = rideobj)
    if(str(check_ride.status_code)=="200"):
        ride_status_obj = {"table":"Join","action":"ride_status","ride_id":rideId,"user_name":user_name}
        ride_status = requests.post("http://ec2-35-172-90-20.compute-1.amazonaws.com/api/v1/db/read",json = ride_status_obj)
        if(str(ride_status.status_code)=="200"):
            #return "ok"
            response_ = Response(status=400)#user already added to the ride
            return response_
        else:
            join_ride = requests.post("http://ec2-35-172-90-20.compute-1.amazonaws.com/api/v1/db/write",json = ride_status_obj)
            response_ = Response(status=201)#added succesfully
            return response_
    else:#return response for ride not exist 
        response_ = Response(status=400)#ride dosnot exist
        return response_

@app.route('/')
@app.route("/api/v1/rides/<rideId>",methods=["GET"])
def ride_detail(rideId):
    rideobj = {"action":"check_ride_detail","ride_id":rideId}
    # return rideobj
    check_ride = requests.post("http://ec2-35-172-90-20.compute-1.amazonaws.com/api/v1/db/read",json = rideobj)
    #return str(check_ride.status_code)
    if(str(check_ride.status_code)=="200"):
        rideobj1 ={"action":"check_ride_detail1","ride_id":rideId}
        ride_detail1 = requests.post("http://ec2-35-172-90-20.compute-1.amazonaws.com/api/v1/db/read",json = rideobj1)
        # return str(ride_detail1.text)
        my_str1 = ride_detail1.text
        # return str(my_str1)
        ret1 = my_str1.split('&')
        users = ret1[1].split('),')
        users1=[]
        new1 = []
        if(len(str(users))>6):
           
            for i in users:
                users1.append(i.split(',')[1])
           
            for i in users1:
                new1.append(i.replace(')]', ' ').strip()[1:-1])
        aa = ret1[0][2:].split(",")
        dest =  aa[2].strip()
        src = aa[1].strip()
        year = aa[3][-4:]
        month = aa[4].strip()
        date = aa[5].strip()
        hour= aa[6].strip()
        minute = aa[7].strip()
        sec = aa[8][:-1].strip()

        user = aa[-1][:-2].strip()
        user = user[1:-1]
        details_ride = {"rideId":int(rideId),"Created_by":user,"users":new1,"Timestamp":date+'-'+month+'-'+year+':'+sec+'-'+minute+'-'+hour,"source":int(src),"destination":int(dest)}
        return jsonify(details_ride)
       
    else:
        response_ = Response(status=400)
        return response_ #invalid rideid





@app.route('/')
@app.route("/api/v1/rides/<rideId>",methods=["DELETE"])
def ride_delete(rideId):  
    rideobj = {"table":"Ride","action":"delete_ride","ride_id":rideId}

    check_ride = requests.post("http://ec2-35-172-90-20.compute-1.amazonaws.com/api/v1/db/read",json = rideobj)
    # return str(check_ride.status_code)
    if(str(check_ride.status_code)=="200"):
        del_ride = requests.post("http://ec2-35-172-90-20.compute-1.amazonaws.com/api/v1/db/write",json = rideobj)
        # ride =session.query(Ride2).get(rideId)
        # return str(del_ride.status_code)
        if(str(del_ride.status_code)=="200"):
            response_ = Response(status=200)
            return response_ #deleted succesfuly
        else:
            response_ = Response(status=500)
            return response_ #ISE       
    else:#return response for ride not exist 
        response_ = Response(status=400)
        return response_ #invalid rideid



def check_place(src,dst):
    df = pd.read_csv("AreaNameEnum.csv")
    area_no = list(df['Area No'])
    if(src not in area_no or dst not in area_no):
        return -1
    else:
        return 1





























# @app.route("/api/v1/rides2",methods=["GET"])
# def list_ride2():#get source and dest from url 
    
#     source = 3
#     destination =5
#     myobj ={"table":"Ride2","action":"upcoming_rides","user_data":[source,destination]}
#     check_user = requests.post("http://ec2-35-172-90-20.compute-1.amazonaws.com/api/v1/db/read",json = myobj)
#     # return check_user.text
#     my_str1 = check_user.text
#     my_str  = my_str1.split("'),")
#     temp= []
#     for i in my_str:
#         temp.append(i[2:].split(','))
#     for i in temp:
#         i[3]=i[3][-4:]
#         i[-2]=i[-2][:-1]
#     temp[-1][-1]=temp[-1][-1][:-3]
#     ret = []
#     for my_lis in temp:
#         user_name = my_lis[-1][2:]
#         ride_id = int(my_lis[0])
#         date=my_lis[5][1:]+'-'+my_lis[4][1:]+'-'+my_lis[3][-4:]+':'+my_lis[8][1:]+'-'+my_lis[7][1:]+'-'+my_lis[6][1:]
#         x = datetime.datetime(int(my_lis[3][-4:]),int(my_lis[4][1:]),int(my_lis[5][1:]),int(my_lis[6][1:]),int(my_lis[7][1:]),int(my_lis[8][1:]))
#         y=datetime.datetime.now()
#         if(x>y):
#             ret_dict={"rideId":ride_id,"username":user_name,"timestamp":date}
#             ret.append(ret_dict)
#     return jsonify(ret)     
       


    

# @app.route("/api/v1/rides_id",methods=["GET"])
# def id():
#     max_id =session.query(func.max(Ride2.ride_id)).scalar()
#     return str(max_id)









































@app.route('/')
@app.route("/api/v1/db/read1",methods=["POST"])
def read_db1():
    # data = request.get_json()
    # if(data['action']=='New_user'):
    #     user_name = data['user_data'][0]
    #     user_db = session.query(User).get(user_name)
    #     if(str(user_db)=="None"):
    #         return "None"
    #     else:
    #         return "Not None"


    
    book = session.query(User).all()
    return jsonify(books= [b.serialize for b in book])
 
# @app.route('/')
# @app.route("/api/v1/db/read2",methods=["POST"])
# def read_db2():
#     # data = request.get_json()
#     # if(data['action']=='New_user'):
#     #     user_name = data['user_data'][0]
#     #     user_db = session.query(User).get(user_name)
#     #     if(str(user_db)=="None"):
#     #         return "None"
#     #     else:
#     #         return "Not None"


    
#     book = session.query(Ride2).all()
#     return str(book)
# @app.route('/')
# @app.route("/api/v1/db/read2",methods=["POST"])
# def read_db2():
#     # data = request.get_json()
#     # if(data['action']=='New_user'):
#     #     user_name = data['user_data'][0]
#     #     user_db = session.query(User).get(user_name)
#     #     if(str(user_db)=="None"):
#     #         return "None"
#     #     else:
#     #         return "Not None"


    
#     book = session.query(Ride2).all()
#     return jsonify(rides= [b.serialize for b in book])
 

          




    





if __name__ == '__main__': 
    app.debug=True
    app.run()
