import random, json, datetime, re

from flask import Flask, Response, request
from flasgger import Swagger
from pymongo import MongoClient, errors
from bson import json_util
from bson.json_util import dumps
import requests
from time import sleep

app = Flask(__name__)
swagger = Swagger(app)
rides = MongoClient('mongodb://localhost:27017/').demo.rides
users = MongoClient('mongodb://localhost:27017/').demo.users
locations = MongoClient('mongodb://localhost:27017/').demo.locations
locarray = [ { "areano": 1, "areaname": "Kempegowda Ward" }, { "areano": 2, "areaname": "Chowdeswari Ward" }, { "areano": 3, "areaname": "Atturu" }, { "areano": 4, "areaname": "Yelahanka Satellite Town" }, { "areano": 5, "areaname": "Jakkuru" }, { "areano": 6, "areaname": "Thanisandra" }, { "areano": 7, "areaname": "Byatarayanapura" }, { "areano": 8, "areaname": "Kodigehalli" }, { "areano": 9, "areaname": "Vidyaranyapura" }, { "areano": 10, "areaname": "Dodda Bommasandra" }, { "areano": 11, "areaname": "Kuvempu Nagar" }, { "areano": 12, "areaname": "Shettihalli" }, { "areano": 13, "areaname": "Mallasandra" }, { "areano": 14, "areaname": "Bagalakunte" }, { "areano": 15, "areaname": "T Dasarahalli" }, { "areano": 16, "areaname": "Jalahalli" }, { "areano": 17, "areaname": "J P Park" }, { "areano": 18, "areaname": "Radhakrishna Temple Ward" }, { "areano": 19, "areaname": "SanJayanagar" }, { "areano": 20, "areaname": "Ganga Nagar" }, { "areano": 21, "areaname": "Hebbala" }, { "areano": 22, "areaname": "Vishwanath Nagenahalli" }, { "areano": 23, "areaname": "Nagavara" }, { "areano": 24, "areaname": "HBR Layout" }, { "areano": 25, "areaname": "Horamavu" }, { "areano": 26, "areaname": "Ramamurthy Nagar" }, { "areano": 27, "areaname": "Banasavadi" }, { "areano": 28, "areaname": "Kammanahalli" }, { "areano": 29, "areaname": "Kacharkanahalli" }, { "areano": 30, "areaname": "Kadugondanahalli" }, { "areano": 31, "areaname": "Kushal Nagar" }, { "areano": 32, "areaname": "Kaval Bairasandra" }, { "areano": 33, "areaname": "Manorayana Palya" }, { "areano": 34, "areaname": "Gangenahalli" }, { "areano": 35, "areaname": "Aramane Nagara" }, { "areano": 36, "areaname": "Mattikere" }, { "areano": 37, "areaname": "Yeshwanthpura" }, { "areano": 38, "areaname": "HMT Ward" }, { "areano": 39, "areaname": "Chokkasandra" }, { "areano": 40, "areaname": "Dodda Bidarakallu" }, { "areano": 41, "areaname": "Peenya Industrial Area" }, { "areano": 42, "areaname": "Lakshmi Devi Nagar" }, { "areano": 43, "areaname": "Nandini Layout" }, { "areano": 44, "areaname": "Marappana Palya" }, { "areano": 45, "areaname": "Malleshwaram" }, { "areano": 46, "areaname": "Jayachamarajendra Nagar" }, { "areano": 47, "areaname": "Devara Jeevanahalli" }, { "areano": 48, "areaname": "Muneshwara Nagar" }, { "areano": 49, "areaname": "Lingarajapura" }, { "areano": 50, "areaname": "Benniganahalli" }, { "areano": 51, "areaname": "Vijnanapura" }, { "areano": 52, "areaname": "KR Puram" }, { "areano": 53, "areaname": "Basavanapura" }, { "areano": 54, "areaname": "Hudi" }, { "areano": 55, "areaname": "Devasandra" }, { "areano": 56, "areaname": "A Narayanapura" }, { "areano": 57, "areaname": "C.V. Raman Nagar" }, { "areano": 58, "areaname": "New Tippa Sandra" }, { "areano": 59, "areaname": "Maruthi Seva Nagar" }, { "areano": 60, "areaname": "Sagayara Puram" }, { "areano": 61, "areaname": "SK Garden" }, { "areano": 62, "areaname": "Ramaswamy Palya" }, { "areano": 63, "areaname": "Jaya Mahal" }, { "areano": 64, "areaname": "Raj Mahal Guttahalli" }, { "areano": 65, "areaname": "Kadu Malleshwar Ward" }, { "areano": 66, "areaname": "Subramanya Nagar" }, { "areano": 67, "areaname": "Nagapura" }, { "areano": 68, "areaname": "Mahalakshmipuram" }, { "areano": 69, "areaname": "Laggere" }, { "areano": 70, "areaname": "Rajagopal Nagar" }, { "areano": 71, "areaname": "Hegganahalli" }, { "areano": 72, "areaname": "Herohalli" }, { "areano": 73, "areaname": "Kottegepalya" }, { "areano": 74, "areaname": "Shakthi Ganapathi Nagar" }, { "areano": 75, "areaname": "Shankar Matt" }, { "areano": 76, "areaname": "Gayithri Nagar" }, { "areano": 77, "areaname": "Dattatreya Temple Ward" }, { "areano": 78, "areaname": "Pulakeshi Nagar" }, { "areano": 79, "areaname": "Sarvagna Nagar" }, { "areano": 80, "areaname": "Hoysala Nagar" }, { "areano": 81, "areaname": "Vijnana Nagar" }, { "areano": 82, "areaname": "Garudachar palya" }, { "areano": 83, "areaname": "Kadugodi" }, { "areano": 84, "areaname": "Hagadur" }, { "areano": 85, "areaname": "Dodda Nekkundi" }, { "areano": 86, "areaname": "Marathahalli" }, { "areano": 87, "areaname": "HAL Airport" }, { "areano": 88, "areaname": "Jeevanbhima Nagar" }, { "areano": 89, "areaname": "Jogupalya" }, { "areano": 90, "areaname": "Halsoor" }, { "areano": 91, "areaname": "Bharathi Nagar" }, { "areano": 92, "areaname": "Shivaji Nagar" }, { "areano": 93, "areaname": "Vasanth Nagar" }, { "areano": 94, "areaname": "Gandhi Nagar" }, { "areano": 95, "areaname": "Subhash Nagar" }, { "areano": 96, "areaname": "Okalipuram" }, { "areano": 97, "areaname": "Dayananda Nagar" }, { "areano": 98, "areaname": "Prakash Nagar" }, { "areano": 99, "areaname": "Rajaji Nagar" }, { "areano": 100, "areaname": "Basaveshwara Nagar" }, { "areano": 101, "areaname": "Kamakshipalya" }, { "areano": 102, "areaname": "Vrisahbhavathi Nagar" }, { "areano": 103, "areaname": "Kaveripura" }, { "areano": 104, "areaname": "Govindaraja Nagar" }, { "areano": 105, "areaname": "Agrahara Dasarahalli" }, { "areano": 106, "areaname": "Dr.Raj Kumar Ward" }, { "areano": 107, "areaname": "Shiva Nagar" }, { "areano": 108, "areaname": "Sri Rama Mandir Ward" }, { "areano": 109, "areaname": "Chickpete" }, { "areano": 110, "areaname": "Sampangiram Nagar" }, { "areano": 111, "areaname": "Shantala Nagar" }, { "areano": 112, "areaname": "Domlur" }, { "areano": 113, "areaname": "Konena Agrahara" }, { "areano": 114, "areaname": "Agaram" }, { "areano": 115, "areaname": "Vannar Pet" }, { "areano": 116, "areaname": "Nilasandra" }, { "areano": 117, "areaname": "Shanthi Nagar" }, { "areano": 118, "areaname": "Sudham Nagar" }, { "areano": 119, "areaname": "Dharmaraya Swamy Temple" }, { "areano": 120, "areaname": "Cottonpete" }, { "areano": 121, "areaname": "Binni Pete" }, { "areano": 122, "areaname": "Kempapura Agrahara" }, { "areano": 123, "areaname": "ViJayanagar" }, { "areano": 124, "areaname": "Hosahalli" }, { "areano": 125, "areaname": "Marenahalli" }, { "areano": 126, "areaname": "Maruthi Mandir Ward" }, { "areano": 127, "areaname": "Mudalapalya" }, { "areano": 128, "areaname": "Nagarabhavi" }, { "areano": 129, "areaname": "Jnana Bharathi Ward" }, { "areano": 130, "areaname": "Ullalu" }, { "areano": 131, "areaname": "Nayandahalli" }, { "areano": 132, "areaname": "Attiguppe" }, { "areano": 133, "areaname": "Hampi Nagar" }, { "areano": 134, "areaname": "Bapuji Nagar" }, { "areano": 135, "areaname": "Padarayanapura" }, { "areano": 136, "areaname": "Jagajivanaram Nagar" }, { "areano": 137, "areaname": "Rayapuram" }, { "areano": 138, "areaname": "Chelavadi Palya" }, { "areano": 139, "areaname": "KR Market" }, { "areano": 140, "areaname": "Chamraja Pet" }, { "areano": 141, "areaname": "Azad Nagar" }, { "areano": 142, "areaname": "Sunkenahalli" }, { "areano": 143, "areaname": "Vishveshwara Puram" }, { "areano": 144, "areaname": "Siddapura" }, { "areano": 145, "areaname": "Hombegowda Nagar" }, { "areano": 146, "areaname": "Lakkasandra" }, { "areano": 147, "areaname": "Adugodi" }, { "areano": 148, "areaname": "Ejipura" }, { "areano": 149, "areaname": "Varthur" }, { "areano": 150, "areaname": "Bellanduru" }, { "areano": 151, "areaname": "Koramangala" }, { "areano": 152, "areaname": "Suddagunte Palya" }, { "areano": 153, "areaname": "Jayanagar" }, { "areano": 154, "areaname": "Basavanagudi" }, { "areano": 155, "areaname": "Hanumanth Nagar" }, { "areano": 156, "areaname": "Sri Nagar" }, { "areano": 157, "areaname": "Gali Anjenaya Temple Ward" }, { "areano": 158, "areaname": "Deepanjali Nagar" }, { "areano": 159, "areaname": "Kengeri" }, { "areano": 160, "areaname": "Raja Rajeshawari Nagar" }, { "areano": 161, "areaname": "Hosakerehalli" }, { "areano": 162, "areaname": "Giri Nagar" }, { "areano": 163, "areaname": "Katriguppe" }, { "areano": 164, "areaname": "Vidya Peeta Ward" }, { "areano": 165, "areaname": "Ganesh Mandir Ward" }, { "areano": 166, "areaname": "Kari Sandra" }, { "areano": 167, "areaname": "Yediyur" }, { "areano": 168, "areaname": "Pattabhi Ram Nagar" }, { "areano": 169, "areaname": "Byra Sandra" }, { "areano": 170, "areaname": "Jayanagar East" }, { "areano": 171, "areaname": "Gurappana Palya" }, { "areano": 172, "areaname": "Madivala" }, { "areano": 173, "areaname": "Jakka Sandra" }, { "areano": 174, "areaname": "HSR Layout" }, { "areano": 175, "areaname": "Bommanahalli" }, { "areano": 176, "areaname": "BTM Layout" }, { "areano": 177, "areaname": "JP Nagar" }, { "areano": 178, "areaname": "Sarakki" }, { "areano": 179, "areaname": "Shakambari Narar" }, { "areano": 180, "areaname": "Banashankari Temple Ward" }, { "areano": 181, "areaname": "Kumara Swamy Layout" }, { "areano": 182, "areaname": "Padmanabha Nagar" }, { "areano": 183, "areaname": "Chikkala Sandra" }, { "areano": 184, "areaname": "Uttarahalli" }, { "areano": 185, "areaname": "Yelchenahalli" }, { "areano": 186, "areaname": "Jaraganahalli" }, { "areano": 187, "areaname": "Puttenahalli" }, { "areano": 188, "areaname": "Bilekhalli" }, { "areano": 189, "areaname": "Honga Sandra" }, { "areano": 190, "areaname": "Mangammana Palya" }, { "areano": 191, "areaname": "Singa Sandra" }, { "areano": 192, "areaname": "Begur" }, { "areano": 193, "areaname": "Arakere" }, { "areano": 194, "areaname": "Gottigere" }, { "areano": 195, "areaname": "Konankunte" }, { "areano": 196, "areaname": "Anjanapura" }, { "areano": 197, "areaname": "Vasanthpura" }, { "areano": 198, "areaname": "Hemmigepura" } ]
locations.remove({})
for location in locarray:
  locations.insert_one({
        '_id': location['areano'],
        'areaname': location['areaname']
    })
  

