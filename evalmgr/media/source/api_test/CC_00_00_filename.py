import re
import json
import requests
import pandas as pd
from datetime import datetime
from flask import Flask, request, jsonify, abort, Response

app = Flask(__name__)

# Working
# Add a new user to the database
@app.route('/api/v1/users', methods=['PUT'])
def add_user():
	# Obtain the data in json format
	data = request.get_json()
	keys = data.keys()

	# Verify the format of the data
	if 'username' not in keys or 'password' not in keys:
		# Json is invalid
		return jsonify({'error':'wrong json format'}), 400

	# Obtain the username and password form the json
	username = str(data['username'])
	password = str(data['password'])

	# Verify the password format
	if len(password) is not 40 or not re.match(re.compile(r'\b[0-9a-f]{40}\b'), password):
		# Password is in wrong format
		return jsonify({'error':'wrong password format'}), 400

	# Check if username already exists in the database
	response = requests.post(url='http://172.31.91.111:8080/api/v1/db/read', json={'api':'add_user', 'username':username})
	if (response.json())['user_exists']:
		# User already exists in the database
		return jsonify({"error":"user already exists"}), 400

	# Insert the user into the database
	response = requests.post(url='http://172.31.91.111:8080/api/v1/db/write', json={'api':'add_user', 'username':username, 'password':password})
	return jsonify(response.json()), 201

# Working
# Delete an existing user from the database
@app.route('/api/v1/users/<string:username>', methods=['DELETE'])
def delete_user(username):
	# Check if user exists in the database
	response = requests.post(url='http://172.31.91.111:8080/api/v1/db/read', json={'api':'delete_user', 'username':username})
	if not (response.json())['user_exists']:
		# User not in the database
		return jsonify({'error':'user not in database'}), 400

	# Remove the user from the database
	response = requests.post(url='http://172.31.91.111:8080/api/v1/db/write', json={'api':'delete_user', 'username':username})
	return jsonify(response.json()), 200

# Working
# Create a new ride in the database
@app.route('/api/v1/rides', methods=['POST'])
def new_ride():
	# Obtain the data in json format
	data = request.get_json()
	keys = data.keys()

	# Verify the format of the data
	if 'created_by' not in keys or 'timestamp' not in keys or 'source' not in keys or 'destination' not in keys:
		return jsonify({'error':'wrong json format'}), 400

	# Obtain the ride information form the json
	created_by = str(data['created_by'])
	timestamp = str(data['timestamp'])
	source = data['source']
	destination = data['destination']

	# Verify the source and destination for validity
	if source == destination:
		return jsonify({'error':'source is same as destination'}), 400

	# Verify the timestamp
	try:
		datetime.strptime(timestamp, '%d-%m-%Y:%S-%M-%H')
	except ValueError:
		return jsonify({'error':'invalid timestamp'}), 400

	# Verify the format of the timestamp
	date, month, year = (timestamp.split(':')[0]).split('-')
	second, minute, hour = (timestamp.split(':')[1]).split('-')
	if len(date) is not 2 or len(month) is not 2 or len(year) is not 4 or len(second) is not 2 or len(minute) is not 2 or len(hour) is not 2:
		return jsonify({'error':'wrong timestamp length/format'}), 400

	# Check the timestamp to verify that the ride is scheduled in the future
	ride_time = datetime.strptime(timestamp, '%d-%m-%Y:%S-%M-%H')
	current_time = datetime.now()
	if (ride_time-current_time).total_seconds() < 0:
		return jsonify({'error':'time is in the past'}), 400

	# Validate the source, destination and username
	response = requests.post(url='http://172.31.91.111:8080/api/v1/db/read', json={'api':'new_ride', 'username':created_by, 'source':source, 'destination':destination})
	if not (response.json())['source_exists']:
		return jsonify({'error':'source not in database'}), 400
	if not (response.json())['destination_exists']:
		return jsonify({'error':'destination not in database'}), 400
	if not (response.json())['user_exists']:
		return jsonify({'error':'user not in database'}), 400
	
	# Insert ride details into the database
	response = requests.post(url='http://172.31.91.111:8080/api/v1/db/write', json={'api':'new_ride', 'created_by':created_by, 'timestamp':timestamp, 'source':source, 'destination':destination})
	return jsonify(response.json()), 201

