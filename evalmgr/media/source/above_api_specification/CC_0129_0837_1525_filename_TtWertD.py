import random
import pandas as pd
from locust import HttpLocust, TaskSet, task, between

class WebsiteTasks(TaskSet):
	@task
	def add_user(self):
		username = str(random.randint(1,100000))
		self.client.put('/api/v1/users', json={"username":username, "password":"1234567890123456789012345678901234567890"})

	@task
	def delete_user(self):
		username = str(random.randint(1,100000))
		self.client.delete('/api/v1/users/' + str(username[0]))

	@task
	def new_ride(self):
		username = str(random.randint(1,100000))
		timestamp = '13-07-2020:12-12-12'
		source = random.randint(1, 100)
		destination = random.randint(1,100)
		self.client.post('/api/v1/rides', json={"created_by":str(username[0]), "timestamp":timestamp, "source":source, "destination":destination})

	@task
	def list_rides(self):
		source = random.randint(1, 100)
		destination = random.randint(1, 100)
		self.client.get('/api/v1/rides?source=' + str(source) + '&destination=' + str(destination))

	@task
	def get_ride_details(self):
		rides_count = open('rides_count.txt','r')
		last_rideId = rides_count.read()
		rides_count.close()
		rideId = str(random.randint(1,int(last_rideId)+1))
		self.client.get('/api/v1/rides/' + str(rideId[0]))

	@task
	def join_ride(self):
		rides_count = open('rides_count.txt','r')
		last_rideId = rides_count.read()
		rides_count.close()
		rideId = str(random.randint(1,int(last_rideId)+1))
		username = str(random.randint(1,100000))
		self.client.post('/api/v1/rides/' + str(rideId[0]), json={"username":str(username[0])})

	@task
	def delete_ride(self):
		rides_count = open('rides_count.txt','r')
		last_rideId = rides_count.read()
		rides_count.close()
		rideId = str(random.randint(1,int(last_rideId)+1))
		self.client.delete('/api/v1/rides/' + str(rideId[0]))

class WebsiteUser(HttpLocust):
	task_set = WebsiteTasks
	wait_time = between(5000,100000)