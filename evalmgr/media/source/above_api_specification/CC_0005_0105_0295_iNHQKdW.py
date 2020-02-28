from assg1 import app
import unittest 
import names

from random import seed
from random import randint


class RideShareTests(unittest.TestCase): 

	@classmethod
	def setUpClass(cls):
		pass 

	@classmethod
	def tearDownClass(cls):
		pass 

	def setUp(self):
		self.app = app.test_client()
		self.app.testing = True 

	def tearDown(self):
		pass 

	def test_get_ride_details(self):
		result = self.app.get('/api/v1/rides/24') 
		self.assertEqual(result.status_code, 200)

	def test_add_username(self):
		result=self.app.put("/api/v1/users", json={"username":names.get_first_name(),"password":"3d725109c7e7c0bfb9d709836735b56d943d263f"})
		self.assertEqual(result.status_code, 201)

	def test_add_ride(self):
		result=self.app.post("/api/v1/rides", json={"created_by":"April","timestamp":"02-01-2020:15-12-12","source":21,"destination":27})
		self.assertEqual(result.status_code, 201)

	def test_get_upcoming_details(self):
		result = self.app.get("/api/v1/rides?source=21&destination=25") 
		self.assertEqual(result.status_code, 200)

	def test_join_ride(self):
		result=self.app.post("/api/v1/rides/"+str(randint(1,30)), json={"username":"Joe"})
		self.assertEqual(result.status_code, 200)
	
	def test_delete_ride(self):
		result=self.app.delete("/api/v1/rides/"+str(randint(1,30)))
		self.assertEqual(result.status_code, 200)	
	

	

	
            
    


