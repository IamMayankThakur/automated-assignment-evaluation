from flask import Flask, render_template,\
jsonify,request,abort, Response
import json
import requests
from datetime import datetime
app=Flask(__name__)

import sqlite3

#@app.route('/write/)
#def write(username,password):

@app.route('/api/v1/db/read',methods=['POST'])
def read_db():
    req=request.get_json()

    table= req.get("table")
    columns= req.get("columns")
    where= req.get("where")

    final_column=''
    for i in columns:
        final_column+= i+', '
    final_column=final_column[:-2]

    final_where=''
    for i in where:
        final_where+= i+' and '
    

    final_where= final_where[:-5]

    # print("Final column",final_column)
    # print("Final where",final_where)

    query='SELECT '+final_column+' FROM '+table+' WHERE '+ final_where+';'
    res={}
    #print(query)
    try:
        conn=sqlite3.connect("RideShare")
        c= conn.cursor()

        check= c.execute(query).fetchall()
        #print(check)
        count = len(check)
        #print("COUNT", count)
        #res={}
        res['count']=count
        #print("COUNT res",res["count"])
        column_index={}
        for i in range(len(columns)):
            column_index[i]=columns[i]
        #print(column_index)
        for i in columns:
            res[i]=[]

        for i in range(count):
            for j in range(len(check[i])):
                res[column_index[j]].append(check[i][j])
        
        
        res['status']=200
        #print(res)
        conn.close()
        return json.dumps(res)
    
    except Exception as err:

        print(err)
        res['status']=400
        conn.close()
        return json.dumps(res)
    
    finally :
        if conn:
            conn.close()
        else:
            pass


@app.route('/api/v1/db/write',methods=['POST'])
def write_db():
    req=request.get_json()
    table=req.get("table")
    flag=req.get("flag")
    if flag==0:     #INSERT
        values=req.get("values")
        columns=req.get("columns")
        final_column=''
        for i in columns:
            final_column+="'"+i+"'"+', '
        final_column=final_column[:-2]
        final_values=''
        for i in values:
            final_values+="'"+i+"'"+', '
        final_values=final_values[:-2]

        query='INSERT INTO '+table+' ('+final_column+') VALUES ('+final_values+');'
    
    else:
        cond=req.get("condition")
        final_cond=''
        for i in cond:
            final_cond+=i+' and '
        final_cond=final_cond[:-5]

        query='DELETE FROM '+table+' WHERE '+final_cond+";"
    
    print(query)
    res={}
    try:
        conn=sqlite3.connect("RideShare")
        c= conn.cursor()
        q="PRAGMA foreign_keys=OFF"
        c.execute(q)
        conn.commit()
        q="PRAGMA foreign_keys=ON"
        c.execute(q)
        conn.commit()
        try:
            c.execute(query)
            conn.commit()
            res["count"]=1
            res["status"]=200
            conn.close()
            return json.dumps(res)
        except Exception as e:
            print("HERE1")
            print(e)
            res["count"]=0
            res["status"]=400
            conn.close()
            return json.dumps(res)

    except Exception as err:
        print("HERE")
        print(err)
        res["count"]=0
        res["status"]=400
        conn.close()
        return json.dumps(res)
        
    finally :
        if conn:
            conn.close()
        else:
            pass






@app.route('/api/v1/users',methods=['PUT'])
def Add_user():
    
    req= request.get_json()
    uname= req.get("username")
    print(uname)
    password= req.get("password")

    if(uname=="" or password==""):
       # Response(status=400)
        return json.dumps({}),400

    if len(password)!=40:
       # Response(status=400)
        return json.dumps({}),400    
    try:
        sha=int(password,16)
    except ValueError:
       # Response(status=400)    #return response message as invalid password
        return json.dumps({}),400



    r=requests.post('http://ec2-3-85-118-254.compute-1.amazonaws.com/api/v1/db/read',
    json={
        'table':'User',
        'columns':['username'],
        'where':["username='"+uname+"'"]

    })

    count=r.json().get("count")
    if count>0:
        status_code=r.json().get("status")
        #print(count)
        #res = {}
        #res["count"] = count
        #res["username"]=r.json().get("username")

       # Response(status=400)      #return username already exists
        return json.dumps({}),400
        
        #return json.dumps(res)
    else:
        r=requests.post('http://ec2-3-85-118-254.compute-1.amazonaws.com/api/v1/db/write',
        json={
            'table':'User',
            'flag':0,
            'columns':['username','password'],
            'values':[uname,password]

        })

        status_code=r.json().get("status")
        count=r.json().get("count")
        res={}
        print(count)
        if count==1:
            res["count"]=count
            #res["username"]=r.json().get()
            #print("COUNT",count)
            
            #Response(status=201)
            return json.dumps({}),201
        
        else:
            #res["count"]=count
           # Response(status=400)   #return couldn't be created
            #return json.dumps(res)
            return json.dumps({}),400