@app.route("/api/v1/users", methods=["PUT"])
def add_user():
    """Create user by entering Username and Password
    ---
    parameters:
      - name: username
        in: formData
        type: string
        required: true
      - name: password
        in: formData
        type: string
        required: true
    responses:
      200:
        description: User creation succeded
    """
    request_params = request.form
    if 'username' not in request_params or 'password' not in request_params:
        return Response('Username and Password not present in parameters!', status=400, mimetype='application/json')
    
    if len(request_params['password']) != 40:
        return Response(json.dumps([{"msg":"Length of the Password should be 40 charecter SHA1 hash HEX "}]), status=400, mimetype='application/json')
    
    pattern = re.compile(r'\b[0-9a-f]{40}\b', re.IGNORECASE)
    match = bool(re.match(pattern, request_params['password']))
    if match == False:
        return Response(json.dumps([{"msg":"Password should be 40 charecter SHA1 hash HEX "}]), status=404, mimetype='application/json')

    
    userid = random.randrange(10000, 99999, 3)

    try:
        user = users.find_one({'username': request_params['username']})
        if None != user:
          return Response(json.dumps([{"msg":"Username already exists! Please try with new Username"}]), status=400, mimetype='application/json')
    except errors.DuplicateKeyError as e:
        print("user not found")
    try:
        users.insert_one({
            '_id': userid,
            'password': request_params['password'],
            'username': request_params['username']
        })
    except errors.DuplicateKeyError as e:
        return Response(json.dumps([{"msg":"Duplicate user id!"}]), status=404, mimetype='application/json')
    return Response(json.dumps(users.find_one({'_id': userid})), status=200, mimetype='application/json')


