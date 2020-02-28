import flask
from flask import Flask, render_template, request, redirect, jsonify
from flask_mysqldb import MySQL
app = Flask(__name__)
#from flask_api import status
import datetime


app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] =  'indu'
app.config['MYSQL_PASSWORD'] = 'indu123'
app.config['MYSQL_DB'] = 'test'

mysql = MySQL(app)

app.config["DEBUG"] = True

# Create some test data for our catalog in the form of a list of dictionaries.


rideidstart=10000
p=0
argg="LOL"
argnum=0



@app.route('/api/v1/users/all', methods=['GET'])
def api_allusers():
    return jsonify(users)

@app.route('/api/v1/rides/all', methods=['GET'])
def api_allrides():
    return jsonify(rides)



# ADD A NEW USER, API=1
@app.route('/api/v1/users', methods=['PUT', 'POST'])
def api_addnewuser():
    if flask.request.method == 'POST':
        return "Method not allowed!",405
    
    if(len(request.json.get('password'))!=40):
        return "Bad password! Please enter a new one.",400

    for letter in request.json.get('password'):
        if(letter not in {'a','b','c','d','e','f','A','B','C','D','E','F','0','1','2','3','4','5','6','7','8','9'}):
            return "Bad password! Please enter a new one.",400
    
    
    global p
    p=1
    return redirect(flask.url_for('readfromdb'), code=307)




# DELETE A USER, API=2
@app.route('/api/v1/users/<usn>', methods=['DELETE', 'POST'])
def api_deluser(usn):
    if flask.request.method == 'POST':
        return "Method not allowed!",405
    global p
    p=2
    global argg
    argg=usn
    print(type(argg))
    return redirect(flask.url_for('readfromdb'), code=307)




# ADD A NEW RIDE, API=3
@app.route('/api/v1/rides', methods=['POST'])
def api_addnewride():
   
    global p
    p=3
    return redirect(flask.url_for('readfromdb'), code=307)




#RETURN ALL UPCOMING RIDES FOR A SOURCE AND DESTINATION API=4
@app.route('/api/v1/rides', methods=['GET'])
def api_sourceanddest():

    if 'source' not in request.args:
        return "Error! Please provide a source.",400

    if 'destination' not in request.args:
        return "Error! Please provide a destination.",400

    global p
    p=4
    global a
    a=int(request.args.get('source'))
    global b
    b=int(request.args.get('destination'))
    return redirect(flask.url_for('readfromdb'), code=307)

    




# LIST ALL DETAILS OF A GIVEN RIDE API=5
@app.route('/api/v1/rides/<id>', methods=['GET'])
def api_id(id):
    if flask.request.method == 'POST':
        return "Method not allowed!", 405 
    
    global p
    p=5
    global argnum
    argnum=id
    print(type(argnum))
    return redirect(flask.url_for('readfromdb'), code=307)




# JOIN A RIDE, API=6

@app.route('/api/v1/rides/<rideid>', methods=['POST'])
def api_joinride(rideid):

    global p
    p=6
    global argnum
    argnum=rideid
    return redirect(flask.url_for('readfromdb'), code=307)






# DELETE A RIDE, API=7
@app.route('/api/v1/rides/<rideid>', methods=['DELETE', 'POST'])
def api_delride(rideid):
    if flask.request.method == 'POST':
        return "Method not allowed!", 405 
    
    global p
    p=7
    global argg
    argg=rideid
    return redirect(flask.url_for('readfromdb'), code=307)







#WRITE TO A DB, API=8

@app.route('/api/v1/db/write', methods=['POST', 'PUT', 'DELETE', 'GET'])
def writetodb():
    results=[]
    global p
    if p==1:
        username = request.json.get('username')
        password = request.json.get('password')
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(username, password) VALUES (%s, %s)", (username, password))
        mysql.connection.commit()
        cur.close()
        results=[]
        return jsonify(results), 201
        
    if p==2:
        cur = mysql.connection.cursor()
        j=argg
        cur.execute("DELETE FROM users WHERE username='"+j+"'" )
        mysql.connection.commit()
        cur.close()
        return jsonify(results), 200
    if p==3:
        created_by= request.json.get('created_by')
        timestamp=request.json.get('timestamp')
        source=request.json.get('source')
        destination=request.json.get('destination')
        global rideidstart
        rideidstart+=1
        rideid=rideidstart
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO rides(created_by, timestamp1, source1, destination1, rideid) VALUES (%s, %s, %s, %s, %s)", (created_by, timestamp, source, destination, rideid))
        cur.execute("INSERT INTO ride_users(rideid,userz) VALUES (%s, %s)", (rideid,created_by))
        mysql.connection.commit()
        cur.close()
        return jsonify(results), 201
        
    
    if p==6:
        cur = mysql.connection.cursor()
        j=argnum
        cur.execute("INSERT INTO ride_users(rideid,userz) VALUES (%s, %s)",(j,request.json.get('username')))
        mysql.connection.commit()
        cur.close()
        return jsonify(results), 200
        

    if p==7:
        cur = mysql.connection.cursor()
        j=argg
        cur.execute("DELETE FROM rides WHERE rideid='"+j+"'" )
        mysql.connection.commit()
        cur.close()
        return jsonify(results), 200













