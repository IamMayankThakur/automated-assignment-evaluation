from flask_api import status
from datetime import datetime
from flask import Flask, render_template,jsonify,request,abort
from flask_sqlalchemy import SQLAlchemy
import requests

def is_sha1(x):
    if len(x) != 40:
        return 0
    try:
        y = int(x, 16)
    except ValueError:
        return 0
    return 1

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)
# Ensure FOREIGN KEY for sqlite3
if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
    def _fk_pragma_on_connect(dbapi_con, con_record):  # noqa
        dbapi_con.execute('pragma foreign_keys=ON')

    with app.app_context():
        from sqlalchemy import event
        event.listen(db.engine, 'connect', _fk_pragma_on_connect)
# app.run(debug=True)
#dictionary containing book names
# and quantities

class User(db.Model):
	username = db.Column(db.Text(), unique=True, primary_key=True)
	password = db.Column(db.Text(), nullable=False)
	#ride= db.relationship("Ride", back_populates="user")

	def __repr__(self):
		return '<User %r>' % self.username
	def __init__(self, Name,passw):
		self.username = Name
		self.password= passw

class Ride(db.Model):
	rideid = db.Column(db.Integer,primary_key=True)
	source = db.Column(db.Text(),nullable=False)
	destination = db.Column(db.Text(),nullable=False)
	timestamp = db.Column(db.DateTime(),nullable=False)
	created_by= db.Column(db.Text(),db.ForeignKey('user.username'),nullable=False)
	#user= db.relationship("User",back_populates="ride")
#db foreign Key contrain to be added
	def __repr__(self):
		return '<rideid %r>' % self.rideid
	def __init__(self,s,d,t,c):
		self.source= s
		self.destination= d
		datetime_object = datetime.strptime(t, '%d-%m-%Y:%S-%M-%H')
		self.timestamp = datetime_object
		self.created_by= c
class Ridetake(db.Model):
	rideid = db.Column(db.Integer,db.ForeignKey('ride.rideid'),nullable=False, primary_key=True)
	user=db.Column(db.Text(),db.ForeignKey('user.username'),nullable=False, primary_key=True)
	def __repr__(self):
		return '<rideid %r>' % self.rideid
	def __init__(self,r,u):
		self.rideid= r
		self.user= u
		

@app.route("/api/v1/db/write",methods=["POST"])
def write_db(db=db):
#“column name” : “data”,
#“column” : “column name”,
#“table” : “table name”
	# print(request.get_json())
	l=request.get_json()['insert']
	me =("global us;us="+request.get_json()["table"]+"("+ str(l)[1:-1]+")")
	# print(type(me))
	exec(me)	
	# print(us)
	#User("a","b")
	db.session.add(us)
	db.session.commit()
	return (jsonify())


@app.route("/api/v1/db/read",methods=["POST"])
def read_db():
# 	{
# “table”: “table name”,
# “columns”: [“column name”,],
# “where”: “[column=='value',"fhgf>=yu"]”
# }
	me =("global us;us="+request.get_json()["table"]+".query.filter"+"("+request.get_json()["where"]+").all()")
	# print(me)
	exec(me)
	# print(us)
	lis=[]
	for i in us:
		global res
		res={}
		for j in request.get_json()["columns"]:
			exec("res[j]=i."+j)
		lis+=[res]
	# print()
	return (jsonify(lis))
	# db.session.add(me)
	# db.session.commit()
@app.route("/api/v1/users",methods=["PUT"])
def create_user():
	#try:
		ur=request.url_root
		#IF SHA1 TO BE DONE case insensitive
		#print(request.get_json()['username'],request.get_json()['password'])
		try:
			data={'table':'User','insert':[request.get_json()['username'],request.get_json()['password']]}
		except:
			return ("Invalid Request",status.HTTP_400_BAD_REQUEST)
		x = is_sha1(request.get_json()['password'])
		if x==0:
			return ("Password format Invalid",status.HTTP_400_BAD_REQUEST)
		# print(data)
		r=requests.post(ur+'api/v1/db/write',json=data )
		# print(r.status_code)
		if r.status_code==500:
			return ("Not Unique Username",status.HTTP_400_BAD_REQUEST)
		return (jsonify(),status.HTTP_201_CREATED)	
	# except:
	# 	abort(400)
@app.route("/api/v1/rides",methods=["POST"])
def create_ride():
	#try:
		ur=request.url_root
		#datetime_object = datetime.strptime(request.get_json()['timestamp'], '%d-%m-%Y:%S-%M-%H')
		#print(request.gset_json()['username'],request.get_json()['password'])
		try:
			data={'table':'Ride','insert':[request.get_json()['source'],request.get_json()['destination'],request.get_json()['timestamp'],request.get_json()['created_by']]}
		except:
			return ("Invalid Request",status.HTTP_400_BAD_REQUEST)
			

		# print(data)
		r=requests.post(ur+'api/v1/db/write',json=data )
		
		#print(r.status_code)
		if r.status_code==500:
			return ("User Not Found",status.HTTP_400_BAD_REQUEST)
		return (jsonify(),status.HTTP_201_CREATED)	
	#except:
	#	abort(400)

	#
	# me = exec(request.get_json()["table"]+"("+request.get_json()["table"]+")")
	# db.session.add(me)
	# db.session.commit()