@app.route('/api/v1/users/<username>',methods=['DELETE'])
def REMOVE_user(username):

    r=requests.post('http://ec2-3-85-118-254.compute-1.amazonaws.com/api/v1/db/read',
    json={
        'table':'User',
        'columns':['username'],
        'where':["username='"+username+"'"]
    })
    
    count=r.json().get("count")
    if count>0:
        r=requests.post('http://ec2-3-85-118-254.compute-1.amazonaws.com/api/v1/db/write',
        json={
            'table':'User',
            'flag':1,
            'condition':["username = '"+username+"'"]
        })
        status_code=r.json().get("status")
        count=r.json().get("count")
       # Response(status=200)
        return json.dumps({}),200



    else:
        #status_code=r.json().get("status")
        #if status_code==200:
         #   return Response(status=400)
       # Response(status=400)    #return username doesn't exist
        return json.dumps({}),400



@app.route('/api/v1/rides',methods=['POST'])
def ADD_ride():
    req= request.get_json()
    uname= req.get("created_by")
    #print(uname)
    #password= req.get("password")
    timestamp=req.get("timestamp")
    source=int(req.get("source"))
    dest=int(req.get("destination"))
    #if source==dest:
    #    return Response(status=400)

    if source==dest:
       # Response(status=400)
        return json.dumps({}),400
    
    r=requests.post('http://ec2-3-85-118-254.compute-1.amazonaws.com/api/v1/db/read',
    json={
        'table':'User',
        'columns':['username'],
        'where':["username='"+uname+"'"]
    })

    count=r.json().get("count")
    if count>0:
        r1=requests.post('http://ec2-3-85-118-254.compute-1.amazonaws.com/api/v1/db/read',
        json={
            'table':'Area',
            'columns':['areaname'],
            'where':["areaid="+str(source)+""]
        })
        
        count1=r1.json().get("count")
        if count1>0:
            r2=requests.post('http://ec2-3-85-118-254.compute-1.amazonaws.com/api/v1/db/read',
            json={
                'table':'Area',
                'columns':['areaname'],
                'where':["areaid="+str(dest)+""]
            })
            count2=r2.json().get("count")
            if count2>0:
                r3=requests.post('http://ec2-3-85-118-254.compute-1.amazonaws.com/api/v1/db/write',
                json={
                    'table':'Ride',
                    'flag':0,
                    'columns':['source','dest','timestamp','username'],
                    'values':[str(source),str(dest),str(timestamp),uname]
                })

                count3=r3.json().get("count")
                status_code=r3.json().get("status")
                if count3==1:
                   # Response(status=201)
                    return json.dumps({}),201

                else:
                  #  Response(status=400)     #return
                    return json.dumps({}),400

            else:
               # Response(status=400)     #return dest doesn't exist
                return json.dumps({}),400
        
        else:
     #       Response(status=400)    #return source doesn't exist
            return json.dumps({}),400
    
    else:
      #  Response(status=400)     #return username doesn't exist
        return json.dumps({}),400


    

@app.route('/api/v1/rides',methods=['GET'])
def upcoming_ride():
    source=int(request.args.get("source"))
    dest=int(request.args.get("destination"))
    #time=str(datetime.now().strftime("%d-%m-%Y:%S-%M-%H"))
    #print("HERE")


    r1=requests.post('http://ec2-3-85-118-254.compute-1.amazonaws.com/api/v1/db/read',
    json={
        "table":"Area",
        "columns":["areaname"],
        "where":["areaid='"+str(source)+"'"]
    })
    count1=r1.json().get("count")

    if count1>0:
        r2=requests.post('http://ec2-3-85-118-254.compute-1.amazonaws.com/api/v1/db/read',
        json={
            "table":"Area",
            "columns":["areaname"],
            "where":["areaid='"+str(dest)+"'"]
        })

        
        count2=r2.json().get("count")

        if count2>0:

            r=requests.post('http://ec2-3-85-118-254.compute-1.amazonaws.com/api/v1/db/read',
            json={
                "table":"Ride",
                "columns":["rideid","username","timestamp"],
                "where":["source='"+str(source)+"'","dest='"+str(dest)+"'"]
            })
            #print(r)
            count=r.json().get("count")
            if count>0:
                ans=[]
            
                res_rideid=r.json().get("rideid")
                res_username=r.json().get("username")
                res_timestamp=r.json().get("timestamp")

                for i in range(count):
                    time_comp=res_timestamp[i]
                    day= time_comp[:2]
                    month= time_comp[3:5]
                    year= time_comp[6:10]
                    sec= time_comp[11:13]
                    min= time_comp[14:16]
                    hour=time_comp[17:19]

                    cur_time= (datetime.now().strftime("%d-%m-%Y:%S-%M-%H"))
                    cur_day= cur_time[:2]
                    cur_mon= cur_time[3:5]
                    cur_year= cur_time[6:10]
                    cur_sec= cur_time[11:13]
                    cur_min= cur_time[14:16]
                    cur_hour= cur_time[17:19]

                    cur= datetime(int(cur_year),int(cur_mon),int(cur_day),int(cur_hour),int(cur_min),int(cur_sec))
                    comp= datetime(int(year),int(month),int(day),int(hour),int(min),int(sec))

                    if comp>cur:

                        res={}
                        res["rideId"]=res_rideid[i]
                        res["username"]=res_username[i]
                        res["timestamp"]=res_timestamp[i]
                        ans.append(res)

                if len(ans)>0:
                   # Response(status=200)
                    return json.dumps(ans),200

                else:
                   # Response(status=400)
                    return json.dumps({}),400

            elif count==0:
               # Response(status=204)    #no upcoming rides
                return json.dumps({}),204

            else:
             #   Response(status=400)    #invalid source or destination
                return json.dumps({}),400
        
        else:
           # Response(status=400)  #invalid destination
            return json.dumps({}),400
    
    else:
      #  Response(status=400) #invalid source
        return json.dumps({}),400


