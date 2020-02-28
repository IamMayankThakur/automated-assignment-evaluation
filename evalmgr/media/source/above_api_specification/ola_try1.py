from flask import Flask, jsonify, request, render_template
# import flask_restful
import re
import pymongo

#WORKING  WITH THE DATABASE

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["RideShare"]
users = mydb["users"]
rides = mydb['rides']

app = Flask(__name__)

#HANDLING ALL THE EXCEPTIONS

@app.errorhandler(404)
def not_found_error(error):
    return ('',404)

# @app.errorhandler(201)
# def ok_created(error):
#     return "Successfully Created", 201

@app.errorhandler(400)
def bad_request_error(error):
    return  ('',400)

@app.errorhandler(405)
def method_not_allowed_error(error):
    return  ('',405)

# @app.errorhandler(204)
# def not_content_error(error):
#     return "No Content", 204

@app.errorhandler(500)
def internal_server_error(error):
    return (''), 500

#API'S

# @app.route('/')
# def test():
#     return "HELLO WORLD"

@app.route('/api/v1/users', methods = ['PUT'])
def add_user():
    if (request.method == 'PUT'):
        dataDict = request.get_json()
        # return jsonify(dataDict)
        username = dataDict["username"]
        password = dataDict["password"]
        if (not(username)):
            # print("bejfb")
            return (),400
        pattern = re.compile(r'\b[0-9a-f]{40}\b')
        match = re.match(pattern, password)
        if ( match == None):
            # print("bejfbberbtg")
            return (),400   #PASSWORD NOT IN THE CORRECT FORMAT
        else:
            search = {"username" : username}
            dbquery = users.find(search)
            found = 0
            for i in dbquery:
                found += 1
                break
            if (found != 0):
                return (),400 #IF USERNAME ALREADY EXISTS
            else:
                users.insert(({"username" : username, "password" : password}))
                return (),201
    else:
        return (),405   #IF METHOD USED IS NOT PUT


@app.route('/api/v1/users/<username>', methods = ['DELETE'])
def remove_user(username):
    if (request.method == 'DELETE'):
        if (not(username)):
            return {}, 400
        search = {"username" : username}
        dbquery = users.find(search)
        found = 0
        for i in dbquery:
            found += 1
        if (found == 0):
            return (), 400    #USERNAME NOT FOUND
        else:
            x = users.delete_many(search)
            if (x.deleted_count == 1):
                return (), 200   #SUCESSFULLY DELETED
            else:
                return (), 400   #CAN'T BE DELETED
    else:
        return (), 405 #IF THE METHOD USED IS NOT DELETE


@app.route('/api/v1/rides', methods = ['POST'])
def new_ride():
    if (request.method == 'POST'):
        dataDict = request.get_json()
        username = dataDict['created_by']
        timestamp = dataDict['timestamp']
        source = dataDict['source']
        destination = dataDict['destination']
        search = {"username" : username}
        dbquery = users.find(search)
        found = 0
        for i in dbquery:
            found += 1
        if (not(found)):
            return (), 400    #USER NOT REGISTERED
        else:
            rides.insert({"created_by" : username, "timestamp" : timestamp, "source" : source, "destination" : destination, "users_rides" : [username]})
            return (), 200     #INSERTION IS SUCCESSFUL
    else:
        return (), 405  #POST METHOD NOT USED


@app.route('/api/v1/rides', methods = ['GET']) #CHECK FOR THE SOURCE AND DESTINATION
def upcoming_rides():
    if (request.method == 'GET'):
        source = request.args.get('source')
        if (not(source)):
            return (), 400
        source = int(source)
        # source = int(source)
        destination = request.args.get('destination')
        if (not(destination)):
            return (), 400
        destination = int(destination)
        # return jsonify(request.data)
        if (source >= 1 and source <= 198) and (destination >= 1 and destination <= 198):
            search = {"source" : source, "destination" : destination}
            dbquery = rides.find(search)
            li = []
            num = 1111
            for i in dbquery:
                d = dict()
                num += 1
                d["rideId"] = num   ##GLOBALLY UNIQUE CHECK
                d["username"] = i["created_by"]
                d["timestamp"] = i["timestamp"]
                li.append(d)
            # return jsonify(dbquery)
            return jsonify(li)
        else:
            return (), 400
    else:
        return (), 405


@app.route('/api/v1/rides/<rideId>', methods = ['GET'])
def list_all_details(rideId):
    if (request.method == 'GET'):
        rideid = rideId
        search = {'_id' : rideid}
        dbquery = rides.find(search)
        found = 0
        for i in dbquery:
            found += 1
            created_by = i["created_by"]
            users = i["users_rides"]
            timestamp = i["timestamp"]
            source = i["source"]
            destination = i["destination"]
            break
        if (not(found)):
            return (), 204
        else:
            retjson = {
                "rideId" : rideid,
                "created_by" : created_by,
                "users" : users,
                "timestamp" : timestamp,
                "source" : source,
                "destination" : destination
            }
            return jsonify(retjson), 200
    else:
        return (), 405

        

@app.route('/api/v1/rides/<rideId>', methods = ['POST'])
def join_ride(rideId):
    if (request.method == 'GET'):
        rideid = rideId
        dataDict = request.get_json()
        username = dataDict['username']
        search = {'username' : username}
        dbquery = users.find(search)
        found = 0
        for i in dbquery:
            found += 1
        if (not(found)):
            return (), 204
        else:
            select = {"_id" : rideid}
            dbquery = rides.find(select)
            found = 0
            for i in dbquery:
                li = i["users_rides"]
                li.append(username)
                found += 1
            if (not(found)):
                return (), 204
            else:
                new_value = {"$set" : {"users_rides" : li}}
                rides.update(select, new_value)
                return (), 200
    else:
        return (), 405


@app.route('/api/v1/rides/<rideId>', methods = ['DELETE'])
def delete_ride(rideId):
    if (request.method == 'DELETE'):
        rideid = rideId
        return (), 200

    else:
        return (), 405




if __name__ == "__main__":
    app.run(debug=True)