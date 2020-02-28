import os
from flask import Flask, request, jsonify, make_response
from flask import render_template, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
#import jwt
import datetime
from functools import wraps
from sqlalchemy import Column, Integer, DateTime
import re
import requests
import json
#import pandas as pd

#df=pd.read_csv("/User
d={
1 : ' Kempegowda Ward ',
2 : ' Chowdeswari Ward ',
3 : ' Atturu ',
4 : ' Yelahanka Satellite Town ',
5 : ' Jakkuru ',
6 : ' Thanisandra ',
7 : ' Byatarayanapura ',
8 : ' Kodigehalli ',
9 : ' Vidyaranyapura ',
10 : ' Dodda Bommasandra ',
11 : ' Kuvempu Nagar ',
12 : ' Shettihalli ',
13 : ' Mallasandra ',
14 : ' Bagalakunte ',
15 : ' T Dasarahalli ',
16 : ' Jalahalli ',
17 : ' J P Park ',
18 : ' Radhakrishna Temple Ward ',
19 : ' SanJayanagar ',
20 : ' Ganga Nagar ',
21 : ' Hebbala ',
22 : ' Vishwanath Nagenahalli ',
23 : ' Nagavara ',
24 : ' HBR Layout ',
25 : ' Horamavu ',
26 : ' Ramamurthy Nagar ',
27 : ' Banasavadi ',
28 : ' Kammanahalli ',
29 : ' Kacharkanahalli ',
30 : ' Kadugondanahalli ',
31 : ' Kushal Nagar ',
32 : ' Kaval Bairasandra ',
33 : ' Manorayana Palya ',
34 : ' Gangenahalli ',
35 : ' Aramane Nagara ',
36 : ' Mattikere ',
37 : ' Yeshwanthpura ',
38 : ' HMT Ward ',
39 : ' Chokkasandra ',
40 : ' Dodda Bidarakallu ',
41 : ' Peenya Industrial Area ',
42 : ' Lakshmi Devi Nagar ',
43 : ' Nandini Layout ',
44 : ' Marappana Palya ',
45 : ' Malleshwaram ',
46 : ' Jayachamarajendra Nagar ',
47 : ' Devara Jeevanahalli ',
48 : ' Muneshwara Nagar ',
49 : ' Lingarajapura ',
50 : ' Benniganahalli ',
51 : ' Vijnanapura ',
52 : ' KR Puram ',
53 : ' Basavanapura ',
54 : ' Hudi ',
55 : ' Devasandra ',
56 : ' A Narayanapura ',
57 : ' C.V. Raman Nagar ',
58 : ' New Tippa Sandra ',
59 : ' Maruthi Seva Nagar ',
60 : ' Sagayara Puram ',
61 : ' SK Garden ',
62 : ' Ramaswamy Palya ',
63 : ' Jaya Mahal ',
64 : ' Raj Mahal Guttahalli ',
65 : ' Kadu Malleshwar Ward ',
66 : ' Subramanya Nagar ',
67 : ' Nagapura ',
68 : ' Mahalakshmipuram ',
69 : ' Laggere ',
70 : ' Rajagopal Nagar ',
71 : ' Hegganahalli ',
72 : ' Herohalli ',
73 : ' Kottegepalya ',
74 : ' Shakthi Ganapathi Nagar ',
75 : ' Shankar Matt ',
76 : ' Gayithri Nagar ',
77 : ' Dattatreya Temple Ward ',
78 : ' Pulakeshi Nagar ',
79 : ' Sarvagna Nagar ',
80 : ' Hoysala Nagar ',
81 : ' Vijnana Nagar ',
82 : ' Garudachar palya ',
83 : ' Kadugodi ',
84 : ' Hagadur ',
85 : ' Dodda Nekkundi ',
86 : ' Marathahalli ',
87 : ' HAL Airport ',
88 : ' Jeevanbhima Nagar ',
89 : ' Jogupalya ',
90 : ' Halsoor ',
91 : ' Bharathi Nagar ',
92 : ' Shivaji Nagar ',
93 : ' Vasanth Nagar ',
94 : ' Gandhi Nagar ',
95 : ' Subhash Nagar ',
96 : ' Okalipuram ',
97 : ' Dayananda Nagar ',
98 : ' Prakash Nagar ',
99 : ' Rajaji Nagar ',
100 : ' Basaveshwara Nagar ',
101 : ' Kamakshipalya ',
102 : ' Vrisahbhavathi Nagar ',
103 : ' Kaveripura ',
104 : ' Govindaraja Nagar ',
105 : ' Agrahara Dasarahalli ',
106 : ' Dr.Raj Kumar Ward ',
107 : ' Shiva Nagar ',
108 : ' Sri Rama Mandir Ward ',
109 : ' Chickpete ',
110 : ' Sampangiram Nagar ',
111 : ' Shantala Nagar ',
112 : ' Domlur ',
113 : ' Konena Agrahara ',
114 : ' Agaram ',
115 : ' Vannar Pet ',
116 : ' Nilasandra ',
117 : ' Shanthi Nagar ',
118 : ' Sudham Nagar ',
119 : ' Dharmaraya Swamy Temple ',
120 : ' Cottonpete ',
121 : ' Binni Pete ',
122 : ' Kempapura Agrahara ',
123 : ' ViJayanagar ',
124 : ' Hosahalli ',
125 : ' Marenahalli ',
126 : ' Maruthi Mandir Ward ',
127 : ' Mudalapalya ',
128 : ' Nagarabhavi ',
129 : ' Jnana Bharathi Ward ',
130 : ' Ullalu ',
131 : ' Nayandahalli ',
132 : ' Attiguppe ',
133 : ' Hampi Nagar ',
134 : ' Bapuji Nagar ',
135 : ' Padarayanapura ',
136 : ' Jagajivanaram Nagar ',
137 : ' Rayapuram ',
138 : ' Chelavadi Palya ',
139 : ' KR Market ',
140 : ' Chamraja Pet ',
141 : ' Azad Nagar ',
142 : ' Sunkenahalli ',
143 : ' Vishveshwara Puram ',
144 : ' Siddapura ',
145 : ' Hombegowda Nagar ',
146 : ' Lakkasandra ',
147 : ' Adugodi ',
148 : ' Ejipura ',
149 : ' Varthur ',
150 : ' Bellanduru ',
151 : ' Koramangala ',
152 : ' Suddagunte Palya ',
153 : ' Jayanagar ',
154 : ' Basavanagudi ',
155 : ' Hanumanth Nagar ',
156 : ' Sri Nagar ',
157 : ' Gali Anjenaya Temple Ward ',
158 : ' Deepanjali Nagar ',
159 : ' Kengeri ',
160 : ' Raja Rajeshawari Nagar ',
161 : ' Hosakerehalli ',
162 : ' Giri Nagar ',
163 : ' Katriguppe ',
164 : ' Vidya Peeta Ward ',
165 : ' Ganesh Mandir Ward ',
166 : ' Kari Sandra ',
167 : ' Yediyur ',
168 : ' Pattabhi Ram Nagar ',
169 : ' Byra Sandra ',
170 : ' Jayanagar East ',
171 : ' Gurappana Palya ',
172 : ' Madivala ',
173 : ' Jakka Sandra ',
174 : ' HSR Layout ',
175 : ' Bommanahalli ',
176 : ' BTM Layout ',
177 : ' JP Nagar ',
178 : ' Sarakki ',
179 : ' Shakambari Narar ',
180 : ' Banashankari Temple Ward ',
181 : ' Kumara Swamy Layout ',
182 : ' Padmanabha Nagar ',
183 : ' Chikkala Sandra ',
184 : ' Uttarahalli ',
185 : ' Yelchenahalli ',
186 : ' Jaraganahalli ',
187 : ' Puttenahalli ',
188 : ' Bilekhalli ',
189 : ' Honga Sandra ',
190 : ' Mangammana Palya ',
191 : ' Singa Sandra ',
192 : ' Begur ',
193 : ' Arakere ',
194 : ' Gottigere ',
195 : ' Konankunte ',
196 : ' Anjanapura ',
197 : ' Vasanthpura ',
198 : ' Hemmigepura '
}

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
res=app.test_client()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'thisissecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'tutorial.db')
db = SQLAlchemy(app)
headers={"Content-Type":"application/json"}
class MyDateTime(db.TypeDecorator):
    impl = db.DateTime
    def process_bind_param(self, value, dialect):
        if type(value) is str:
            return datetime.datetime.strptime(value, '%d-%m-%Y:%S-%M-%H')
        return value