# Working
# List all the rides from a given source to given destination
@app.route('/api/v1/rides', methods=['GET'])
def list_rides():
	# Ontain the data
	source = request.args.get('source')
	destination = request.args.get('destination')
	none_type = request.args.get('none_type')
	
	# Check if source and destination is present
	if source is none_type or destination is none_type or (not source.isdigit()) or (not destination.isdigit()):
		return jsonify({'error':'source or destination is missing'}), 400

	# Obtain the source and the destination
	source = int(request.args.get('source'))
	destination = int(request.args.get('destination'))

	# Read the database for the rides and return 204 if not ride found
	response = requests.post(url='http://172.31.91.111:8080/api/v1/db/read', json={'api':'list_rides', 'source':source, 'destination':destination})
	if not response.json():
		return jsonify(), 204

	return jsonify(response.json()), 200

# Working
# Return the details of a particular ride
@app.route('/api/v1/rides/<string:rideId>', methods=['GET'])
def get_ride_details(rideId):
	# Validate the format of the rideId
	if not rideId.isdigit():
		return jsonify({'error': 'rideId has atleast one non numerical character'}), 400

	# Read the database for the ride details
	response = requests.post(url='http://172.31.91.111:8080/api/v1/db/read', json={'api':'get_ride_details', 'rideId':rideId})

	# If there is not ride with the specified rideId
	if not response.json():
		return jsonify({}), 400

	return jsonify(response.json()), 200

# Working
# Adding a user to an existing ride
@app.route('/api/v1/rides/<string:rideId>', methods=['POST'])
def join_ride(rideId):
	# Validate the format of the rideId
	if not rideId.isdigit():
		return jsonify({'error': 'rideId has atleast one non numerical character'}), 400

	# Obtain the data in json format
	data = request.get_json()
	keys = data.keys()

	# Verify the format of the data
	if 'username' not in keys:
		# Json is invalid
		return jsonify({'error':'wrong json format'}), 400

	# Obtain the username from the json
	username = str(data['username'])

	# Read the database to check if user exists, ride exists and if it is expired or not
	response = requests.post(url='http://172.31.91.111:8080/api/v1/db/read', json={'api':'join_ride', 'username':username, 'rideId':rideId})
	if not (response.json())['user_exists']:
		return jsonify({'error':'user not in database'}), 400
	if not (response.json())['rideId_exists']:
		return jsonify({'error':'rideId not in database'}), 400
	if not (response.json())['ride_valid']:
		return jsonify({'error':'ride is expired'}), 400
	if not (response.json())['can_add_rider']:
		return jsonify({'error':'rider already in ride'}), 400

	# Add new user to the ride
	response = requests.post(url='http://172.31.91.111:8080/api/v1/db/write', json={'api':'join_ride', 'username':username, 'rideId':rideId})
	return jsonify(response.json()), 201

# Working
# Deleting a ride from the database
@app.route('/api/v1/rides/<string:rideId>', methods=['DELETE'])
def delete_ride(rideId):
	# Validate the format of the rideId
	if not rideId.isdigit():
		return jsonify({'error': 'rideId has atleast one non numerical character'}), 400

	# Check if the rideId exists in the database and if not return error
	response = requests.post(url='http://172.31.91.111:8080/api/v1/db/read', json={'api':'delete_ride', 'rideId':rideId})
	if not (response.json())['rideId_exists']:
		return jsonify({'error':'rideId not in the database'}), 400

	# Remove ride from the database
	response = requests.post(url='http://172.31.91.111:8080/api/v1/db/write', json={'api':'delete_ride', 'rideId':rideId})
	return jsonify(response.json()), 200

