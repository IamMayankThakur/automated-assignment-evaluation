from flask import Flask, render_template,\
jsonify,request,abort,redirect
import requests
from datetime import datetime
from flask_mysqldb import MySQL

def is_sha1(maybe_sha):
    if len(maybe_sha) != 40:
        return False
    try:
        sha_int = int(maybe_sha, 16)
    except ValueError:
        return False
    return True

app= Flask(__name__)

app.config['MYSQL_HOST']	 = 'localhost'
app.config['MYSQL_USER']	 = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] 		 = 'flask'

mysql=MySQL(app)

#Users={}
Rides={}
#cur=mysql.connection.cursor()
#v=cur.execute("select *from rides ORDER BY rideId DESC LIMIT 1")
#r=v.fechall()
rideId=8
avail=[]


@app.route("/api/v1/users", methods=["PUT"])
def adduser():
	if(request.method == 'PUT'):
		Users={}
		user=request.get_json()["username"]
		passw=request.get_json()["password"]
		check={"type":1,"user":user}
		Users["value"]=[user,passw]
		Users["type"]=1
		send=requests.post('http://34.230.153.167/api/v1/db/read',json=check)
		res=send.json()
		if(len(res['val'])!= 0):
			return jsonify(),400
		else:
			check=is_sha1(passw)
			if check:
				send1=requests.post('http://34.230.153.167/api/v1/db/write',json=Users)
				res1=send1.json()
				if(res1['val']==200):
					return jsonify(),200
				else:
					return jsonify(),400
			else:
				return jsonify(),400	
	else:
		return jsonify(),405


@app.route("/api/v1/users/<username>", methods=["DELETE"])
def deluser(username):
	if(request.method == 'DELETE'):
		check={"type":1,"user":username}
		send={}
		send["type"]=2
		send["value"]=username
		rec=requests.post('http://34.230.153.167/api/v1/db/read',json=check)
		res=rec.json()
		if(len(res['val'])== 0):
			return jsonify(),400
		else:
			sent=requests.post('http://34.230.153.167/api/v1/db/write',json=send)
			r=sent.json()
			
			if((r['val']) == 400):
				return jsonify(),400
			else:
				return jsonify(),200
	else:
		return jsonify(),405


@app.route("/api/v1/rides",methods=["POST"])
def create_ride():
	if(request.method == 'POST'):
		global rideId
		user=request.get_json()["created_by"]
		check={"type":1,"user":user}
		timest=request.get_json()["timestamp"]
		source=request.get_json()["source"]
		destination=request.get_json()["destination"]
		dic={}
		dic["type"]=3
		dic["ride"]=[rideId,user,timest,source,destination]
		send=requests.post('http://34.230.153.167//api/v1/db/read',json=check)
		res=send.json()
		if (int(source)>190 or int(destination)>190 or int(source)<0 or int(destination)<0):
			print("qwe")
			return jsonify(),400
		if(len(res['val'])== 0):
			print("asd")
			return jsonify(),400
		else:
			r=requests.post('http://34.230.153.167/api/v1/db/write',json=dic)
			s=r.json()
			if((s['val'])== 400):
				print("zxcv")
				return jsonify(),400	
			rideId+=1
			return jsonify(),200
	else:
		return jsonify(),405

@app.route("/api/v1/rides",methods=["GET"])
def get_rides():
	if(request.method == 'GET'):
		source=request.args.get('source')
		destination=request.args.get('destination')
		dic={}
		dic["type"]=2
		dic["ride"]=[source,destination]
		send=requests.post('http://127.0.0.1:5000/api/v1/db/read',json=dic)
		res=send.json()
		curr_time=datetime.now()
		cur_time=curr_time.strftime("%Y-%m-%d:%H-%M-%S")
		ans=[]
		if(len(res['val'])==0):
			return jsonify(),204
		else:
			for i in res['val']:
				r=datetime.strptime(i[2],"%d-%m-%Y:%S-%M-%H")
				time=datetime.strftime(r,"%Y-%m-%d:%H-%M-%S")
				if(not(cur_time>time)):
					ans.append({"rideId":i[0],"username":i[1],"timestamp":i[2]})
		return jsonify(ans),200
	else:
		return jsonify(),405

@app.route("/api/v1/rides/<rideId>",methods=["GET"])
def ride_details(rideId):
	if(request.method == 'GET'):
		temp = {'type':4, 'ride':int(rideId)}
		res = requests.post('http://34.230.153.167/api/v1/db/read', json = temp)
		r = res.json()['val']
		if(len(r)==0):
			return jsonify(),400
		else:
			return jsonify(r),200
	else:
		return jsonify(),405

