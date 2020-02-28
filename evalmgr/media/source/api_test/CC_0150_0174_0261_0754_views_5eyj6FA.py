
from flask import Flask, render_template, jsonify, request, abort, Response, make_response
import json
import requests
from pymongo import MongoClient
from datetime import datetime
import hashlib

app = Flask(__name__)

host = 'http://ec2-3-220-138-188.compute-1.amazonaws.com'
# host = 'http://127.0.0.1:5000'

global rideId
rideId = 1


def is_sha1(maybe_sha):
    if len(maybe_sha) != 40:
        return False
    try:
        sha_int = int(maybe_sha, 16)
    except ValueError:
        return False
    return True


@app.route('/api/v1/users', methods=['PUT'])
def add_user():
#    try:
        content = request.get_json()
        if(not content['username'] or not content['password'] or not is_sha1(content['password'])):
            # return json.dumps({'success': False, 'message': 'The password field must be a SHA1 hash hex.'}), 400, {'ContentType': 'application/json'}
            return jsonify({'message':'Contents missing'}), 400

        data = {
            'table': 'users',
            'insert': {
                'username': str(content['username']),
                'password': str(content['password'])
            },
        }
        response = requests.post(
            host + '/api/v1/write', json=data)

        if(response.status_code == 201):

#             return json.dumps({}), 200, {'ContentType': 'application/json'}
            return ('', 201)
        elif(response.status_code == 403):
            # return json.dumps({'success': False, 'message': 'User Exists.'}), 403, {'ContentType': 'application/json'}
            print(2)
            return jsonify({'message':'User Exists'}), 400
        else:
            print(3)
            # return json.dumps({'success': False, 'message': 'Invalid Request Body.'}), 400, {'ContentType': 'application/json'}
            return jsonify({'message':'Invalid Body'}), 400
        print(4)
#    except:
        # return json.dumps({'success': False, 'message': 'Invalid Request Body.'}), 400, {'ContentType': 'application/json'}
        return jsonify({'message':'Invalid Request'}), 400


@app.route('/api/v1/users/<username>', methods=['DELETE'])
def remove_user(username):
    try:
        content = {
            'table': 'users',
            'delete': {'username': username},
            'cascade': 1,
            'exist': [['username', username, 'users']]
        }
        response = requests.post(
            host + '/api/v1/write', json=content)

        if(response.status_code == 200):
            # return json.dumps({'success': True, 'message': 'Deleted User ' + username + '.'}), 200, {'ContentType': 'application/json'}
            return jsonify({}), 200
        elif(response.status_code == 404):
            # return json.dumps({'success': False, 'message': 'Username does not exist.'}), 404, {'ContentType': 'application/json'}
            return jsonify({}), 400
        else:
            # return json.dumps({'success': False, 'message': 'Invalid Request Body.'}), 400, {'ContentType': 'application/json'}
            return jsonify({}), 400
    except:
        # return json.dumps({'success': False, 'message': 'Invalid Request Body.'}), 400, {'ContentType': 'application/json'}
        return jsonify({}), 400


@app.route('/api/v1/rides', methods=['POST', 'GET'])
def new_ride():
    if(request.method == 'POST'):
#        try:
            content = request.get_json()
            data = {
                'table': 'rides',
                'insert': {
                    'created-by': str(content['created_by']),
                    'users': [str(content['created_by'])],
                    # 'timestamp': datetime.now().strftime('%d-%m-%Y:%S-%M-%H'),
                    'timestamp': content['timestamp'],
                    'source': str(content['source']),
                    'destination': str(content['destination'])
                },
                'exist': [['username', str(content['created_by']), 'users'], ['areaNo', int(content['source']), 'areaName'], ['areaNo', int(content['destination']), 'areaName']]
            }
            response = requests.post(
                host + '/api/v1/write', json=data)

            print(data)

            if(response.status_code == 201):

                # return json.dumps({'success': True, 'message': 'Created New Ride.'}), 201, {'ContentType': 'application/json'}
                return jsonify({}), 201
            elif(response.status_code == 404):
                print(1)
                # return json.dumps({'success': False, 'message': 'Username does not exist.'}), 404, {'ContentType': 'application/json'}
                return jsonify({}), 400
            elif(response.status_code == 403):
                print(2)
                # return json.dumps({'success': False, 'message': 'Ride exists.'}), 403, {'ContentType': 'application/json'}
                return jsonify({}), 400
            else:
                print(3)
                # return json.dumps({'success': False, 'message': 'Invalid Request Body.'}), 400, {'ContentType': 'application/json'}
                return jsonify({}), 400