@app.route("/api/v1/users/<int:userid>", methods=["POST"])
def update_user(userid):
    """Update user information by userid
    ---
    parameters:
      - name: userid
        in: path
        type: string
        required: true
      - name: username
        in: formData
        type: string
        required: false
    responses:
      200:
        description: Update succeded
    """
    request_params = request.form
    if 'userid' not in request_params and 'username' not in request_params:
        return Response('Userid and username must be present in parameters!', status=404, mimetype='application/json')

    usernames = users.find_one({'username': request_params['username']})
    if None != usernames:
      return Response(json.dumps([{"msg":"Username already exists! Please try with new Username"}]), status=400, mimetype='application/json')

    userids = users.find_one({'_id': userid})
    if None == userids:
      return Response(json.dumps([{"msg":"Userid not found! Please try with correct userid"}]), status=400, mimetype='application/json')

    set = {}
    if 'userid' in request_params:
        set['userid'] = request_params['userid']
    if 'username' in request_params:
        set['username'] = request_params['username']
    users.update_one({'_id': userid}, {'$set': set})
    return Response(json.dumps(users.find_one({'_id': userid})), status=200, mimetype='application/json')


@app.route("/api/v1/users/<int:userid>", methods=["GET"])
def get_user(userid):
    """Details about a user by userid
    ---
    parameters:
      - name: userid
        in: path
        type: string
        required: true
    definitions:
      User:
        type: object
        properties:
          _id:
            type: int
          username:
            type: string
    responses:
      200:
        description: User model
        schema:
          $ref: '#/definitions/User'
      404:
        description: User not found
    """
    user = users.find_one({'_id': userid})
    if None == user:
        return Response(json.dumps([[{"msg":"User id not found in users list"}]]), status=404, mimetype='application/json')
    return Response(json.dumps(user), status=200, mimetype='application/json')

