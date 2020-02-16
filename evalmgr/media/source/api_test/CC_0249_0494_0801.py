from flask import Flask,render_template,jsonify,request,abort
import csv
import os
import re
import enumeration
import time
import datetime
import pickle
import flask
import os.path
import requests

app=Flask(__name__)

c1=0
b={}

if(os.path.isfile("users.data")==False):

	f=open("users.data","wb")
	f.close()

	'''b["data"]={}

	b["file"]="users.data"

	q=request.post("http://127.0.0.1:5000/api/v1/db/write",json=b)
	'''


if(os.path.isfile("rides.data")==False):


	f=open("rides.data","wb")

	f.close()
'''
	b["data"]={}

	b["file"]="rides.data"

	q=request.post("http://127.0.0.1:5000/api/v1/db/write",json=b)
'''
"""

f=open("users.data","wb")

f.close()



f=open("rides.data","wb")

f.close()
"""


def authenticate(passwd):

    if len(passwd) != 40:

        return False

    try:

        temp = int(passwd, 16)

    except ValueError:

        return False

    return True



@app.route("/api/v1/users",methods=["PUT"])

def add_user():



	users={}

	temp=dict(request.get_json())
	b={}


	if request.method!="PUT":

		abort(405)



	else:

		if os.stat("users.data").st_size !=0:

			#f=open("users.data","rb")

			#users=pickle.load(f)

			#f.close()

			b["file"]="users.data"

			users1=requests.post("http://127.0.0.1:5000/api/v1/db/read",json=b)
			users=users1.json()



			if temp["username"] not in users.keys():

				if authenticate(temp["password"])==True:

					users[temp["username"]]=temp["password"]

					#f=open("users.data","wb")

					#pickle.dump(users,f)

					#f.close()

					b["data"]=users

					b["file"]="users.data"

					q=requests.post("http://127.0.0.1:5000/api/v1/db/write",json=b)

					return "",201

				else:

					abort(400,description="invalid password")

			else:

				abort(400,description="user already exists")

		else:

			if temp["username"] not in users.keys():

				if authenticate(temp["password"])==True:

					users[temp["username"]]=temp["password"]

					#f=open("users.data","wb")

					#pickle.dump(users,f)

					#f.close()

					b["data"]=users

					b["file"]="users.data"

					q=requests.post("http://127.0.0.1:5000/api/v1/db/write",json=b)


					#status_code = flask.Response(status=201)

					return "",201

				else:

					abort(400,description="invalid password")

			else:

				abort(400,description="user already exists")

				"""Status Codes"""




@app.route("/api/v1/users/<username>",methods=["DELETE"])

def remove_user(username):

	b=dict()

	if request.method!="DELETE":

		abort(405)

	else:

		temp=dict()

		users=dict()

		rides=[]

		if os.stat("rides.data").st_size!=0:

			#f=open("rides.data","rb")

			#rides=pickle.load(f)

			#f.close()

			b["file"]="rides.data"

			rides1=requests.post("http://127.0.0.1:5000/api/v1/db/read",json=b)
			rides=rides1.json()
			for i in range(0,len(rides)):

				if rides[i]["created_by"]==username:

					del rides[i]

			for i in range(0,len(rides)):

				for j in range(0,len(rides[i]["users"])):

					if username==rides[i]["users"][j]:

						del rides[i]["users"][j]

		if os.stat("users.data").st_size!=0:

			#f=open("users.data","rb")

			#users=pickle.load(f)

			#f.close()

			b["file"]="users.data"

			users1=requests.post("http://127.0.0.1:5000/api/v1/db/read",json=b)
			users=users1.json()
			if username in users:

				users.pop(username)

				#f=open("users.data","wb")

				#pickle.dump(users,f)

				#f.close()

				b["data"]=users

				b["file"]="users.data"

				q=requests.post("http://127.0.0.1:5000/api/v1/db/write",json=b)

				return "",200

			else:

				abort(400,description="user doesnt exist")

				"""Status Codes"""

		else:

			abort(400,description="no users")



@app.route("/api/v1/rides",methods=["POST"])

