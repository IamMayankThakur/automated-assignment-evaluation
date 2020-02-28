import app_server
import copy
import constants
import hashlib
import json
import mysql.connector
import responses
import requests
import unittest

from app_server import app
from datetime import datetime
from unittest import mock

# Test users.
username_1 = "abc"
password_1 =  hashlib.sha1("abc".encode()).hexdigest()

username_2 = "xyz"
password_2 =  hashlib.sha1("xyz".encode()).hexdigest()

username_3 = "def"
password_3 =  hashlib.sha1("def".encode()).hexdigest()

username_non_sha = "ijk"
password_non_sha = "password"

# Test Rides.
ride_invalid_time_format = dict(
    created_by = username_1,
    source = "1",
    destination = "2",
    timestamp = "9-18-32:2-12-2020")

ride_past_time = dict(
    created_by = username_1,
    source = "1",
    destination = "2",
    timestamp = "2-12-2000:9-18-32")

ride_base = dict(
    created_by = username_1,
    timestamp = "2-12-2021:9-18-32")
    
ride_invalid_src = copy.deepcopy(ride_base)
ride_invalid_src["source"] = "-1"
ride_invalid_src["destination"] = "1"

ride_valid_1 = copy.deepcopy(ride_base)
ride_valid_1["source"] = "1"
ride_valid_1["destination"] = "2"

ride_valid_2 = copy.deepcopy(ride_base)
ride_valid_2["source"] = "2"
ride_valid_2["destination"] = "3"

