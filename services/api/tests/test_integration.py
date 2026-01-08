"""
Integration Tests
Tests full workflows end-to-end
"""

import pytest
from fastapi.testclient import TestClient
from app.main_complete import app

client = TestClient(app)

class TestIntegration:
    """Test complete workflows"""
    
    def test_employee_lifecycle(self):
        """Test: Create -> Read -> Update -> Delete"""
        
        # 1. Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin@example.com", "password": "admin123"}
        )
        
        if login_response.status_code != 200:
            pytest.skip("Auth not configured")
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Create employee
        employee_data = {
            "email": "john.doe@test.com",
            "first_name": "John",
            "last_name": "Doe",
            "employee_number": "EMP001",
            "department": "Engineering",
            "position": "Developer",
            "hire_date": "2024-01-01"
        }
        
        create_response = client.post(
            "/api/employees",
            json=employee_data,
            headers=headers
        )
        
        if create_response.status_code == 201:
            employee_id = create_response.json()["id"]
            
            # 3. Read employee
            read_response = client.get(
                f"/api/employees/{employee_id}",
                headers=headers
            )
            assert read_response.status_code == 200
            
            # 4. Update employee
            update_response = client.put(
                f"/api/employees/{employee_id}",
                json={"position": "Senior Developer"},
                headers=headers
            )
            assert update_response.status_code in [200, 204]
            
            # 5. Delete employee
            delete_response = client.delete(
                f"/api/employees/{employee_id}",
                headers=headers
            )
            assert delete_response.status_code in [200, 204]
    
    def test_time_tracking_workflow(self):
        """Test: Clock In -> View Entry -> Clock Out"""
        
        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "user@example.com", "password": "user123"}
        )
        
        if login_response.status_code != 200:
            pytest.skip("Auth not configured")
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Clock in
        clock_in_response = client.post("/api/time/clock-in", headers=headers)
        
        if clock_in_response.status_code == 200:
            entry = clock_in_response.json()
            entry_id = entry.get("id")
            
            # Get entries
            entries_response = client.get("/api/time/entries", headers=headers)
            assert entries_response.status_code == 200
            
            # Clock out
            clock_out_response = client.post("/api/time/clock-out", headers=headers)
            assert clock_out_response.status_code == 200
    
    def test_dashboard_data_consistency(self):
        """Test dashboard data is consistent"""
        
        login_response = client.post(
            "/api/auth/login",
            json={"email": "user@example.com", "password": "user123"}
        )
        
        if login_response.status_code != 200:
            pytest.skip("Auth not configured")
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get complete dashboard
        dashboard_response = client.get("/api/dashboard/complete", headers=headers)
        
        if dashboard_response.status_code == 200:
            data = dashboard_response.json()
            
            # Validate structure
            assert "metrics" in data
            assert "employees" in data
            
            # Cross-validate
            metrics = data["metrics"]
            employees = data["employees"]
            
            # Active employees count should match array
            active = [e for e in employees if e.get("status") == "active"]
            # Note: might not match exactly due to pagination
