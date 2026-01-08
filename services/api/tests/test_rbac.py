"""
Unit Tests for RBAC System
"""

import pytest
from app.auth.rbac import has_permission, Permission, Role

class TestRBAC:
    """Test RBAC functionality"""
    
    def test_admin_has_all_permissions(self):
        """Admin should have all permissions"""
        admin_user = {'roles': [Role.ADMIN.value]}
        
        assert has_permission(admin_user, Permission.EMPLOYEE_CREATE)
        assert has_permission(admin_user, Permission.PAYROLL_RUN)
        assert has_permission(admin_user, Permission.ADMIN_SETTINGS)
    
    def test_employee_limited_permissions(self):
        """Employee should have limited permissions"""
        employee_user = {'roles': [Role.EMPLOYEE.value]}
        
        assert has_permission(employee_user, Permission.TIME_CREATE)
        assert not has_permission(employee_user, Permission.EMPLOYEE_CREATE)
        assert not has_permission(employee_user, Permission.PAYROLL_RUN)
    
    def test_manager_permissions(self):
        """Manager should have team management permissions"""
        manager_user = {'roles': [Role.MANAGER.value]}
        
        assert has_permission(manager_user, Permission.EMPLOYEE_READ)
        assert has_permission(manager_user, Permission.TIME_APPROVE)
        assert not has_permission(manager_user, Permission.PAYROLL_RUN)
    
    def test_multiple_roles(self):
        """User with multiple roles should have combined permissions"""
        user = {'roles': [Role.MANAGER.value, Role.HR.value]}
        
        assert has_permission(user, Permission.EMPLOYEE_READ)
        assert has_permission(user, Permission.EMPLOYEE_CREATE)
    
    def test_no_roles(self):
        """User with no roles should have no permissions"""
        user = {'roles': []}
        
        assert not has_permission(user, Permission.EMPLOYEE_READ)
        assert not has_permission(user, Permission.TIME_CREATE)
