"""
API Contract Tests
Ensures API adheres to contracts
"""

import pytest
from fastapi.testclient import TestClient
from app.main_complete import app

client = TestClient(app)

class TestAPIContracts:
    """Test all API endpoints against contracts"""
    
    def test_auth_login_contract(self):
        """Test /api/auth/login contract"""
        response = client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "password123"}
        )
        
        # Should return 200 or 401 (not 500)
        assert response.status_code in [200, 401]
        
        # Response structure
        if response.status_code == 200:
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data
            assert "token_type" in data
            assert data["token_type"] == "bearer"
    
    def test_employees_list_contract(self):
        """Test GET /api/employees contract"""
        # Mock auth token
        headers = {"Authorization": "Bearer test_token"}
        
        response = client.get("/api/employees", headers=headers)
        
        # Should be array
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
            
            if len(data) > 0:
                employee = data[0]
                # Required fields
                assert "id" in employee
                assert "first_name" in employee
                assert "last_name" in employee
                assert "email" in employee
    
    def test_dashboard_metrics_contract(self):
        """Test GET /api/dashboard/metrics contract"""
        headers = {"Authorization": "Bearer test_token"}
        
        response = client.get("/api/dashboard/metrics", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            assert "metrics" in data
            
            metrics = data["metrics"]
            assert "active_employees" in metrics
            assert "clocked_in" in metrics
            assert "today_hours" in metrics
            assert "week_hours" in metrics
            
            # Type validation
            assert isinstance(metrics["active_employees"], int)
            assert isinstance(metrics["clocked_in"], int)
            assert isinstance(metrics["today_hours"], (int, float))
    
    def test_error_format_contract(self):
        """Test error response format"""
        response = client.get("/api/nonexistent")
        
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], str)
    
    def test_input_validation_contract(self):
        """Test input validation"""
        headers = {"Authorization": "Bearer test_token"}
        
        # Oversized payload should be rejected
        huge_string = "x" * 20000
        response = client.post(
            "/api/employees",
            json={"first_name": huge_string},
            headers=headers
        )
        
        assert response.status_code in [400, 413]
    
    def test_injection_prevention(self):
        """Test SQL injection prevention"""
        headers = {"Authorization": "Bearer test_token"}
        
        response = client.post(
            "/api/employees",
            json={"first_name": "'; DROP TABLE users--"},
            headers=headers
        )
        
        # Should be blocked
        assert response.status_code in [400, 403]
