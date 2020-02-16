from flaskapp import app
import json
from datetime import datetime
from datetime import timedelta
import unittest

class FlaskTestCase(unittest.TestCase):

    #Test if index page is working
    def test_A_index(self):
        tester = app.test_client(self)
        response = tester.get('/cc', content_type='html/text')
        self.assertTrue(b'Welcome to our submission for Assignment 1' in response.data)

    #Test correct user insert
    def test_B1_insert_user(self):
        tester = app.test_client(self)
        info = {"username":"UTest", "password":"3e725109c7e7c0bfb9d709836735b56d943d263a"} 
        response = tester.put('/api/v1/users', data=json.dumps(info), headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code,201)

    #Test for incorrect password
    def test_B2_insert_user(self):
        tester = app.test_client(self)
        info = {"username":"UTest_dup", "password":"Incorrect_pass"} 
        response = tester.put('/api/v1/users', data=json.dumps(info), headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code,400)
    
    #Test for user already exists
    def test_B3_user_exists(self):
        tester = app.test_client(self)
        info = {"username":"UTest", "password":"3e725109c7e7c0bfb9d709836735b56d943d263e"}
        response = tester.put('api/v1/users', data=json.dumps(info), headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 400)

    #Test correct ride insert
    def test_C1_insert_ride(self):
        tester = app.test_client(self)      
        now = datetime.now() + timedelta(days=1)
        info = {"created_by":"UTest", "timestamp":now.strftime("%d-%m-%Y:%S-%M-%H"),"source":"3", "destination":"197"} 
        response = tester.post('/api/v1/rides', data=json.dumps(info), headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code,201)

    #Test for non existing user ride insert
    def test_C2_insert_ride(self):
        tester = app.test_client(self)      
        now = datetime.now()+ timedelta(days=1)
        info = {"created_by":"UTest_dup", "timestamp":now.strftime("%d-%m-%Y:%S-%M-%H"),"source":"3", "destination":"197"} 
        response = tester.post('/api/v1/rides', data=json.dumps(info), headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code,400)

    #Test for incorrect value of source above max value
    def test_C3_insert_ride(self):
        tester = app.test_client(self)      
        now = datetime.now() + timedelta(days=1) 
        info = {"created_by":"UTest", "timestamp":now.strftime("%d-%m-%Y:%S-%M-%H"),"source":"200", "destination":"197"} 
        response = tester.post('/api/v1/rides', data=json.dumps(info), headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code,400)

    #Test for incorrect value of source below min value
    def test_C4_insert_ride(self):
        tester = app.test_client(self)      
        now = datetime.now() + timedelta(days=1) 
        info = {"created_by":"UTest", "timestamp":now.strftime("%d-%m-%Y:%S-%M-%H"),"source":"0", "destination":"197"} 
        response = tester.post('/api/v1/rides', data=json.dumps(info), headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code,400)

    #Test for incorrect value of destination above max value
    def test_C5_insert_ride(self):
        tester = app.test_client(self)      
        now = datetime.now() + timedelta(days=1) 
        info = {"created_by":"UTest", "timestamp":now.strftime("%d-%m-%Y:%S-%M-%H"),"source":"3", "destination":"200"} 
        response = tester.post('/api/v1/rides', data=json.dumps(info), headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code,400)

    #Test for incorrect value of destination below min value
    def test_C6_insert_ride(self):
        tester = app.test_client(self)      
        now = datetime.now() + timedelta(days=1)
        info = {"created_by":"UTest", "timestamp":now.strftime("%d-%m-%Y:%S-%M-%H"),"source":"3", "destination":"0"} 
        response = tester.post('/api/v1/rides', data=json.dumps(info), headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code,400)

    #Test correct rides list
    def test_D1_list_rides(self):
        tester = app.test_client(self)
        response = tester.get('/api/v1/rides?source={source}&destination={destination}'.format(source=3,destination=197))
        self.assertEqual(response.status_code,200)

    #Test for valid but incorrect source and destination
    def test_D2_list_rides(self):
        tester = app.test_client(self)
        response = tester.get('/api/v1/rides?source={source}&destination={destination}'.format(source=1,destination=2))
        self.assertEqual(response.status_code,204)
    
    #Test for invalid source upper bound 
    def test_D3_list_rides(self):
        tester = app.test_client(self)
        response = tester.get('/api/v1/rides?source={source}&destination={destination}'.format(source=200,destination=197))
        self.assertEqual(response.status_code,400)
    
    #Test for invalid destination upper bound
    def test_D4_list_rides(self):
        tester = app.test_client(self)
        response = tester.get('/api/v1/rides?source={source}&destination={destination}'.format(source=3,destination=200))
        self.assertEqual(response.status_code,400)

    #Test for invalid source lower bound 
    def test_D5_list_rides(self):
        tester = app.test_client(self)
        response = tester.get('/api/v1/rides?source={source}&destination={destination}'.format(source=0,destination=197))
        self.assertEqual(response.status_code,400)
    
    #Test for invalid destination lower bound
    def test_D6_list_rides(self):
        tester = app.test_client(self)
        response = tester.get('/api/v1/rides?source={source}&destination={destination}'.format(source=3,destination=0))
        self.assertEqual(response.status_code,400)

    #Test correct given ride list
    def test_E1_given_ride(self):
        tester = app.test_client(self)
        response = tester.get('/api/v1/rides/{rideId}'.format(rideId=1))
        self.assertEqual(response.status_code,200)
    
    #Test for nonexisting rideId
    def test_E2_given_ride(self):
        tester = app.test_client(self)
        response = tester.get('/api/v1/rides/{rideId}'.format(rideId=999))
        self.assertEqual(response.status_code,204)

    #Test correct join ride
    def test_F1_join_ride(self):
        tester = app.test_client(self)
        info = {"username":"UTest"}
        response = tester.post('/api/v1/rides/{rideId}'.format(rideId=1),data=json.dumps(info),headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code,200)

    #Test for nonexisting user
    def test_F2_join_ride(self):
        tester = app.test_client(self)
        info = {"username":"UTest_dup"}
        response = tester.post('/api/v1/rides/{rideId}'.format(rideId=2),data=json.dumps(info),headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code,400)

    #Test for nonexisitng rideId
    def test_F3_join_ride(self):
        tester = app.test_client(self)
        info = {"username":"UTest"}
        response = tester.post('/api/v1/rides/{rideId}'.format(rideId=999),data=json.dumps(info),headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code,400)

    #Test correct delete ride
    def test_G1_delete_ride(self):
        tester = app.test_client(self)
        response = tester.delete('/api/v1/rides/{rideId}'.format(rideId=1))
        self.assertEqual(response.status_code,200)

    #Test for nonexisting rideId
    def test_G2_delete_ride(self):
        tester = app.test_client(self)
        response = tester.delete('/api/v1/rides/{rideId}'.format(rideId=999))
        self.assertEqual(response.status_code,400)

    #Test for correct delete user
    def test_H1_delete_user(self):
        tester = app.test_client(self)
        response = tester.delete('/api/v1/users/{username}'.format(username="UTest"))
        self.assertEqual(response.status_code,200)

    #Test for deleting non existing user
    def test_H2_delete_user(self):
        tester = app.test_client(self)
        response = tester.delete('/api/v1/users/{username}'.format(username="UTest_dup"))
        self.assertEqual(response.status_code,400)

if __name__ == '__main__':
    unittest.main()