@app.route("/api/v1/rides/<rideId>",methods=["POST"])
def join_ride(rideId):
	if(request.method == 'POST'):
		dic = request.get_json()
		username = dic["username"]
		temp = {'type':3, 'ride':int(rideId)}
		users = requests.post('http://34.230.153.167/api/v1/db/read', json = temp)
		val = users.json()
		if(len(val['val']) == 0):
			return jsonify(),400
		temp = {'type':1, 'user':username}
		user_list = requests.post('http://34.230.153.167/api/v1/db/read', json = temp)
		val = user_list.json()
		if(len(val['val']) == 0):
			return jsonify(),400
		t1 = (username,rideId)
		temp = {'type':4, 'ride':t1}
		resp = requests.post('http://34.230.153.167/api/v1/db/write', json = temp)
		val = user_list.json()['val']
		return jsonify(),200
	else:
		return jsonify(),405


@app.route("/api/v1/rides/<rideId>",methods=["DELETE"])
def delete_ride(rideId):
	if(request.method=="DELETE"):
		temp={'type':3,'ride':int(rideId)}
		res=requests.post('http://34.230.153.167/api/v1/db/read',json=temp)
		r=res.json()
		if(len(r['val'])==0):
			return jsonify(),400
		temp={"type":5,'ride':[rideId]}
		resp=requests.post('http://34.230.153.167/api/v1/db/write',json=temp)
		d=resp.json()
		if(d['val']== 400):
			return jsonify(),400
		else:
			return jsonify(),200
	else:
		return jsonify(),405


@app.route("/api/v1/db/write",methods=["POST","DELETE","PUT"])
def write():
	dic=request.get_json()
	if(dic["type"]==1):
		cur=mysql.connection.cursor()
		try:
			cur.execute("INSERT INTO users(username,password) VALUES (%s,%s)",(dic["value"][0],dic["value"][1]))
		except:
			return {'val':400}
		mysql.connection.commit()
		cur.close()
		return {'val':200}	
	if(dic["type"]==2):
		#print(dic["value"])
		cur=mysql.connection.cursor()
		#print(dic)
		sql="DELETE FROM users WHERE username=%s"
		val=[dic["value"],]
		cur.execute(sql,val)
		#return {'val':400}
		mysql.connection.commit()
		cur.close()
		return {'val':200}
	if(dic["type"]==3):
		cur=mysql.connection.cursor()
		try:
			cur.execute("INSERT INTO rides(rideId,username,_timestamp,source,destination) VALUES (%s,%s,%s,%s,%s)",(dic["ride"][0],dic["ride"][1],dic["ride"][2],dic["ride"][3],dic["ride"][4]))
		except:
			return {'val':400}
		mysql.connection.commit()
		cur.close()
		return {'val':200}
	if(dic["type"]==4):
		cur=mysql.connection.cursor()
		try:
			cur.execute("INSERT INTO urides values(%s, %s)",(dic['ride'][0], dic['ride'][1]))
		except:
			return {'val':400}
		mysql.connection.commit()
		cur.close()
		return {'val':200}
	if(dic["type"]==5):
		cur=mysql.connection.cursor()
		try:
			cur.execute("DELETE FROM rides WHERE rideId = %s",(dic['ride'][0],))
		except:
			return {'val':400}
		mysql.connection.commit()
		cur.close()
		return {'val':200}
			
@app.route("/api/v1/db/read",methods=["POST","GET"])
def read():
	dic=request.get_json()
	print(dic)
	if(dic["type"]==1):
		cur=mysql.connection.cursor()
		val=(dic["user"],)
		cur.execute("SELECT * FROM users WHERE username=%s",val)
		l = cur.fetchall()
		print(l)
		mysql.connection.commit()
		cur.close()
		return {"val":l}
	if(dic["type"]==2):
		cur=mysql.connection.cursor()
		val=(dic["ride"][0],dic["ride"][1])
		exe="SELECT * FROM rides WHERE source=%s AND destination=%s"
		cur.execute(exe,val)
		res = cur.fetchall()
		print(res)
		mysql.connection.commit()
		cur.close()
		return {"val":res}
	if(dic["type"] == 3):
		cur=mysql.connection.cursor()
		val=(dic["ride"],)
		exe="SELECT * FROM rides WHERE rideId=%s"
		cur.execute(exe,val)
		res = cur.fetchall()
		mysql.connection.commit()
		cur.close()
		return {"val":res}
	if(dic["type"]==4):
		users=[]
		cur=mysql.connection.cursor()
		val=(dic["ride"],)
		exe="SELECT * FROM rides WHERE rideId = %s"
		cur.execute(exe,val)
		res1 = cur.fetchall()
		print(res1)
		cur1=mysql.connection.cursor()
		val=(dic["ride"],)
		exe="SELECT username FROM urides WHERE rideId = %s"
		cur1.execute(exe,val)
		res2 = cur1.fetchall()
		for i in res2:
			users.append(i[0])
		if(len(res1)==0):
			return {'val':res1}
		ret={}
		ret["rideId"]=res1[0][0]
		ret["Created_by"]=res1[0][1]
		ret["users"]=users
		ret["Timestamp"]=res1[0][2]
		ret["source"]=res1[0][3]
		ret["destination"]=res1[0][4]
		return {'val':ret}
if __name__ =="__main__":
	app.run(debug=True)