@app.route("/api/v1/usersbyname/<string:username>", methods=["GET"])
def get_userbyname(username):
    """Details about a user by Username
    ---
    parameters:
      - name: username
        in: path
        type: string
        required: true
    definitions:
      User:
        type: object
        properties:
          _id:
            type: int
          email:
            type: string
          username:
            type: string
    responses:
      200:
        description: User model
        schema:
          $ref: '#/definitions/User'
      404:
        description: User not found
    """
    user = users.find_one({'username': username})
    if None == user:
        return Response(json.dumps([[{"msg":"Username not found in users list"}]]), status=404, mimetype='application/json')
    return Response(json.dumps([user]), status=200, mimetype='application/json')


@app.route("/api/v1/users", methods=["GET"])
def get_users():
    """Endpoint returning all Users with pagination
    ---
    parameters:
      - name: limit
        in: query
        type: integer
        required: false
      - name: offset
        in: query
        type: integer
        required: false
    definitions:
      User:
        type: object
        properties:
          _id:
            type: int
          username:
            type: string
    responses:
      200:
        description: List of user models
        schema:
          $ref: '#/definitions/User'
    """
    request_args = request.args
    limit = int(request_args.get('limit')) if 'limit' in request_args else 10
    offset = int(request_args.get('offset')) if 'offset' in request_args else 0
    user_list = users.find().limit(limit).skip(offset)
    if None == users:
        return Response(json.dumps([[{"msg":"Users list empty or not found"}]]), status=404, mimetype='application/json')

    return Response(dumps(user_list, default=json_util.default), status=200, mimetype='application/json')


