"""
Load Testing with Locust
"""
from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def get_dashboard(self):
        self.client.get("/api/dashboard")
    
    @task(2)
    def get_employees(self):
        self.client.get("/api/employees")
    
    @task(1)
    def post_timesheet(self):
        self.client.post("/api/timesheets", json={
            "employee_id": "test",
            "hours": 8
        })