#        except:
            print(4)
            # return json.dumps({'success': False, 'message': 'Invalid Request Body.'}), 400, {'ContentType': 'application/json'}
            return jsonify({}), 400

    else:
        data = {
            'table': 'rides',
            'query': {
                'source': int(request.args.get('source')),
                'destination': int(request.args.get('destination'))
            },
            'timestamp': datetime.now().strftime('%d-%m-%Y:%S-%M-%H'),
        }

        response = requests.post(
            host + '/api/v1/db/read', json=data)
        if(response.status_code == 200):
            # return json.dumps({'success': True, 'data': json.loads(response.text)['data']}), 200, {'ContentType': 'application/json'}
            return jsonify(json.loads(response.text)['data']), 200
        elif(response.status_code == 204):
            # return json.dumps({'success': True, 'data': json.loads(response.text)['data'][0]}), 200, {'ContentType': 'application/json'}
            return jsonify({}), 204
        # return json.dumps({'success': False}), 400, {'ContentType': 'application/json'}
        return jsonify({}), 400


@app.route('/api/v1/rides/<rideId>', methods=['GET', 'POST', 'DELETE'])
def join_ride(rideId):
    content = request.get_json()
    if(request.method == 'POST'):
        data = {
            'table': 'rides',
            'update': {'users': str(content['username'])},
            'find':  {'rideId': rideId},
            'exist': [['username', str(content['username']), 'users'], ['rideId', rideId, 'rides']]
        }

        response = requests.post(
            host + '/api/v1/write', json=data)

        if(response.status_code == 200):
            # return json.dumps({'success': True, 'message': 'Updated Ride.'}), 200, {'ContentType': 'application/json'}
            return jsonify({}), 200
        elif(response.status_code == 404):
            # return json.dumps({'success': False, 'message': 'Username/rideId does not exist.'}), 404, {'ContentType': 'application/json'}
            return jsonify({}), 404
        else:
            # return json.dumps({'success': False, 'message': 'Invalid Request Body.'}), 400, {'ContentType': 'application/json'}
            return jsonify({}), 400
    elif(request.method == 'GET'):
        data = {
            "table": "rides",
            "query": {
                "rideId": rideId
            },
            'exist': [['rideId', rideId, 'rides']]
        }
        response = requests.post(
            host + '/api/v1/db/read', json=data)
        if(response.status_code == 200):
            # return json.dumps({'success': True, 'data': json.loads(response.text)['data'][0]}), 200, {'ContentType': 'application/json'}
            return jsonify(json.loads(response.text)['data'][0]), 200
        elif(response.status_code == 204):
            # return json.dumps({'success': True, 'data': json.loads(response.text)['data'][0]}), 200, {'ContentType': 'application/json'}
            return jsonify({}), 204
        # return json.dumps({'success': False}), 400, {'ContentType': 'application/json'}
        return jsonify({}), 400

    else:
        content = {
            'table': 'rides',
            'delete': {'rideId': rideId},
            'cascade': 0,
            'exist': [['rideId', rideId, 'rides']]
        }
        response = requests.post(
            host + '/api/v1/write', json=content)

        if(response.status_code == 200):
            # return json.dumps({'success': True, 'message': 'Deleted Ride ' + rideId + '.'}), 200, {'ContentType': 'application/json'}
            return jsonify({}), 200
        elif(response.status_code == 404):
            # return json.dumps({'success': False, 'message': 'Ride does not exist.'}), 404, {'ContentType': 'application/json'}
            return jsonify({}), 404
        else:
            # return json.dumps({'success': False, 'message': 'Invalid Request Body.'}), 400, {'ContentType': 'application/json'}
            return jsonify({}), 400