class AppServerUnitTests(unittest.TestCase):

    def setUp(self):
        app.config['DATABASE'] = "TestRideShare"
        self.app = app.test_client()

        # Setting up database.
        try:
            self.ride_share_db = mysql.connector.connect(host = "localhost",user = "admin",passwd="admin@123")
            self.cursor = self.ride_share_db.cursor()
            self.cursor.execute("DROP DATABASE IF EXISTS TestRideShare;")
            self.cursor.execute("CREATE DATABASE TestRideShare;")
            self.cursor.close()
            self.ride_share_db.commit()

            self.ride_share_db = mysql.connector.connect(host="localhost",user="admin",passwd="admin@123",database="TestRideShare")
            self.cursor = self.ride_share_db.cursor(buffered = True)
            self.cursor.execute("DROP TABLE IF EXISTS USERS;")
            self.cursor.execute("CREATE TABLE USERS (username VARCHAR(255) PRIMARY KEY,password VARCHAR(255));")
            self.cursor.execute("DROP TABLE IF EXISTS RIDES;")
            self.cursor.execute("CREATE TABLE RIDES (rideId INT AUTO_INCREMENT PRIMARY KEY,created_by VARCHAR(255),timestamp VARCHAR(255),source INT,destination INT);")
            self.cursor.execute("DROP TABLE IF EXISTS RIDERS;")
            self.cursor.execute("CREATE TABLE RIDERS (rideId INT, username VARCHAR(255),FOREIGN KEY (username) REFERENCES USERS(username),FOREIGN KEY (rideId) REFERENCES RIDES(rideId));") 
            self.cursor.close()
            self.ride_share_db.commit()

            self.cursor = self.ride_share_db.cursor(buffered = True)
            self.cursor.execute("INSERT INTO USERS (username, password) VALUES ('{}','{}');".format(username_1, password_1))
            self.cursor.execute("INSERT INTO USERS (username, password) VALUES ('{}','{}');".format(username_2, password_2))
            self.cursor.execute("INSERT INTO {} ({}) VALUES ({})".format(
                "RIDES",
                "created_by, source, destination, timestamp",
                "'{}', '{}', '{}', '{}'".format(
                    ride_valid_2["created_by"],
                    ride_valid_2["source"],
                    ride_valid_2["destination"],
                    ride_valid_2["timestamp"])))
            self.cursor.close()
            self.ride_share_db.commit()

        except Exception as e:
            print(e)

    def test_main_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
    
    # Unit tests for API 1
    
    def test_API1_not_allowed(self):
        """API 1 ~ Send request using wrong method.
        Response with status code 405 expected."""
        response = self.app.post(
            constants.API1_URL,
            json = dict(
                username = username_3,
                password = password_3),
            mimetype = 'application/json')

        self.assertEqual(response.status_code, 405)

    def test_API1_missing(self):
        """API 1 ~ Send request with missing values.
        Response with status code 400 expected."""
        response = self.app.put(
            constants.API1_URL,
            json = dict(),
            mimetype = 'application/json')

        self.assertEqual(response.status_code, 400)

    @responses.activate
    def test_API1_repeated_username(self):
        """API 1 ~ Send request using repeated username.
        Response with status code 400 expected."""
        responses.add(
            responses.POST, 
            constants.API_URL + constants.API9_URL,
            json={'query_result': [username_1]},
            status=200)

        response = self.app.put(
            constants.API1_URL,
            json = dict(
                username = username_1,
                password = password_1),
            mimetype = 'application/json')

        self.assertEqual(response.status_code, 400)

    def test_API1_invalid_password(self):
        """API 1 ~ Send request using invalid password.
        Response with status code 400 expected."""
        response = self.app.put(
            constants.API1_URL,
            json = dict(
                username = username_non_sha,
                password = password_non_sha),
            mimetype = 'application/json')

        self.assertEqual(response.status_code, 400)

    @responses.activate
    def test_API1_valid(self):
        """API 1 ~ Send valid request.
        Response with status code 200 expected."""
        responses.add(
            responses.POST, 
            constants.API_URL + constants.API9_URL,
            json = {'query_result': []},
            status = 200)

        responses.add(
            responses.POST, 
            constants.API_URL + constants.API8_URL,
            json = {},
            status = 200)

        response = self.app.put(
            constants.API1_URL,
            json = dict(
                username = username_3,
                password = password_3),
            mimetype = 'application/json')

        self.assertEqual(response.status_code, 201)

    # Unit tests for API 2
    
    def test_API2_not_allowed(self):
        """API 2 ~ Send request using wrong method.
        Response with status code 405 expected."""
        response = self.app.post("{}/{}".format(
                constants.API2_URL,
                username_1),
            mimetype = 'application/json')

        self.assertEqual(response.status_code, 405)
    
    @responses.activate
    def test_API2_nonexisting_user(self):
        """API 2 ~ Send request with invalid user.
        Response with status code 400 expected."""
        responses.add(
            responses.POST, 
            constants.API_URL + constants.API9_URL,
            json = {'query_result': []},
            status = 200)

        responses.add(
            responses.POST, 
            constants.API_URL + constants.API8_URL,
            json = {},
            status = 200)

        response = self.app.delete("{}/{}".format(
                constants.API2_URL,
                username_3),
            mimetype = 'application/json')

        self.assertEqual(response.status_code, 400)    
    
    @responses.activate
    def test_API2_valid(self):
        """API 2 ~ Send request with valid user.
        Response with status code 200 expected."""
        responses.add(
            responses.POST, 
            constants.API_URL + constants.API9_URL,
            json = {'query_result': [username_1]},
            status = 200)

        responses.add(
            responses.POST, 
            constants.API_URL + constants.API8_URL,
            json = {},
            status = 200)

        response = self.app.delete("{}/{}".format(
                constants.API2_URL,
                username_3),
            mimetype = 'application/json')
    
        self.assertEqual(response.status_code, 200)    

    # Unit tests for API 3

    def test_API3_not_allowed(self):
        """API 3 ~ Send request using wrong method.
        Response with status code 405 expected."""
        response = self.app.put(
            constants.API3_URL,
            json = dict(
                username = username_3,
                password = password_3),
            mimetype = 'application/json')

        self.assertEqual(response.status_code, 405)

    def test_API3_missing(self):
        """API 3 ~ Send request with missing values.
        Response with status code 400 expected."""
        response = self.app.post(
            constants.API3_URL,
            json = dict(),
            mimetype = 'application/json')

        self.assertEqual(response.status_code, 400)

    @responses.activate
    def test_API3_invalid_timestamp(self):
        """API 3 ~ Send request using invalid timestamp.
        Response with status code 400 expected."""
        responses.add(
            responses.POST, 
            constants.API_URL + constants.API9_URL,
            json={'query_result': [username_1]},
            status=200)

        response = self.app.post(
            constants.API3_URL,
            json = ride_invalid_time_format,
            mimetype = 'application/json')

        self.assertEqual(response.status_code, 400)

    @responses.activate
    def test_API3_invalid_source(self):
        """API 3 ~ Send request using invalid source.
        Response with status code 400 expected."""
        responses.add(
            responses.POST, 
            constants.API_URL + constants.API9_URL,
            json={'query_result': [username_1]},
            status=200)

        response = self.app.post(
            constants.API3_URL,
            json = ride_invalid_src,
            mimetype = 'application/json')

        self.assertEqual(response.status_code, 400)

    @responses.activate
    def test_API3_valid(self):
        """API 3 ~ Send valid request.
        Response with status code 201 expected."""
        responses.add(
            responses.POST, 
            constants.API_URL + constants.API9_URL,
            json = {'query_result': [username_1]},
            status = 200)

        responses.add(
            responses.POST, 
            constants.API_URL + constants.API8_URL,
            json = {},
            status = 200)

        response = self.app.post(
            constants.API3_URL,
            json = ride_valid_1,
            mimetype = 'application/json')

        self.assertEqual(response.status_code, 201)
    
    # Unit tests for API 4

    def test_API4_not_allowed(self):
        """API 4 ~ Send request using wrong method.
        Response with status code 405 expected."""
        response = self.app.delete(
            constants.API4_URL,
            mimetype = 'application/json')

        self.assertEqual(response.status_code, 405)

    @responses.activate
    def test_API4_valid(self):
        """API 4 ~ Send valid request.
        Adding source and destination such that 
        one is in the future and other in past.
        Response with status code 200 expected."""
        ride_valid_1.update(dict(rideId = "1"))
        ride_past_time.update(dict(rideId = "2"))
        query_result = [
            [ride_valid_1["rideId"],
                ride_valid_1["created_by"],
                ride_valid_1["timestamp"]],
            [ride_past_time["rideId"],
                ride_past_time["created_by"],
                ride_past_time["timestamp"]]]

        expected_response = dict(
                    rideId = ride_valid_1["rideId"],
                    username = ride_valid_1["created_by"],
                    timestamp = ride_valid_1["timestamp"])
        responses.add(
            responses.POST, 
            constants.API_URL + constants.API9_URL,
            json = {'query_result': query_result},
            status = 200)

        response = self.app.get(
            constants.API4_URL + 
                "?source={}&destination={}".format(1,2),
            mimetype = 'application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json()[0]['rideId'],
            expected_response['rideId'])        
        self.assertEqual(
            response.get_json()[0]['username'],
            expected_response['username'])
        self.assertEqual(
            response.get_json()[0]['timestamp'],
            expected_response['timestamp'])

    @responses.activate
    def test_API4_nomatch(self):
        """API 4 ~ Send request [204].
        No match response."""
        ride_past_time.update(dict(rideId = 2))
        query_result = [
            [ride_past_time["rideId"],
            ride_past_time["created_by"],
            ride_past_time["timestamp"]]]
        responses.add(
            responses.POST, 
            constants.API_URL + constants.API9_URL,
            json = {'query_result': query_result},
            status = 200)

        response = self.app.get(
            constants.API4_URL + 
                "?source={}&destination={}".format(1,2),
            mimetype = 'application/json')

        self.assertEqual(response.status_code, 204)
    
    # Unit tests for API 5
    
    def test_API5_not_allowed(self):
        """API 5 ~ Send request using wrong method.
        Response with status code 405 expected."""
        response = self.app.delete(
            constants.API5_URL,
            json = dict(
                username = username_3,
                password = password_3),
            mimetype = 'application/json')

        self.assertEqual(response.status_code, 405)

    @responses.activate
    def test_API5_nonexistantride(self):
        """API 5 ~ Send request using non existant ride.
        Response with status code 400 expected."""
        fake_ride = 1000
        responses.add(
            responses.POST, 
            constants.API_URL + constants.API9_URL,
            json={'query_result': []},
            status=200)

        response = self.app.get(
            constants.API5_URL + "/{}".format(fake_ride),
            mimetype = 'application/json')

        self.assertEqual(response.status_code, 400)

    # Unit tests for API 6
    
    def test_API6_not_allowed(self):
        """API 6 ~ Send request using wrong method.
        Response with status code 405 expected."""
        response = self.app.delete(
            constants.API6_URL,
            mimetype = 'application/json')

        self.assertEqual(response.status_code, 405)

    
    def test_API6_missing(self):
        """API 6 ~ Send request with missing values.
        Response with status code 400 expected."""
        response = self.app.post(
            constants.API6_URL + "/{}".format(1),
            json = dict(),
            mimetype = 'application/json')

        self.assertEqual(response.status_code, 400)
    
    @responses.activate
    def test_API6_nonexistant_ride(self):
        """API 6 ~ Send request using non existant ride.
        Response with status code 400 expected."""
        #username is valid, it is returned from API9.
        responses.add(
            responses.POST, 
            constants.API_URL + constants.API9_URL,
            json = {'query_result': [username_1]},
            status = 200)
        
        #rideId is invalid nothing is returned from API9.
        responses.add(
            responses.POST, 
            constants.API_URL + constants.API9_URL,
            json={'query_result': []},
            status=200)

        # fake ride with ride id -1
        response = self.app.post(
            constants.API6_URL + "/{}".format(-1),
            json = {"username" : username_1},
            mimetype = 'application/json')

        self.assertEqual(response.status_code, 400)

    @responses.activate
    def test_API6_nonexistant_user(self):
        """API 6 ~ Send request with invalid user.
        Response with status code 400 expected."""
        #username is invalid, nothing is returned.
        responses.add(
            responses.POST, 
            constants.API_URL + constants.API9_URL,
            json = {'query_result': []},
            status = 200)

        response = self.app.post(
            constants.API6_URL + "/{}".format(1),
            json = {"username" : username_3},
            mimetype = 'application/json')

        self.assertEqual(response.status_code, 400)

       
    @responses.activate
    def test_API6_valid(self):
        """API 6 ~ Send valid.
        Response with status code 200 expected."""
        rideId = 1
        #username is valid, it is returned from API9.
        responses.add(
            responses.POST, 
            constants.API_URL + constants.API9_URL,
            json = {'query_result': [username_2]},
            status = 200)
        
        #rideId is valid, it is returned from API9.
        responses.add(
            responses.POST, 
            constants.API_URL + constants.API9_URL,
            json = {'query_result': [(
                rideId,
                ride_valid_2["created_by"],
                ride_valid_2["timestamp"])]},
            status = 200)

        # API8 response
        responses.add(
            responses.POST, 
            constants.API_URL + constants.API8_URL,
            status = 200)

        response = self.app.post(
            constants.API6_URL + "/{}".format(rideId),
            json = {"username" : username_2},
            mimetype = 'application/json')

        self.assertEqual(response.status_code, 200)
    
    # Unit tests for API 7
    
    def test_API7_not_allowed(self):
        """API 7 ~ Send request using wrong method.
        Response with status code 405 expected."""
        response = self.app.patch("{}/{}".format(
                constants.API7_URL,
                1),
            mimetype = 'application/json')

        self.assertEqual(response.status_code, 405)
    
    @responses.activate
    def test_API7_nonexisting_ride(self):
        """API 7 ~ Send request with invalid ride.
        Response with status code 400 expected."""
        fake_ride = -1
        responses.add(
            responses.POST, 
            constants.API_URL + constants.API9_URL,
            json = {'query_result': []},
            status = 200)

        response = self.app.delete("{}/{}".format(
                constants.API7_URL,
                fake_ride),
            mimetype = 'application/json')

        self.assertEqual(response.status_code, 400)    
    
    @responses.activate
    def test_API7_valid(self):
        """API 7 ~ Send valid request.
        Response with status code 200 expected."""
        rideId = 1
        responses.add(
            responses.POST, 
            constants.API_URL + constants.API9_URL,
            json = {'query_result': [rideId]},
            status = 200)

        responses.add(
            responses.POST, 
            constants.API_URL + constants.API8_URL,
            json = {},
            status = 200)

        response = self.app.delete("{}/{}".format(
                constants.API7_URL,
                username_3),
            mimetype = 'application/json')
    
        self.assertEqual(response.status_code, 200)    

    # Unit tests for API 8

    def test_API8_empty_columns(self):
        """API 8 ~ Send request without columns.
        Response with status code 400 expected."""

        response = self.app.post(
            constants.API8_URL,
            json = dict(table = "RIDES"),
            mimetype = 'application/json')

        self.assertEqual(response.status_code, 400)

    def test_API8_empty_table(self):
        """API 8 ~ Send request without table name. 
        Response with status code 400 expected."""

        response = self.app.post(
            constants.API9_URL,
            json = dict(),
            mimetype = 'application/json')

        self.assertEqual(response.status_code, 400)
      
    def test_API8_invalid_operation(self):
        """API 8 ~ Send request without columns.
        Response with status code 400 expected."""

        response = self.app.post(
            constants.API8_URL,
            json = dict(
                columns = ["username", "password"],
                values = [username_2, password_2],
                operation = "NO_OP",
                table = "USERS"),
            mimetype = 'application/json')

        self.assertEqual(response.status_code, 400)

    def test_API8_insert(self):
        """API 8 ~ Test insert operation.
        Response with status code 200 expected."""

        response = self.app.post(
            constants.API8_URL,
            json = dict(
                columns = ["username", "password"],
                values = [username_3, password_3],
                operation = "INSERT",
                table = "USERS"),
            mimetype = 'application/json')

        self.assertEqual(response.status_code, 200)
        
    def test_API8_delete(self):
        """API 8 ~ Test delete operation.
        Response with status code 200 expected."""

        response = self.app.post(
            constants.API8_URL,
            json = dict(
                columns = ["username"],
                values = [username_2],
                operation = "DELETE",
                table = "USERS"),
            mimetype = 'application/json')

        self.assertEqual(response.status_code, 200)
        
    # Unit tests for API 9

    def test_API9_empty_columns(self):
        """API 9 ~ Send request without columns.
        Response with status code 400 expected."""

        response = self.app.post(
            constants.API9_URL,
            json = dict(table = "RIDES"),
            mimetype = 'application/json')

        self.assertEqual(response.status_code, 400)

    def test_API9_empty_table(self):
        """API 9 ~ Send request without table name. 
        Response with status code 400 expected."""

        response = self.app.post(
            constants.API9_URL,
            json = dict(),
            mimetype = 'application/json')

        self.assertEqual(response.status_code, 400)
    
    def test_API9_valid_request(self):
        """API 9 ~ Send valid request.
        Response with status code 200 expected.
        Entries added in setUp expected in response"""
        expected_result = [[username_1],[username_2]]
        response = self.app.post(
            constants.API9_URL,
            json = dict(
                columns = ["username"],
                table = "USERS"),
            mimetype = 'application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['query_result'], expected_result)
   
    def test_API9_valid_request(self):
        """API 9 ~ Send valid request with where clause.
        Response with status code 200 expected.
        Entry mathcing clause added in setUp expected in response"""
        expected_result = [[username_1]]
        response = self.app.post(
            constants.API9_URL,
                json = dict(
                columns = ["username"],
                table = "USERS",
                wheres = ["username = '{}'".format(username_1)]),
            mimetype = 'application/json')
    
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['query_result'], expected_result)
    
if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(AppServerUnitTests)
    unittest.TextTestRunner(verbosity = 2).run(suite)