@app.route("/api/v1/usersbyid/<int:userid>", methods=["DELETE"])
def delete_user(userid):
    """Delete operation for a User by userid
    ---
    parameters:
      - name: userid
        in: path
        type: string
        required: true
    responses:
      200:
        description: User deleted successfully
    """
    user = users.find_one({'_id': userid})
    if None == user:
        return Response(json.dumps([{"msg":"User id not found"}]), status=400, mimetype='application/json')
    users.delete_one({'_id': userid})
    return Response(json.dumps([{"msg":"User deleted"}]), status=200, mimetype='application/json')




@app.route("/api/v1/users/<string:username>", methods=["DELETE"])
def delete_userbyname(username):
    """Delete operation for a User by Username
    ---
    parameters:
      - name: username
        in: path
        type: string
        required: true
    responses:
      200:
        description: User deleted successfully
    """
    user = users.find_one({'username': username})
    if None == user:
        return Response(json.dumps([{"msg":"Username not found"}]), status=400, mimetype='application/json')
    users.delete_one({'username': username})
    return Response(json.dumps([{"msg":"User deleted"}]), status=200, mimetype='application/json')




@app.route("/api/v1/cleardbuser", methods=["GET"])
def clear_dbaseuser():
    """Clear all data from Users database
    ---
    responses:
      200:
        description: Users DB cleared - Success
    """
    users.remove({})
    return Response(json.dumps([{"msg":"Users DB cleared"}]), status=200, mimetype='application/json')


