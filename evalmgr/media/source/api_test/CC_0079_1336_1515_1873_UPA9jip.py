from flask import Flask,request,jsonify,abort
from pymongo import MongoClient,errors
import requests as send_request
import json
from flask import make_response
from datetime import datetime
import pandas as pd

df = pd.read_csv("AreaNameEnum.csv")
area_dict = dict()

for i in range(len(df)):
	area_dict[df['Area No'][i]]=df['Area Name'][i]

app = Flask(__name__)
client = MongoClient(port=27017)

db = client.rideshare

empty_response = app.make_response('') #default 200 OK send this response for sending 200 OK



"""
1.Add Users

POST Request
Body Format
{
	"username":"username",
	"password":"password"

}

"""
hashset = set(['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f'])
@app.route("/api/v1/users",methods=["PUT"])
def add_users():
	print("recieved a request to add user")
	user_details = request.get_json()
	data_to_send = dict()
	data_to_send['operation'] = 'insert'
	data_to_send['table'] ='users'
	data_to_send['data'] = user_details
	print(user_details)

	try:
		print("here")
		if(len(user_details['password'])==40):
			if((hashset & set(user_details['password'])) != set(user_details['password'])):
				print("Password not in SHA1")
				abort(400)
		else:
			print("Password not in 40 length")
			abort(400)
	except:
			abort(400)
	
	print("Generating Request")
	print(data_to_send)
	response_recieved = send_request.post('http://127.0.0.1:5000/api/v1/write',json=data_to_send)
	print("Response Recieved")
	
	response_201 = make_response('{}',201)
	if(response_recieved.status_code == 200):
		return response_201
	else:
		abort(400)

"""
2. Remove a user form db
"""	
@app.route("/api/v1/users/<username>",methods=["DELETE"])
def delete_users(username):
	print("Recieved request to delete the user with username:",username)

	data_to_send = dict()
	data_to_send['table'] = 'users'
	data_to_send['operation'] = 'delete'
	data_to_send['data'] = {"username":username}

	response_recieved = send_request.post('http://127.0.0.1:5000/api/v1/write',json = data_to_send)


	response_400 = make_response('{}',400)
	if(response_recieved.status_code  == 405):
		return response_400
	else:
		
		return empty_response	

"""
3. Add Ride
POST Request
body Format
{
	"created by":"username"
	"timestamp": "D/m/y:s/m/h"
	"source": "source"
	"destination":"destination"

5. List all upcoming rides for a given source and destination
}
"""

@app.route("/api/v1/rides",methods = ["POST","GET"])
def add_ride():
	response_400 = make_response('{}',400)
	if request.method == 'POST':
		print("recieved a request to add ride")
		ride_details = request.get_json()
		try:
			ride_details['source'] = area_dict[int(ride_details['source'])]
			ride_details['destination'] = area_dict[int(ride_details['destination'])]
		except KeyError:
			return response_400
		data_to_send = {}
		data_to_send['table'] = 'users'
		data_to_send['conditions'] = {"username":ride_details['created_by']}

		response_received = send_request.post('http://127.0.0.1:5000/api/v1/read',json = data_to_send)

	
		if(response_received.status_code == 204):
			return response_400
		else:
			response_received = send_request.post('http://127.0.0.1:5000/api/v1/read',json = {"table":"rides","conditions":{}})
			max_rideID = -1
			if(response_received.status_code != 204):
				data_recieved = response_received.json()
				for row in data_recieved:
					if(int(row['rideId']) > max_rideID ):
						max_rideID = int(row['rideId'])
			rideId = max_rideID + 1
			ride_details['rideId'] = rideId
			ride_details['users'] = []
			# ride_details['users'] = [ride_details["created_by"]]
			data_send = {}
			data_send['operation'] = 'insert'
			data_send['data'] = ride_details
			data_send['table'] = 'rides'
			print(data_send)
			response_recieved = send_request.post('http://127.0.0.1:5000/api/v1/write',json=data_send)

			if(response_received.status_code == 200):
				response_201 = make_response('{}', 201)
				return response_201
	else:
		print('received a request to list rides')
		source = request.args.get('source')
		destination = request.args.get('destination')
		try:
			source = area_dict[int(source)]
			destination = area_dict[int(destination)]
		except :
			return response_400
		response_400 = make_response('{}',400)
		response_204 = make_response('{}',204)
		

		if(source == None or destination == None):
			return response_400

		data_to_send = {}
		data_to_send['table'] = 'rides'
		data_to_send['conditions'] = {'source': source, 'destination': destination}

		response_received = send_request.post('http://127.0.0.1:5000/api/v1/read',json = data_to_send)
	
		response_400 = make_response('{}',400)
		response_204 = make_response('{}',204)
		if(response_received.status_code == 204):
			return response_204
		# assumed that the response of above returns a array of json objects which just need to be returned.
		else:
			data = response_received.json()			
			response_data = []
			print(data)
			for i in data:
				temp = dict()
				print(i)
				temp['rideId'] = i['rideId']
				temp['username'] = i['created_by']
				temp['timestamp'] = i['timestamp']

				time_now = datetime.now()
				time_created = datetime.strptime(temp['timestamp'],'%d-%m-%Y:%H-%M-%S')

				if(time_created >= time_now):						
					response_data.append(temp)
			
			return jsonify(response_data)
	

"""
6. update a given ride
request body:
{
	username: username
}
"""

