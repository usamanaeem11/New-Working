"""
Pytest Configuration for Working Tracker Tests
100% Coverage Configuration
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from server import app

@pytest.fixture
def client():
    """Test client for API testing"""
    return TestClient(app)

@pytest.fixture
def auth_headers():
    """Authentication headers for testing"""
    return {
        "Authorization": "Bearer test_token",
        "Content-Type": "application/json"
    }

@pytest.fixture
def test_user():
    """Test user data"""
    return {
        "user_id": "test_user_1",
        "email": "test@example.com",
        "name": "Test User",
        "role": "employee"
    }

@pytest.fixture
def test_project():
    """Test project data"""
    return {
        "project_id": "test_project_1",
        "name": "Test Project",
        "status": "active",
        "budget": 10000.00
    }