@app.route('/api/v1/write', methods=['POST'])
def write():
    client = MongoClient()
    try:
        content = request.get_json()
    except:
        return json.dumps({'success': False}), 400, {'ContentType': 'application/json'}
    table = content['table']
    myClient = client.A1[table]

    if(('exist' in content.keys())):
        for i in content['exist']:
            tmp_table = i[2]
            tmp_Client = client.A1[tmp_table]
            if(i[0] in ['rideId', 'source', 'destination']):
                i[1] = int(i[1])
            if((tmp_Client.count_documents({i[0]: i[1]}, limit=1) == 0)):
                # return json.dumps({'success': False}), 404, {'ContentType': 'application/json'}
                return Response(status=404, mimetype='application/json')

    if('insert' in content.keys()):
        ins = content['insert']
        if(content['table'] == 'rides'):
            global rideId
            ins['rideId'] = rideId
            rideId += 1
        if('source' in ins.keys()):
            ins['source'] = int(ins['source'])
            ins['destination'] = int(ins['destination'])
        exists = myClient.find_one(ins)

        if not exists:
            myClient.insert_one(ins)
            # return json.dumps({'success': True}), 201, {'ContentType': 'application/json'}
            return Response(status=201, mimetype='application/json')

        # return json.dumps({'success': True}), 403, {'ContentType': 'application/json'}
        return Response(status=403, mimetype='application/json')

    elif('delete' in content.keys()):
        if('rideId' in content['delete']):
            content['delete']['rideId'] = int(content['delete']['rideId'])
        myClient.delete_one(content['delete'])
        if(content['cascade']==1):
            rideCol = client.A1['rides']
            for doc in rideCol.find():
                if(doc['created-by'] == content['delete']['username']):
                    rideCol.delete_one({'rideId': int(doc['rideId'])})
                if(content['delete']['username'] in doc['users']):
                    rideCol.update_one({'rideId': int(doc['rideId'])}, {'$pull': { 'users': content['delete']['username']}})

        # return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
        return Response(status=200, mimetype='application/json')

    elif('update' in content.keys()):
        if('rideId' in content['find']):
            content['find']['rideId'] = int(content['find']['rideId'])
        myClient.update_one(
            content['find'], {'$addToSet': content['update']})
        # return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
        return Response(status=200, mimetype='application/json')


@app.route('/api/v1/db/read', methods=['POST'])
def read_data():
    client = MongoClient()
    try:
        content = request.get_json()
    except:
        # return json.dumps({'success': False}), 400, {'ContentType': 'application/json'}
        return Response(status=400, mimetype='application/json')
    table = content['table']
    myClient = client.A1[table]

    respArray = []
    if('rideId' in content['query']):
        content['query']['rideId'] = int(content['query']['rideId'])
    for resp in myClient.find(content['query']):
        if('timestamp' in content.keys() and content['timestamp'] < resp['timestamp']):
            tmp = {
                'rideId': resp['rideId'],
                'username': resp['created-by'],
                'timestamp': resp['timestamp']
            }
        else:
            tmp = {
                'rideId': resp['rideId'],
                'username': resp['created-by'],
                'timestamp': resp['timestamp'],
                'source': resp['source'],
                'users': resp['users'],
                'destination': resp['destination']
            }

        respArray.append(tmp)
    if(len(respArray) > 0):
        return json.dumps({'data': respArray}), 200, {'ContentType': 'application/json'}
        # return Response(status=200, mimetype='application/json')
    return json.dumps({'data': {}}), 204, {'ContentType': 'application/json'}
    # return Response(status=204, mimetype='application/json')


@app.route('/home')
def hello():
    return '<h1>Rishi Gonna Hide</h1>'


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