@app.route("/api/v1/rides/<rideId>",methods = ["DELETE","POST"])
def delete_ride(rideId):
	response_400 = make_response('{}',400)

	if request.method == "POST":
		flag=1
		response_data = request.get_json()
		data_to_send = dict()
		data_to_send['table'] = 'rides'
		data_to_send['conditions'] = {"rideId":int(rideId)}
		response_received = send_request.post('http://127.0.0.1:5000/api/v1/read',json = data_to_send)
		
		if(response_received.status_code == 204):
			flag =0

		data_to_send = dict()
		data_to_send['table'] = 'users'
		data_to_send['conditions'] = {"username":response_data['username']}

		response_received = send_request.post('http://127.0.0.1:5000/api/v1/read',json = data_to_send)

		if(response_received.status_code == 204):
			flag =0

		if(flag==0):
			return response_400	
		else:
			data_to_send = dict()
			data_to_send['table'] = 'rides'
			data_to_send['conditions'] = {"rideId":int(rideId),"users":response_data["username"]}
			response_received = send_request.post('http://127.0.0.1:5000/api/v1/read',json = data_to_send)
			response_400 = make_response('{}',400)
			if(response_received.status_code == 200):
				return response_400
			try:
				db.rides.update(
					{"rideId" : int(rideId)},
					{"$push": {"users": response_data["username"]}}
					)
				response_data = make_response('{}', 200)
				return response_data
			except:
				response_data = make_response('{}', 400)
				print("yo-yo")
				return response_data
	else:
		print("Recieved request to delete the ride with rideId :",rideId)

		data_to_send = dict()
		data_to_send['table'] = 'rides'
		data_to_send['operation'] = 'delete'
		data_to_send['data'] = {"rideId":int(rideId)}

		response_recieved = send_request.post('http://127.0.0.1:5000/api/v1/write',json = data_to_send)

		if(response_recieved.status_code  == 405):
			abort(400)
		else:
			return empty_response	


@app.route("/api/v1/rides/<rideId>",methods = ["GET"])
def details_of_ride(rideId):

	print("Received request to display all the details of ride with ride ID :",rideId)

	data_to_send = dict()
	try:
		data_to_send['table'] = 'rides'
		data_to_send['conditions'] = {"rideId":int(rideId)}
	except:
		abort(400)
	response_recieved = send_request.post('http://127.0.0.1:5000/api/v1/read',json = data_to_send)

	#print(response_recieved.__dict__
	data_recieved = response_recieved._content

	response_204 = make_response('{}',204)

	if(response_recieved.status_code == 204):
		return response_204
	elif(response_recieved.status_code == 200):
		return data_recieved
	else:
		abort(405)	
"""
8.Write a DB

POST Request
Body Format FOR insert update
{
	"operation":"insert","update"
	"data":data  // A row in JSON format
	"table" :"tablename" 
}

Body Format
{
	"operation":"update"
	"data":"data_to_Be updated"
	"table":"table_name"
	"filter":"filter for documents"


}
"""
@app.route("/api/v1/write",methods=["POST"])
def write_db():	
	json_data = request.get_json()
	try:
		collection_name = json_data['table']
		document =  json_data['data']
		if(json_data['operation']=="update"):
			filter_data = json_data['filter']
	except KeyError:
		abort(400) # Recieved Data is not valid  - BAD Request

	if(json_data['operation']=="insert"):
		success_code = insert_data(collection_name,document)
	elif(json_data['operation']=="delete"):
		success_code = delete_data(collection_name,document)
	elif(json_data['operation']=="update"):
		success_code = update_data(collection_name,document,filter_data)
	else:
		abort(400) #Operation not supported - BAD Request
	if(success_code==1):
		return empty_response
	else:
		abort(405) #Error Encountered while Performing DB operations - Method Not Allowed

def update_data(collection_name,document,filter_data):
	print("Updating based on",document,"for ONE row satisfying",filter_data)
	try:
		db[collection_name].update_one(filter_data,document)
		return 1
	except:
		return 0


def insert_data(collection_name,document):
	print("Inserting",document,"into collection",collection_name)
	try:
		db[collection_name].insert_one(document)
		return 1
	except errors.DuplicateKeyError:
		print("DuplicateKeyError")
		return 0

def delete_data(collection_name,document):
	print("Deleting",document,"from collection",collection_name)
	print("Searching",document,"from collection",collection_name)
	search_res = db[collection_name].find_one(document)
	#print(document)

	print(search_res)
	if(search_res==None):
		print("here")
		return 0
	try:
		db[collection_name].delete_one(document)
		print("Operation Done")
		return 1
	except:
		return 0



"""
9. Read from DB
POST Request
Body Format
{
	"table":"tablename",
	"conditions":{column:value , ...}
}

"""
@app.route("/api/v1/read",methods=["POST"])
def read_db():
	data_request = request.get_json()
	try:
		collection = data_request['table']
		condition = data_request['conditions']
	except KeyError:
		abort(400)
	cursor = db[collection].find(condition)
	if((cursor.count())>1):
		print("WARNING :The Query matches",cursor.count(),"documents")
	elif(cursor.count()==0):
		print("WARNING : 0 results matched")
		respone_204 = make_response('',204)
		return respone_204

	res = list()
	for row in cursor:
		row.pop("_id")
		res.append(row)
	return jsonify(res)
	# res = cursor[0]                      
	# res.pop("_id")
	# return jsonify(res)



if __name__ == '__main__':	
	app.debug=True
	app.run(threaded=True)  #Threaded to have Mutliple concurrent requests