@app.route('/api/v1/rides/<rideId>',methods=['GET'])
def ride_detail(rideId):
    #id=int(req.args.get("rideid"))

    r=requests.post('http://ec2-3-85-118-254.compute-1.amazonaws.com/api/v1/db/read',
    json={
        "table":"Ride",
        "columns":["rideid","username","timestamp","source","dest"],
        "where":["rideid='"+str(rideId)+"'"]
    })

    count= r.json().get("count")
    if count>0:
        res={}
        res["rideId"]= rideId
        res["created_by"]= r.json().get("username")[0]
        res["timestamp"]= r.json().get("timestamp")[0]
        res["source"]= r.json().get("source")[0]
        res["destination"]= r.json().get("dest")[0]

        res["users"]=[]

        r1=requests.post('http://ec2-3-85-118-254.compute-1.amazonaws.com/api/v1/db/read',
        json={
            "table":"RideUser",
            "columns":["username"],
            "where":["rideid='"+str(rideId)+"'"]
        })

        count1=r1.json().get("count")
        if count1>0:
            u_join= r1.json().get("username")
            joined=""
            for i in u_join:
                joined+= i+", "
            joined=joined[:-2]
            res["users"]= joined
        #Response(status=200)
        return json.dumps(res),200


    else:
        #Response(status=204)
        return json.dumps({}),204


@app.route('/api/v1/rides/<rideId>',methods=['POST'])
def join_ride(rideId):
    req= request.get_json()
    uname= req.get("username")

    r=requests.post('http://ec2-3-85-118-254.compute-1.amazonaws.com/api/v1/db/read',
    json={
        "table":"Ride",
        "columns":["rideid"],
        "where":["rideid='"+str(rideId)+"'"]
    })

    count=r.json().get("count")
    if count>0:
        r1=requests.post('http://ec2-3-85-118-254.compute-1.amazonaws.com/api/v1/db/read',
        json={
            "table":"User",
            "columns":["username"],
            "where":["username='"+str(uname)+"'"]
        })

        count1=r.json().get("count")

        if count1>0:
            r2=requests.post('http://ec2-3-85-118-254.compute-1.amazonaws.com/api/v1/db/write',
            json={
                "table":"RideUser",
                "columns":["username","rideid"],
                "flag":0,
                "values":[uname,rideId]
                
            })

            count2=r2.json().get("count")
            if count2>0:
                res={}
               # Response(status=200)
                return jsonify({}),200

            else:
               # Response(status=400)    #unsuccessful
                return json.dumps({}),400

        else:
          #  Response(status=400)    #user doesn't exist
            return json.dumps({}),400

    else:
      #  Response(status=400)   #invalid rideid, rideid doesn't exist
        return json.dumps({}),400


@app.route('/api/v1/rides/<rideId>',methods=['DELETE'])
def delete_ride(rideId):

    r=requests.post('http://ec2-3-85-118-254.compute-1.amazonaws.com/api/v1/db/read',
    json={
        "table":"Ride",
        "columns":["rideid"],
        "where":["rideid='"+str(rideId)+"'"]
    })

    count=r.json().get("count")
    if count>0:
        r1=requests.post('http://ec2-3-85-118-254.compute-1.amazonaws.com/api/v1/db/write',
        json={
            "table":"Ride",
            "flag":1,
            "condition":["rideid="+str(rideId)]
        })

        count1=r1.json().get("count")
        if count1==1:
        #    Response(status=200)
            return json.dumps({}),200
        else:
          #  Response(status=400)
            return json.dumps({}),400
    else:
       # Response(status=405)
        return json.dumps({}),405

if __name__ == '__main__':	
	app.debug=True
	app.run()