@app.route('/api/v1/db/read', methods=['POST', 'PUT', 'DELETE', 'GET'])
def readfromdb():
    result=[]
    if p==1:
        cur = mysql.connection.cursor()
        cur.execute("SELECT *  FROM users where username='"+request.json.get('username')+"'")
        row = cur.fetchone()
        if(row!=None):
            return "This user already exists!",400
        
        else:
            return redirect(flask.url_for('writetodb'), code=307)

    if p==2:
        cur = mysql.connection.cursor()
        j=argg
        cur.execute("SELECT *  FROM users where username='"+j+"'")
        row = cur.fetchone()
        if(row==None):
            return "This user doesn't exit. Can't delete.",400
        
        else:
            return redirect(flask.url_for('writetodb'), code=307)
    
    if p==3:
        cur = mysql.connection.cursor()
        cur.execute("SELECT *  FROM users where username='"+request.json.get('created_by')+"'")
        row = cur.fetchone()
        if(row==None):
            return "User doesn't exist. Join now to create a ride!",400
        
        else:
            return redirect(flask.url_for('writetodb'), code=307)

    
    if p==4:
        cur = mysql.connection.cursor()
        cur.execute("SELECT *  FROM rides where source1=%d AND destination1=%d", (request.args.get('source'),request.args.get('destination')))
        #datetime.strptime(str(date), '%Y-%m-%d %H:%M:%S') 
        row1 = cur.fetchall()
        res=[]
        for row in row1:
            resp={
                "rideid":row[4],
                "usernane": row[0],
                "timestamp": row[1]
            }
            res.append(resp)
        #print(row)
        return jsonify(res),200
        


    if p==5:
        cur = mysql.connection.cursor()
        j=argnum
        cur.execute("SELECT *  FROM rides where rideid='"+j+"'")
        row = cur.fetchone()
        #return jsonify(row)
        if(row==None):
            return "Ride doesn't exist!", 204
        cur.execute("SELECT userz  FROM ride_users where rideid='"+j+"'")
        res=[]
        for row1 in cur:
            res.append(row1[0])
        #for x in row1:
        #    res.append(x)

        resp={
            "rideid": row[4],
            "created_by": row[0],
            "timestamp": row[1],
            "source": row[2],
            "destination": row[3],
            "users": res
        }
        result.append(resp)
        cur.close()
        print(resp)
        #return resp, 200
        return jsonify(resp),200

    if p==6:
        cur = mysql.connection.cursor()
        j=argnum
        cur.execute("SELECT *  FROM rides where rideid='"+j+"'")
        row = cur.fetchone()
        if(row==None):
            return "Ride doesn't exist. Create a new ride now!",400

        cur.execute("SELECT *  FROM users where username='"+request.json.get('username')+"'")
        row1 = cur.fetchone()
        if(row1==None):
            return "User doesn't exist. Join today!", 400

        cur.execute("SELECT *  FROM ride_users where userz='"+request.json.get('username')+"' AND rideid='"+j+"'")
        row2 = cur.fetchone()
        if(row2!=None):
            return "This user is already in the ride.",400

        return redirect(flask.url_for('writetodb'), code=307)


    if p==7:
        cur = mysql.connection.cursor()
        j=argg
        print(j)
        cur.execute("SELECT *  FROM rides where rideid='"+j+"'")
        row = cur.fetchone()
        print(row)
        if(row==None):
            return "This ride doesn't exist. Can't delete.",400
        else:
            return redirect(flask.url_for('writetodb'), code=307)
        
    
app.run(host='0.0.0.0', port=80)