@app.route("/api/v1/rides", methods=["PUT"])
def add_rides():
    """Create rides
    ---
    parameters:
      - name: username
        in: formData
        type: string
        required: true
      - name: timestamp
        in: formData
        type: string
        required: true
      - name: source
        in: formData
        type: integer
        required: true
      - name: destination
        in: formData
        type: integer
        required: true
    responses:
      200:
        description: Creation succeded
    """
    request_params = request.form
    if 'username' not in request_params or 'timestamp' not in request_params or 'source' not in request_params or 'destination' not in request_params:
        return Response('Username, Timestamp, Source, Destination not present in parameters!', status=404, mimetype='application/json')
    users = []
    rideid = random.randrange(10000, 99999, 3)
    userlist = requests.get('http://127.0.01:5000/api/v1/usersbyname/'+request_params['username'])
    sleep(4)
    if 200 != userlist.status_code:
        return Response(json.dumps([{"msg":"Username not found in User list!"}]), status=404, mimetype='application/json')
    
    users.append(request_params['username'])
    srcname = locations.find_one({'_id':int(request_params['source'])})
    if None == srcname:
        return  Response(json.dumps([{'msg':'Source location not available'}]), status=404, mimetype='application/json')
    
    dstname = locations.find_one({'_id':int(request_params['destination'])})
    if None == dstname:
        return  Response(json.dumps([{'msg':'Destination location not available'}]), status=404, mimetype='application/json')
    try:
        rides.insert_one({
            '_id': rideid,
            'users': users,
            'timestamp': request_params['timestamp'],
            'source': request_params['source'],
            'destination': request_params['destination'],
            'sourcename': srcname['areaname'],
            'destinationname':  dstname['areaname']
        })
    except errors.DuplicateKeyError as e:
        return "some error occured"
    return Response(json.dumps(rides.find_one({'_id': rideid})), status=200, mimetype='application/json')


@app.route("/api/v1/addusertoaride/<int:rideid>", methods=["POST"])
def update_ride(rideid):
    """Add user to a ride
    ---
    parameters:
      - name: rideid
        in: path
        type: string
        required: true
      - name: username
        in: formData
        type: string
        required: true
    responses:
      200:
        description: Update succeded
    """
    request_params = request.form
    if 'username' not in request_params:
        return Response('Username must be present in parameters!', status=404, mimetype='application/json')
        
    userlist = requests.get('http://127.0.01:5000/api/v1/usersbyname/'+request_params['username'])
    sleep(4)
    if 200 != userlist.status_code:
        return Response(json.dumps([{"msg":"Username not found in User list!"}]), status=404, mimetype='application/json')
           
    currentuser = []
    currentride = rides.find_one({'_id': rideid})
    currentuser = currentride['users']
    currentuser.append(request_params['username'])
    if None == currentride:
        return  Response('Invalid ride id!', status=404, mimetype='application/json')
    else:
        rides.delete_one({'_id': rideid})
        rides.insert_one({
            '_id': rideid,
            'users': currentuser,
            'timestamp': currentride['timestamp'],
            'source': currentride['source'],
            'destination': currentride['destination']
        })
    return Response(json.dumps(rides.find_one({'_id': rideid})), status=200, mimetype='application/json')


@app.route("/api/v1/allrides", methods=["GET"])
def get_rides():
    """Example endpoint returning all rides with pagination
    ---
    parameters:
      - name: limit
        in: query
        type: integer
        required: false
      - name: offset
        in: query
        type: integer
        required: false
    definitions:
      Ride:
        type: object
        properties:
          _id:
            type: string
          users:
            type: array
          timestamp:
            type: string
          source:
            type: string
          destination:
            type: string
    responses:
      200:
        description: List of rides models
        schema:
          $ref: '#/definitions/Ride'
    """
    request_args = request.args
    limit = int(request_args.get('limit')) if 'limit' in request_args else 10
    offset = int(request_args.get('offset')) if 'offset' in request_args else 0
    rides_list = rides.find().limit(limit).skip(offset)
    if None == rides:
        return Response(json.dumps([{"msg":"Rides list is empty"}]), status=200, mimetype='application/json')

    extracted = [
        {'_id': d['_id'],
         'users': d['users'],
         'timestamp': d['timestamp'],
         'source': d['source'],
         'destination': d['destination']
         } for d in rides_list]
    return Response(json.dumps(extracted, default=json_util.default), status=200, mimetype='application/json')


