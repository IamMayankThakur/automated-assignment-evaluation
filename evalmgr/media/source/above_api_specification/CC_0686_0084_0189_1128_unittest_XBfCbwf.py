import unittest
import requests
import json


class TestStringMethods(unittest.TestCase):
    
    def test_adduser(self):
        
        api_data = {
            "username": "user1",
            "password": "b3daa77b4c04a9551b8781d03191fe098f325e67"
        }
        URL = "http://52.86.159.3/api/v1/users"
        object_returned = requests.put(URL,json=api_data)
        self.assertEqual(len(json.loads(object_returned.content.decode('UTF-8'))),0) #checking body content
        self.assertEqual(object_returned.status_code,201) #checking status code
        object_returned = requests.put(URL,json=api_data)
        self.assertEqual(object_returned.status_code,400) #checking status code while adding an existing user
        object_returned = requests.post(URL,json=api_data)
        self.assertEqual(object_returned.status_code,405) #checking status code for wrong method
        object_returned = requests.get(URL,json=api_data)
        self.assertEqual(object_returned.status_code,405) #checking status code for wrong method
        object_returned = requests.delete(URL,json=api_data)
        self.assertEqual(object_returned.status_code,405) #checking status code for wrong method
        #checking with a new username
        api_data["username"] = "user2"
        object_returned = requests.put(URL,json=api_data)
        self.assertEqual(len(json.loads(object_returned.content.decode('UTF-8'))),0) #checking body content
        self.assertEqual(object_returned.status_code,201) #checking status code

        #adding extra usernames for further testing
        extra_unames = ["user5","user6","user7","user8"]
        for i in extra_unames:
            api_data["username"] = i
            object_returned = requests.put(URL,json=api_data)
            self.assertEqual(len(json.loads(object_returned.content.decode('UTF-8'))),0) #checking body content
            self.assertEqual(object_returned.status_code,201) #checking status code



    def test_removeUser(self):
        URL = "http://52.86.159.3/api/v1/users/user1"
        object_returned = requests.delete(URL) #deleting user
        self.assertEqual(len(json.loads(object_returned.content.decode('UTF-8'))),0) #checking body content
        self.assertEqual(object_returned.status_code,200) #checking status code
        URL = "http://52.86.159.3/api/v1/users/user2"
        object_returned = requests.delete(URL) #deleting user
        self.assertEqual(len(json.loads(object_returned.content.decode('UTF-8'))),0) #checking body content
        self.assertEqual(object_returned.status_code,200) #checking status code
        URL = "http://52.86.159.3/api/v1/users/user1"
        object_returned = requests.delete(URL) #re-deleting user
        self.assertEqual(object_returned.status_code,400) #checking status code
        URL = "http://52.86.159.3/api/v1/users/user2"
        object_returned = requests.delete(URL) #re-deleting user
        self.assertEqual(object_returned.status_code,400) #checking status code
        object_returned = requests.post(URL)
        self.assertEqual(object_returned.status_code,405) #checking status code for wrong method
        object_returned = requests.get(URL)
        self.assertEqual(object_returned.status_code,405) #checking status code for wrong method
        object_returned = requests.put(URL)
        self.assertEqual(object_returned.status_code,405) #checking status code for wrong method



    def test_createNewRide(self):

        api_data = {
        "created_by" : "user5",
        "timestamp": "16-09-2020:11-11-12",
        "source" : "1",
        "destination" : "2"
        }
        URL = "http://52.86.159.3/api/v1/rides"
        object_returned = requests.post(URL,json=api_data)
        self.assertEqual(len(json.loads(object_returned.content.decode('UTF-8'))),0) #checking body content
        self.assertEqual(object_returned.status_code,201) #checking status code

        #creating another valid ride
        URL = "http://52.86.159.3/api/v1/rides"
        object_returned = requests.post(URL,json=api_data)
        self.assertEqual(len(json.loads(object_returned.content.decode('UTF-8'))),0) #checking body content
        self.assertEqual(object_returned.status_code,201) #checking status code


        object_returned = requests.post(URL) #not passing any data/invalid data
        self.assertEqual(object_returned.status_code,400) #checking status code

        #source and destination same
        api_data["destination"] = api_data["source"]
        object_returned = requests.post(URL,json=api_data) 
        self.assertEqual(object_returned.status_code,400) #checking status code

        #wrong ource and destination 
        api_data["destination"] = 99999
        object_returned = requests.post(URL,json=api_data) 
        self.assertEqual(object_returned.status_code,400) #checking status code

        #timestamp smaller than current time
        api_data["destination"] = 2 #correcting the destination
        api_data["timestamp"] = "01-01-2010:11-11-12"
        object_returned = requests.post(URL,json=api_data) 
        self.assertEqual(object_returned.status_code,400) #checking status code

        #wrong timestamp
        api_data["destination"] = 2 #correcting the destination
        api_data["timestamp"] = "31-02-2010:11-11-12"
        object_returned = requests.post(URL,json=api_data) 
        self.assertEqual(object_returned.status_code,400) #checking status code


        #wrong timestamp format
        api_data["destination"] = 2 #correcting the destination
        api_data["timestamp"] = "31-02-20110:11-121-12"
        object_returned = requests.post(URL,json=api_data) 
        self.assertEqual(object_returned.status_code,400) #checking status code


        #created by a nonexistent user 
        api_data["created_by"]  = "nonexistent_user"
        api_data["timestamp"] = "16-09-2020:11-11-12" #correcting time
        object_returned = requests.post(URL,json=api_data) 
        self.assertEqual(object_returned.status_code,400) #checking status code

        #not performing a method_405 check as two functions have the same flask route but different methods.
        #hence 405 will never be returned.

    
    def test_listrides(self):

        URL = "http://52.86.159.3/api/v1/rides?source=1&destination=2"
        object_returned = requests.get(URL)
        self.assertEqual(type(json.loads(object_returned.content.decode('UTF-8'))),list) #list of dictionaries will be returned
        self.assertEqual(object_returned.status_code,200) #checking status code

        #passing wrong area codes
        URL = "http://52.86.159.3/api/v1/rides?source=9999&destination=9999"
        object_returned = requests.get(URL)
        self.assertEqual(object_returned.status_code,400) #checking status code

        #retrieving non-existant rides
        URL = "http://52.86.159.3/api/v1/rides?source=44&destination=45"
        object_returned = requests.get(URL)
        self.assertEqual(object_returned.status_code,204) #checking status code



    def test_listGivenRide(self):

        URL = "http://52.86.159.3/api/v1/rides/1"
        object_returned = requests.get(URL)
        self.assertEqual(object_returned.status_code,200) #checking status code

        URL = "http://52.86.159.3/api/v1/rides/10" #non-existent ride ID
        object_returned = requests.get(URL)
        self.assertEqual(object_returned.status_code,400) #checking status code

    def test_joinExisting(self):

        api_data = {
            "username" : "user6"
        }
        URL = "http://52.86.159.3/api/v1/rides/1"
        object_returned = requests.post(URL,json=api_data)
        self.assertEqual(object_returned.status_code,200) #checking status code

        #wrong rideID
        URL = "http://52.86.159.3/api/v1/rides/10"
        object_returned = requests.post(URL,json=api_data)
        self.assertEqual(object_returned.status_code,400) #checking status code

        #wrong username
        URL = "http://52.86.159.3/api/v1/rides/1"
        api_data["username"] = "non_existent_username"
        object_returned = requests.post(URL,json=api_data)
        self.assertEqual(object_returned.status_code,400) #checking status code

    def test_deleteRide(self):

        URL = "http://52.86.159.3/api/v1/rides/2"
        object_returned = requests.delete(URL)
        self.assertEqual(object_returned.status_code,200) #checking status code

        #wrong rideID
        URL = "http://52.86.159.3/api/v1/rides/10"
        object_returned = requests.delete(URL)
        self.assertEqual(object_returned.status_code,400) #checking status code

        #re-deleting ride
        URL = "http://52.86.159.3/api/v1/rides/2"
        object_returned = requests.delete(URL)
        self.assertEqual(object_returned.status_code,400) #checking status code






if __name__ == '__main__':
    unittest.main()