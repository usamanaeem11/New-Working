"""
Unit Tests for Validation Middleware
"""

import pytest
from fastapi.testclient import TestClient
from app.main_complete import app

client = TestClient(app)

class TestValidation:
    """Test input validation"""
    
    def test_sql_injection_blocked(self):
        """SQL injection should be blocked"""
        response = client.post(
            "/api/employees",
            json={"first_name": "'; DROP TABLE users--"},
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code in [400, 403]
    
    def test_xss_blocked(self):
        """XSS should be blocked"""
        response = client.post(
            "/api/employees",
            json={"first_name": "<script>alert('xss')</script>"},
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code in [400, 403]
    
    def test_oversized_payload_blocked(self):
        """Oversized payloads should be rejected"""
        huge_data = "x" * 50000
        
        response = client.post(
            "/api/employees",
            json={"first_name": huge_data},
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code in [400, 413]
    
    def test_valid_input_accepted(self):
        """Valid input should be accepted"""
        response = client.post(
            "/api/employees",
            json={
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com"
            },
            headers={"Authorization": "Bearer test_token"}
        )
        
        # Should not be blocked by validation
        assert response.status_code not in [400, 413]