def create_ride():
	b={}
	c=0
	flag=0
	if request.method!="POST":

		abort(405)



	else:

		temp=dict(request.get_json())

		temp["users"]=[]

		users=dict()

		rides=[]

		if os.stat("rides.data").st_size!=0:

			#f=open("rides.data","rb")

			#rides=pickle.load(f)

			#f.close()

			b["file"]="rides.data"

			rides1=requests.post("http://127.0.0.1:5000/api/v1/db/read",json=b)
			rides=rides1.json()
		if os.stat("users.data").st_size!=0:

			#f=open("users.data","rb")

			#users=pickle.load(f)

			#f.close()

			b["file"]="users.data"

			users1=requests.post("http://127.0.0.1:5000/api/v1/db/read",json=b)
			users=users1.json()

		#pattern = re.compile("((0[1-9]|[12][0-9]|3[01])-(0[13578]|1[02])-(18|19|20)[0-9]{2})|(0[1-9]|[12][0-9]|30)-(0[469]|11)-(18|19|20)[0-9]{2}|(0[1-9]|1[0-9]|2[0-8])-(02)-(18|19|20)[0-9]{2}|29-(02)-(((18|19|20)(04|08|[2468][048]|[13579][26]))|2000) [0-5][0-9]:[0-5][0-9]:(2[0-3]|[01][0-9])")

		#pattern = re.compile("^([1-9]|([012][0-9])|(3[01]))-([0]{0,1}[1-9]|1[012])-\d\d\d\d(20|21|22|23|[0-1]?\d):[0-5]?\d:[0-5]?\d$")

		pattern=re.search("((0[1-9]|[12][0-9]|3[01])-(0[13578]|1[02])-(18|19|20)[0-9]{2})|(0[1-9]|[12][0-9]|30)-(0[469]|11)-(18|19|20)[0-9]{2}|(0[1-9]|1[0-9]|2[0-8])-(02)-(18|19|20)[0-9]{2}|29-(02)-(((18|19|20)(04|08|[2468][048]|[13579][26]))|2000) [0-5][0-9]:[0-5][0-9]:(2[0-3]|[01][0-9])",temp["timestamp"])

		for area in enumeration.Area:

			if temp["source"] == str(area.value):

				c=c+1

		for area in enumeration.Area:

			if temp["destination"] == str(area.value):

				c=c+1

		if(len(rides)!=0):
			o=len(rides)-1
			w=rides[o]["rideId"]
			temp["rideId"]=w+1

		else:
			temp["rideId"]=1

		if temp["created_by"] in users.keys():

			if pattern!=None:

				if temp["source"]!=temp["destination"]:

					if c==2:

						if(len(rides)!=0):

							for cur in rides:

								if(temp["rideId"]==cur["rideId"]):

									flag=1

								else:

									flag=0



							if(flag!=1):	

								rides.append(temp)

								#f=open("rides.data","wb")

								#pickle.dump(rides,f)

								#f.close()

								b["data"]=rides

								b["file"]="rides.data"

								q=requests.post("http://127.0.0.1:5000/api/v1/db/write",json=b)


								#status_code = flask.Response(status=201)

								#return status_code

								return "",201

							else:

								abort(400,description="cant have same rideId")



						else:

							rides.append(temp)

							#f=open("rides.data","wb")

							#pickle.dump(rides,f)

							#f.close()

							b["data"]=rides

							b["file"]="rides.data"

							q=requests.post("http://127.0.0.1:5000/api/v1/db/write",json=b)


							#status_code = flask.Response(status=201)

							#return status_code

							return "",201
					else:
						abort(400,description="invalid source or destination")
				else:
					abort(400,description="same source and destination")
			else:
				abort(400,description="invalid timestamp")
		else:
			abort(400,description="user doesnt exist")


@app.route("/api/v1/rides",methods=["GET"])

def upcoming_rides():
	b={}

	if request.method!="GET":
		abort(405)

	else:

		destination = request.args.get('destination')

		source = request.args.get('source')

		c=0

		for area in enumeration.Area:

			if source == str(area.value):

				c=c+1

		for area in enumeration.Area:

			if destination == str(area.value):

				c=c+1

		if c==2:

			temp1=[]

			temp=dict()

			rides=[]

			users={}

			if os.stat("rides.data").st_size!=0:

				#f=open("rides.data","rb")

				#rides=pickle.load(f)

				#f.close()

				b["file"]="rides.data"

				rides1=requests.post("http://127.0.0.1:5000/api/v1/db/read",json=b)
				rides=rides1.json()

			if os.stat("users.data").st_size!=0:

				#f=open("users.data","rb")

				#users=pickle.load(f)

				#f.close()

				b["file"]="users.data"

				users1=requests.post("http://127.0.0.1:5000/api/v1/db/read",json=b)
				users=users1.json()

			for i in range(0,len(rides)):

				temp={}
				if rides[i]["source"]==source and rides[i]["destination"]==destination:

					if rides[i]["created_by"] in users.keys():

						ts = time.time()

						st = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y:%S-%M-%H')

						datetime_object1 = datetime.datetime.strptime(st, '%d-%m-%Y:%S-%M-%H')

						st1=rides[i]["timestamp"]

						datetime_object = datetime.datetime.strptime(st1, '%d-%m-%Y:%S-%M-%H')

						if datetime_object>datetime_object1:

							temp["rideId"]=rides[i]["rideId"]

							temp["username"]=rides[i]["created_by"]

							temp["timestamp"]=rides[i]["timestamp"]

							temp1.append(temp)

			if len(temp1)==0:

				return '',204

			else:

				return jsonify(temp1),200

		else:

			abort(400,description="incorrect source or destination")