@app.route('/api/v1/db/write', methods=['POST'])
def db_write():
	# Extract the json data
	data = request.get_json()

	# If the calling API is add_user API
	if data['api'] == 'add_user':
		username = data['username']
		password = data['password']

		# Add the user to the database
		users_data = pd.read_csv('users.csv')
		users_data = users_data.append({'username': username, 'password': password}, ignore_index=True)
		users_data.to_csv('users.csv', index=False)

		return jsonify({}), 201

	# If the calling API is delete_user API
	if data['api'] == 'delete_user':
		username = data['username']

		# Remove user form the user database
		users_data = pd.read_csv('users.csv')
		users_data = users_data[users_data.username != username]
		users_data.to_csv('users.csv', index=False)

		# Remove user data from rides database
		rides_data = pd.read_csv('rides.csv')
		rides_data = rides_data[rides_data.created_by != username]
		riders_data = list(rides_data.riders)
		for index in range(len(riders_data)):
			riders = riders_data[index]
			riders = riders.split(',')
			if username in riders:
				riders.remove(username)
			riders_data[index] = ','.join(riders)
		rides_data.riders = riders_data
		rides_data.to_csv('rides.csv', index=False)

		return jsonify({}), 200

	# If the calling API is new_ride API
	if data['api'] == 'new_ride':
		created_by = data['created_by']
		timestamp = data['timestamp']
		source = data['source']
		destination = data['destination']

		# Read the latest rideId
		rides_count = open('rides_count.txt','r')
		last_rideId = rides_count.read()
		rides_count.close()

		# Update the latest rideId to generate new rideId
		current_rideId = int(last_rideId) + 1
		rides_count = open('rides_count.txt','w')
		rides_count.write(str(current_rideId))
		rides_count.close()

		# Add the ride detials to the database
		rides_data = pd.read_csv('rides.csv')
		rides_data = rides_data.append({'rideId': current_rideId, 'created_by': created_by, 'riders': created_by, 'timestamp': timestamp, 'source': source, 'destination': destination}, ignore_index=True)
		rides_data.to_csv('rides.csv', index=False)

		return jsonify({}), 201

	if data['api'] == 'join_ride':
		rideId = data['rideId']
		username = data['username']

		# Add user to the ride
		rides_data = pd.read_csv('rides.csv')
		for index in range(len(rides_data)):
			if int((rides_data.rideId)[index]) is int(rideId):
				riders_list = rides_data.loc[index, 'riders'].split(',')
				if username not in riders_list:
					riders_list.append(username)
				rides_data.loc[index, 'riders'] = ','.join(riders_list)
				rides_data.to_csv('rides.csv', index=False)
				return jsonify({}), 200

	if data['api'] == 'delete_ride':
		rideId = data['rideId']

		# Delete the ride from the database
		rides_data = pd.read_csv('rides.csv')
		initial_number_of_rides = len(rides_data)
		rides_data = rides_data[rides_data.rideId != int(rideId)]
		final_number_of_rides = len(rides_data)
		rides_data.to_csv('rides.csv', index=False)

		return jsonify({}), 200