@app.route("/api/v1/rides", methods=["GET"])
def get_rides_by_src_dst():
    """Example endpoint returning all rides with pagination filtered by Sorce and Destination
    ---
    parameters:
      - name: source
        in: query
        type: integer
        required: true
      - name: destination
        in: query
        type: integer
        required: true
    definitions:
      Ride:
        type: object
        properties:
          _id:
            type: string
          users:
            type: array
          timestamp:
            type: string
          source:
            type: integer
          destination:
            type: integer
    responses:
      200:
        description: List of rides models
        schema:
          $ref: '#/definitions/Ride'
    """
    request_args = request.args
    rides_list = rides.find_one({'source': request_args['source'],'destination':request_args['destination'] })
    if None == rides_list:
        return Response(json.dumps([{"msg":"Rides from selected Source and Destination is Empty"}]), status=404, mimetype='application/json')

    return Response(json.dumps(rides_list, default=json_util.default), status=200, mimetype='application/json')


@app.route("/api/v1/ridesmaster", methods=["GET"])
def get_rides_master():
    """Example endpoint returning all rides master data, Sorce and Destination
    ---
    definitions:
      Ride:
        type: object
        properties:
          _id:
            type: string
          areaname:
            type: string
    responses:
      200:
        description: List of master source and sestination
        schema:
          $ref: '#/definitions/Ride'
    """
    locations_list = locations.find()
    if None == locations_list:
        return Response(json.dumps([{"msg":"Master data for Source and Destination is Empty"}]), status=404, mimetype='application/json')

    return Response(dumps(locations_list, default=json_util.default), status=200, mimetype='application/json')

@app.route("/api/v1/rides/<int:rideid>", methods=["DELETE"])
def delete_ride(rideid):
    """Delete operation for a ride
    ---
    parameters:
      - name: rideid
        in: path
        type: string
        required: true
    responses:
      200:
        description: Ride deleted
    """
    rides.delete_one({'_id': rideid})
    return Response(json.dumps([{"msg":"Ride Deleted"}]), status=200, mimetype='application/json')

@app.route("/api/v1/rides/<int:rideid>", methods=["GET"])
def get_ridebyid(rideid):
    """Get ride by rideid
    ---
    parameters:
      - name: rideid
        in: path
        type: string
        required: true
    responses:
      200:
        description: Ride by raidid
    """
    ridebyid = rides.find_one({'_id': rideid})
    if None == ridebyid:
        return Response(json.dumps([{"msg":"Rideid not found"}]), status=404, mimetype='application/json')
    return Response(json.dumps(ridebyid), status=200, mimetype='application/json')

@app.route("/api/v1/userrides/<string:username>", methods=["GET"])
def check_user(username):
    """Get username from Users
    ---
    parameters:
      - name: username
        in: path
        type: string
        required: true
    responses:
      200:
        description: Getting data from Users image
    """
    userlist = requests.get('http://127.0.01:5000/api/v1/usersbyname/'+username)
    if None == userlist:
        return Response(json.dumps([{"msg":"User not found"}]), status=404, mimetype='application/json')
    return Response(userlist, status=200, mimetype='application/json')


@app.route("/api/v1/cleardbride", methods=["GET"])
def clear_dbaserides():
    """Clear all data from Ride database
    ---
    responses:
      200:
        description: Rides DB cleared - Success
    """
    rides.remove({})
    return Response(json.dumps([{"msg":"Rides DB cleared"}]), status=200, mimetype='application/json')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=6000)