@app.route("/api/v1/rides/<rideId>",methods=["GET"])

def ride_details(rideId):
	b=dict()


	if request.method!="GET":

		abort(405)

	else:


		c=0
		l={}

		rides=[]

		if os.stat("rides.data").st_size!=0:

			#f=open("rides.data","rb")

			#rides=pickle.load(f)

			#f.close()

			b["file"]="rides.data"

			rides1=requests.post("http://127.0.0.1:5000/api/v1/db/read",json=b)
			rides=rides1.json()
			#return jsonify(str(rides[0]["rideId"])==str(rideId))
			for i in rides:

				if str(rideId)==str(i["rideId"]):
					c=c+1

					return jsonify(i),200


		if c==0:

			return "",204


@app.route("/api/v1/rides/<rideId>",methods=["POST"])

def join_existing_ride(rideId):
	b={}


	if request.method!="POST":

		abort(405)

	else:

		rides=[]

		users=dict()

		temp=dict(request.get_json())

		if os.stat("users.data").st_size!=0:

			#f=open("users.data","rb")

			#users=pickle.load(f)

			#f.close()

			b["file"]="users.data"

			users1=requests.post("http://127.0.0.1:5000/api/v1/db/read",json=b)
			users=users1.json()

		if os.stat("rides.data").st_size!=0:

			#f=open("rides.data","rb")

			#rides=pickle.load(f)

			#f.close()

			b["file"]="rides.data"

			rides1=requests.post("http://127.0.0.1:5000/api/v1/db/read",json=b)
			rides=rides1.json()

		for i in rides:

			if str(rideId)==str(i["rideId"]):

				if temp["username"] in users.keys():

					if temp["username"] not in i["users"]:

						i["users"].append(temp["username"])

						#f=open("rides.data","wb")

						#pickle.dump(rides,f)

						#f.close()

						b["data"]=rides

						b["file"]="rides.data"

						q=requests.post("http://127.0.0.1:5000/api/v1/db/write",json=b)



						#status_code = flask.Response(status=201)

						#return status_code

						return "",200

					else:

						abort(400,description="users already joined ride")
				else:
					abort(400, description="user doesnt exist")
			else:
				return "",204


	

@app.route("/api/v1/rides/<rideId>",methods=["DELETE"])

def delete_ride(rideId):
	b={}

	if request.method!="DELETE":

		abort(405)

	else:

		flag=0

		if os.stat("users.data").st_size!=0:

			#f=open("users.data","rb")

			#users=pickle.load(f)

			#f.close()

			b["file"]="users.data"

			users1=requests.post("http://127.0.0.1:5000/api/v1/db/read",json=b)
			users=users1.json()


		if os.stat("rides.data").st_size!=0:

			#f=open("rides.data","rb")

			#rides=pickle.load(f)

			#f.close()

			b["file"]="rides.data"

			rides1=requests.post("http://127.0.0.1:5000/api/v1/db/read",json=b)
			rides=rides1.json()

		for i in range(0,len(rides)):

			if str(rideId)==str(rides[i]["rideId"]):

				flag=1

				j=i

				break

			else:

				flag=0



		if(len(rides)==0):

			flag=0



		if(flag==1):

			del rides[j]

			#f=open("rides.data","wb")

			#pickle.dump(rides,f)

			#f.close()

			b["data"]=rides

			b["file"]="rides.data"

			q=requests.post("http://127.0.0.1:5000/api/v1/db/write",json=b)

			return "",200

		else:

			abort(400,description="ride doesnt exist")


@app.route("/api/v1/db/write",methods=["POST"])

def write():
	b=dict(request.get_json())
	f=open(b["file"],"wb")
	pickle.dump(b["data"],f)
	f.close()
	return jsonify({})

@app.route("/api/v1/db/read",methods=["POST"])

def read():
	b=dict(request.get_json())
	f=open(b["file"],"rb")
	a=pickle.load(f)
	f.close()
	return jsonify(a)





if __name__ == '__main__':	

	app.debug=True
	app.run(host="0.0.0.0",port=5000)