@app.route('/api/v1/db/read', methods=['POST'])
def db_read():
	# Extract the json data
	data = request.get_json()

	# If the calling API is add_user API
	if data['api'] == 'add_user':
		return_data = dict()

		# Extract users from the users database
		existing_users = pd.read_csv('users.csv')['username']
		existing_users = list(map(str, existing_users))

		# Check if user exists in the database
		if data['username'] in list(existing_users):
			return_data['user_exists'] = True
		else:
			return_data['user_exists'] = False

		return jsonify(return_data), 200

	# If the calling API is delete_user API
	if data['api'] == 'delete_user':
		return_data = dict()

		# Extract users from the users database
		existing_users = pd.read_csv('users.csv')['username']
		existing_users = list(map(str, existing_users))

		# Check if user exists in the database
		if data['username'] in list(existing_users):
			return_data['user_exists'] = True
		else:
			return_data['user_exists'] = False

		return jsonify(return_data), 200

	# If the calling API is new_ride API
	if data['api'] == 'new_ride':
		return_data = dict()

		# Extract the AreaNameEnum from database
		area_name_enum = pd.read_csv('AreaNameEnum.csv')['Area No']

		# Check if source exists in the database
		if data['source'] in list(area_name_enum):
			return_data['source_exists'] = True
		else:
			return_data['source_exists'] = False

		# Check if the destination exists in the database
		if data['destination'] in list(area_name_enum):
			return_data['destination_exists'] = True
		else:
			return_data['destination_exists'] = False

		# Extract users from the users database
		existing_users = pd.read_csv('users.csv')['username']
		existing_users = list(map(str, existing_users))

		# Check if user exist in the database
		if data['username'] in list(existing_users):
			return_data['user_exists'] = True
		else:
			return_data['user_exists'] = False

		return jsonify(return_data), 200

	# If the calling API is list_rides API
	if data['api'] == 'list_rides':
		# Extract the source and the destination
		source = data['source']
		destination = data['destination']

		# Validate the source and destination
		area_name_enum = pd.read_csv('AreaNameEnum.csv')['Area No']
		if source not in area_name_enum or destination not in area_name_enum:
			return jsonify({'error':'source or destination not in database'}), 400

		# Get the list of all the rides from database from source to destination
		rides_data = pd.read_csv('rides.csv')
		rides_data = rides_data[rides_data.source == source]
		rides_data = rides_data[rides_data.destination == destination]

		# Extract the rides data from the dataframe
		rides_Id = list(rides_data.rideId)
		rides_Id = list(map(str, rides_Id))
		rides_created_by = list(rides_data.created_by)
		rides_created_by = list(map(str, rides_created_by))
		rides_timestamp = list(rides_data.timestamp)
		rides_timestamp = list(map(str, rides_timestamp))
		rides_data_returned = []

		# Get current time
		date_time = datetime.now()

		# Create teh list of ride details to be returned
		for index in range(len(rides_data)):
			ride_date_time = datetime.strptime(rides_timestamp[index], '%d-%m-%Y:%S-%M-%H')

			# Add ride data to list if the ride is scheduled in the future
			if (ride_date_time-date_time).total_seconds() > 0:
				temp_dict = {'rideId': rides_Id[index], 'username': rides_created_by[index], 'timestamp': rides_timestamp[index]}
				rides_data_returned.append(temp_dict)

		return jsonify(rides_data_returned), 200

	# If the calling API is get_ride_details API
	if data['api'] == 'get_ride_details':
		# Access the rides database
		rides_data = pd.read_csv('rides.csv')
		rides_Id = list(rides_data.rideId)
		rides_Id = list(map(str, rides_Id))

		# If the rideId is not in the database
		if data['rideId'] not in rides_Id:
			return jsonify({}), 200

		# Get the ride with the given rideId
		rides_data = rides_data[rides_data.rideId == int(data['rideId'])]
		ride_details = dict()
		ride_details['rideId'] = str(list(rides_data.rideId)[0])
		ride_details['created_by'] = str(list(rides_data.created_by)[0])
		ride_details['users'] = ((list(rides_data.riders)[0]).split(','))
		ride_details['users'].remove(ride_details['created_by'])
		ride_details['timestamp'] = str(list(rides_data.timestamp)[0])
		ride_details['source'] = str(list(rides_data.source)[0])
		ride_details['destination'] = str(list(rides_data.destination)[0])

		return jsonify(ride_details), 200

	# If the calling API is join_ride API
	if data['api'] == 'join_ride':
		return_data = dict()

		# Extract users from the users database
		existing_users = pd.read_csv('users.csv')['username']
		existing_users = list(map(str, existing_users))

		# Check if user exist in the database
		if data['username'] in list(existing_users):
			return_data['user_exists'] = True
		else:
			return_data['user_exists'] = False

		# Access the rides database
		rides_data = pd.read_csv('rides.csv')

		# Extract the rideIds from the database
		rides_Id = list(rides_data.rideId)
		rides_Id = list(map(str, rides_Id))

		# If the rideId is not in the database
		if data['rideId'] in list(rides_Id):
			return_data['rideId_exists'] = True
		else:
			return_data['rideId_exists'] = False

		# Check if the ride is still valid
		if return_data['rideId_exists']:
			rides_data = rides_data[rides_data.rideId == int(data['rideId'])]
			current_time = datetime.now()
			ride_time = datetime.strptime(list(rides_data.timestamp)[0], '%d-%m-%Y:%S-%M-%H')
			if (ride_time-current_time).total_seconds() > 0:
				return_data['ride_valid'] = True
			else:
				return_data['ride_valid'] = False
		else:
			return_data['ride_valid'] = False

		# Check if the rider already exists
		if return_data['ride_valid']:
			rides_data = rides_data[rides_data.rideId == int(data['rideId'])]
			riders_list = list(list(rides_data.riders)[0].split(','))
			if data['username'] not in list(riders_list):
				return_data['can_add_rider'] = True
			else:
				return_data['can_add_rider'] = False

		return jsonify(return_data), 200

	# If the calling API is delete_ride API
	if data['api'] == 'delete_ride':
		return_data = dict()

		# Extract rideIds from the users database
		rides_Id = pd.read_csv('rides.csv')['rideId']
		rides_Id = list(map(str, rides_Id))

		# If the rideId is not in the database
		if data['rideId'] in list(rides_Id):
			return_data['rideId_exists'] = True
		else:
			return_data['rideId_exists'] = False

		return jsonify(return_data), 200