#CREATING USER
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(80))

#CREATING RIDER
class Rider(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_by = db.Column(db.String(50))
    timestamp = db.Column(MyDateTime, default=datetime.datetime.now)
    source = db.Column(db.Integer)
    destination = db.Column(db.Integer)

class Shared(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ride_id = db.Column(db.Integer)
    shared_by = db.Column(db.String(50))

#API:1
@app.route('/api/v1/users', methods=['PUT'])
def create_user():
    data = request.get_json()
    if db.session.query(User).filter_by(name=data['name']).count():
        abort(405)
    pattern = re.compile(r'\b[0-9a-f]{40}\b')
    if(bool(pattern.match(data['password']))!=True):
        abort(405)
    print(data["name"])
    requests.post("http://127.0.0.1:4010/api/v1/db/write", json={"api":"1","name":data['name'],"password":data['password']},headers=headers)
    return {},201

#API:2
@app.route('/api/v1/users/<string:username>', methods=['DELETE'])
def remove_user(username):
    if db.session.query(User).filter_by(name=username).count():
        requests.post("http://127.0.0.1:4010/api/v1/db/write", json ={"api":"2","name":username})
        return {},200
    else:
        abort(405)

#API:3
@app.route('/api/v1/rides', methods=['POST'])
def create_rider():
    data = request.get_json()
    if request.method == 'POST':
        if ((db.session.query(User).filter_by(name=data['created_by']).count()) and (data['source'] in d )and data['destination'] in d):
            requests.post("http://127.0.0.1:4010/api/v1/db/write", json ={"api":"3","created_by":data['created_by'], "timestamp":data['timestamp'], "source":data['source'], "destination":data['destination']},headers=headers)
            return {},201
    else:
        abort(405)


#API:5,6,7
@app.route('/api/v1/rides/<int:ride_id>',methods=['GET','DELETE','POST'])
def list_ride(ride_id):
    if request.method == 'GET':
        if db.session.query(Rider).filter_by(id=ride_id).count():
            r=requests.post("http://127.0.0.1:4010/api/v1/db/read", json ={"api":"5","ride_id":ride_id},headers=headers)
            return r.json(),200
        else:
            return {},204
    elif request.method == 'POST':
        if db.session.query(Rider).filter_by(id=ride_id).count() and db.session.query(User).filter_by(name=request.get_json()['username']).one():
            requests.post("http://127.0.0.1:4010/api/v1/db/write", json ={"api":"6","ride_id":ride_id,"shared_by":request.get_json()['username']},headers=headers)
            return {},201
        else:
            return {},204
    elif request.method == 'DELETE':
        if db.session.query(Rider).filter_by(id=ride_id).count():
            return {},200
    else:
        abort(405)

#API:8
@app.route('/api/v1/db/write', methods=['POST'])
def write_db():
    data = request.get_json()
    if(data['api']=="1"):
        new_user = User( name=data['name'], password=data['password'])
        db.session.add(new_user)
        db.session.commit()
    if(data['api']=="2"):
        user_delete= db.session.query(User).filter_by(name=data['name']).one()
        db.session.delete(user_delete)
        db.session.commit()
    if(data['api']=="3"):
        new_rider= Rider( created_by=data['created_by'], timestamp=data['timestamp'], source=data['source'], destination=data['destination'])
        db.session.add(new_rider)
        db.session.commit()
    if(data['api']=="6"):
        new_shared = Shared(ride_id=data['ride_id'],shared_by=data['shared_by'])
        db.session.add(new_shared)
        db.session.commit()
    if(data['api']=="7"):
        rider_delete= db.session.query(Rider).filter_by(id=data['ride_id']).one()
        db.session.delete(rider_delete)
        db.session.commit()

@app.route('/api/v1/db/read', methods=['POST'])
def read_db():
    if(data['api']=="5"):
        ride = db.session.query(Rider).filter_by(id=data['ride_id']).one()
        shared = db.session.query(Shared).filter_by(ride_id=data['ride_id']).all()
        l=[]
        for share in shared:
            l.append(share.shared_by)
        return jsonify(ride_Id=ride.id,Created_by=ride.created_by,users=l,Timestamp=ride.timestamp,source=d[ride.source],destination=d[ride.destination])

@app.route('/test',methods=['GET'])
def test():
	return "hello"

if __name__ == '__main__':
    app.run(host='3.81.137.167',port=80,debug=True)
