from locust import HttpLocust, TaskSet, task
from flask import Flask,request, render_template,\
jsonify,request,abort
import names

class UserBehavior(TaskSet):

	@task
	def get_tests(self):
		self.client.get("/api/v1/rides/2")
        
	@task
	def post_tests(self):
		self.client.put("/api/v1/users", json={"username":names.get_first_name(),"password":"3d725109c7e7c0bfb9d709836735b56d943d263f"})

	@task   
	def add_ride_tests(self):
		self.client.post("/api/v1/rides", json={"created_by":"Shaun","timestamp":"02-02-2020:12-12-12","source":"21","destination":"27"})


	

class WebsiteUser(HttpLocust):
	task_set = UserBehavior