@app.route("/api/v1/rides",methods=["GET"])
def get_rides():
	#try:	
		ur=request.url_root
		#datetime_object = datetime.strptime(request.get_json()['timestamp'], '%d-%m-%Y:%S-%M-%H')
		# print(request.gset_json()['username'],request.get_json()['password'])
		# print(request.args.get('source'))
		try:
			data={"table": "Ride","columns": ["created_by","rideid","timestamp"],"where": "Ride.timestamp>='"+str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))+"',Ride.source=="+request.args.get('source')+",Ride.destination=="+request.args.get('destination')}
			# print(data)
		except:
			return ('Missing Parameter',status.HTTP_400_BAD_REQUEST)
		if int(request.args.get('source')) in range(1,199) and int(request.args.get('destination')) in range(1,199):
			r=requests.post(ur+'api/v1/db/read',json=data )
			d=r.json()
			if(len(d)==0):
				return ("",status.HTTP_204_NO_CONTENT)
			for i in d:
				i["username"]=i.pop("created_by")
				i['timestamp'] = datetime.strptime(i['timestamp'], '%a, %d %b %Y %H:%M:%S %Z').strftime('%d-%m-%Y:%S-%M-%H')
			# print(d)
			return (jsonify(d))	
		else:
			return ('Source/destination invalid',status.HTTP_400_BAD_REQUEST)
		

		#except:
	#	abort(400)

	#
	# me = exec(request.get_json()["table"]+"("+request.get_json()["table"]+")")
	# db.session.add(me)
	# db.session.commit()
	

@app.route("/api/v1/rides/<rideId>",methods=["POST"])
def join_rides(rideId):
		ur=request.url_root
		#datetime_object = datetime.strptime(request.get_json()['timestamp'], '%d-%m-%Y:%S-%M-%H')
		#print(request.gset_json()['username'],request.get_json()['password'])
		try:
			data={'table':'Ridetake','insert':[rideId,request.get_json()['username']]}
			# print(data)
		except:
			return ('Missing Parameter',status.HTTP_400_BAD_REQUEST)
		
		r=requests.post(ur+'api/v1/db/write',json=data )
		
		# print(r.status_code)
		if r.status_code==500:
			return ("User/Ride Not Found",status.HTTP_400_BAD_REQUEST)
		return (jsonify())	
	#except:
	#	abort(400)
@app.route("/api/v1/rides/<rideId>")
def ride_detail(rideId):
	#try:
		ur=request.url_root
		try:
			data={"table": "Ride","columns": ["created_by","rideid","timestamp","source","destination"],"where": "Ride.rideid=="+rideId}
			# print(data)
		except:
			return ('Missing Parameter',status.HTTP_400_BAD_REQUEST)
		r=requests.post(ur+'api/v1/db/read',json=data )
		d=r.json()[0]

		data={"table": "Ridetake","columns": ["user"],"where": "Ride.rideid=="+rideId}
		# print(data)
		r=requests.post(ur+'api/v1/db/read',json=data )
		user=(r.json())
		d["users"]=[x["user"] for x in user ]
		if r.status_code==500:
			return ("Ride Not Found",status.HTTP_400_BAD_REQUEST)
		
		return (jsonify(d))	
	#except:
	#	abort(400)

	#
	# me = exec(request.get_json()["table"]+"("+request.get_json()["table"]+")")
	# db.session.add(me)
	# db.session.commit()

@app.route("/api/v1/users/<username>",methods=["DELETE"])
def del_user(username):
	#try:
		# ur=request.url_root
		# #datetime_object = datetime.strptime(request.get_json()['timestamp'], '%d-%m-%Y:%S-%M-%H')
		# #print(request.gset_json()['username'],request.get_json()['password'])
		# # print(request.args.get('source'))
		# data={"table": "User","columns": ["username","password"],"where": "User.username=='"+username+"'"}
		# print(data)
		# r=requests.post(ur+'api/v1/db/read',json=data )
		# d=r.json()
		# for i in d:
		# 		o=User(i['username'],i['password'])
		# 		db.session.delete(o)
		# db.session.commit()
		# return (jsonify())	
	#except:
	#	abort(400)

	#
	# me = exec(request.get_json()["table"]+"("+request.get_json()["table"]+")")
	# db.session.add(me)
	# db.session.commit()
	a=User.query.filter(User.username==username).first()
	print(a)
	if(a==None):
		return('Username Not found',status.HTTP_400_BAD_REQUEST)
	db.session.delete(a)
	db.session.commit()	
	return(jsonify())

@app.route("/api/v1/rides/<rideId>",methods=["DELETE"])
def del_ride(rideId):
	#try:
		# ur=request.url_root
		#datetime_object = datetime.strptime(request.get_json()['timestamp'], '%d-%m-%Y:%S-%M-%H')
		#print(request.gset_json()['username'],request.get_json()['password'])
		# print(request.args.get('source'))
		# data={"table": "Ride","columns":["created_by","rideid","timestamp","source","destination"],"where": "Ride.rideid=="+rideId}
		# print(data)
		# r=requests.post(ur+'api/v1/db/read',json=data )
		# print(r)
		# d=r.json()
		# for i in d:
		# 		o=Ride(i['rideid'],i['source'],i['destination'],i['timestamp'],i['created_by'])		
		# 		db.session.delete(o)
		# db.session.commit()
		# return (jsonify())	
	#except:
	#	abort(400)

	#
	# me = exec(request.get_json()["table"]+"("+request.get_json()["table"]+")")
	# db.session.add(me)
	# db.session.commit()
	b=Ride.query.filter(Ride.rideid==rideId).first()
	if(b==None):
		return('Username Not found',status.HTTP_400_BAD_REQUEST)
	
	# ?print(b)
	db.session.delete(b)
	db.session.commit()	
	return(jsonify())
	


if __name__ == '__main__':	
	app.debug=True
