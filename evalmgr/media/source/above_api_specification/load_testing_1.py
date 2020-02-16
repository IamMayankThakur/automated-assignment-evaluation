from locust import HttpLocust, TaskSet, task,between
import json
 
class UserBehavior(TaskSet):
 
    @task(1)    
    def put_user(self):
        data = json.dumps({"username":"Anshuman","password":"3d725109c7e7c0bfb9d709836735b56d943d263f"})
        self.client.put("/api/v1/users",data= json.dumps(data))
     
    @task(2)    
    def create_ride(self):
        data = json.dumps({"created_by":"Anshuman","timestamp":"10-02-2020:20:33:08","source":"21","destination":"25"})
        self.client.post("/api/v1/rides",data= json.dumps(data))

    @task(3)    
    def srcdst_ride(self):
        self.client.get("/api/v1/rides?source=21&destination=25")

    @task(4)    
    def ride_detail(self):
        self.client.get("/api/v1/rides/1")

    @task(5)    
    def join_ride(self):
        data = json.dumps({"username":"Anshuman"})
        self.client.post("/api/v1/rides",data= json.dumps(data))

    @task(6)    
    def delete_ride(self):
        self.client.delete("/api/v1/rides/1")

    @task(7)    
    def delete_user(self):
        self.client.delete("/api/v1/users/Anshuman")

 
class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    wait_time = between(1.000,20.000)