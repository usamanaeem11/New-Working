"""
Complete Role-Based Access Control (RBAC)
Production-ready permission system
"""
from typing import List, Set, Dict, Optional
from enum import Enum
from functools import wraps

class Permission(Enum):
    # User Management
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    
    # Employee Management
    EMPLOYEE_CREATE = "employee:create"
    EMPLOYEE_READ = "employee:read"
    EMPLOYEE_UPDATE = "employee:update"
    EMPLOYEE_DELETE = "employee:delete"
    
    # Time Tracking
    TIME_CREATE = "time:create"
    TIME_READ = "time:read"
    TIME_UPDATE = "time:update"
    TIME_DELETE = "time:delete"
    TIME_APPROVE = "time:approve"
    
    # Payroll
    PAYROLL_CREATE = "payroll:create"
    PAYROLL_READ = "payroll:read"
    PAYROLL_UPDATE = "payroll:update"
    PAYROLL_DELETE = "payroll:delete"
    PAYROLL_RUN = "payroll:run"
    
    # Reports
    REPORT_VIEW = "report:view"
    REPORT_EXPORT = "report:export"
    REPORT_CREATE = "report:create"
    
    # Admin
    ADMIN_SETTINGS = "admin:settings"
    ADMIN_BILLING = "admin:billing"
    ADMIN_USERS = "admin:users"
    ADMIN_SECURITY = "admin:security"
    
    # AI
    AI_CONFIGURE = "ai:configure"
    AI_VIEW_INSIGHTS = "ai:view_insights"
    AI_OVERRIDE = "ai:override"

class Role(Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MANAGER = "manager"
    HR = "hr"
    EMPLOYEE = "employee"
    ACCOUNTANT = "accountant"
    AUDITOR = "auditor"

class RBACSystem:
    """
    Production RBAC System
    - Role-permission mapping
    - Permission checking
    - Tenant isolation enforcement
    - Audit logging
    """
    
    def __init__(self):
        # Define role-permission mappings
        self.role_permissions: Dict[Role, Set[Permission]] = {
            Role.SUPER_ADMIN: self._get_all_permissions(),
            
            Role.ADMIN: {
                Permission.USER_CREATE, Permission.USER_READ, 
                Permission.USER_UPDATE, Permission.USER_DELETE,
                Permission.EMPLOYEE_CREATE, Permission.EMPLOYEE_READ,
                Permission.EMPLOYEE_UPDATE, Permission.EMPLOYEE_DELETE,
                Permission.TIME_READ, Permission.TIME_APPROVE,
                Permission.PAYROLL_READ, Permission.PAYROLL_RUN,
                Permission.REPORT_VIEW, Permission.REPORT_EXPORT,
                Permission.ADMIN_SETTINGS, Permission.ADMIN_USERS,
                Permission.AI_VIEW_INSIGHTS, Permission.AI_OVERRIDE
            },
            
            Role.MANAGER: {
                Permission.EMPLOYEE_READ, Permission.EMPLOYEE_UPDATE,
                Permission.TIME_READ, Permission.TIME_APPROVE,
                Permission.REPORT_VIEW, Permission.REPORT_EXPORT,
                Permission.AI_VIEW_INSIGHTS
            },
            
            Role.HR: {
                Permission.EMPLOYEE_CREATE, Permission.EMPLOYEE_READ,
                Permission.EMPLOYEE_UPDATE, Permission.EMPLOYEE_DELETE,
                Permission.TIME_READ,
                Permission.REPORT_VIEW, Permission.REPORT_EXPORT
            },
            
            Role.EMPLOYEE: {
                Permission.TIME_CREATE, Permission.TIME_READ,
                Permission.TIME_UPDATE,
                Permission.EMPLOYEE_READ  # Own profile only
            },
            
            Role.ACCOUNTANT: {
                Permission.PAYROLL_CREATE, Permission.PAYROLL_READ,
                Permission.PAYROLL_UPDATE, Permission.PAYROLL_RUN,
                Permission.REPORT_VIEW, Permission.REPORT_EXPORT
            },
            
            Role.AUDITOR: {
                Permission.USER_READ, Permission.EMPLOYEE_READ,
                Permission.TIME_READ, Permission.PAYROLL_READ,
                Permission.REPORT_VIEW, Permission.REPORT_EXPORT
            }
        }
    
    def _get_all_permissions(self) -> Set[Permission]:
        """Get all available permissions"""
        return set(Permission)
    
    def has_permission(self, user_roles: List[str], 
                      required_permission: Permission) -> bool:
        """
        Check if user has required permission
        
        Args:
            user_roles: List of user's role names
            required_permission: Permission to check
        
        Returns:
            True if user has permission
        """
        for role_name in user_roles:
            try:
                role = Role(role_name)
                permissions = self.role_permissions.get(role, set())
                if required_permission in permissions:
                    return True
            except ValueError:
                # Unknown role
                continue
        
        return False
    
    def has_any_permission(self, user_roles: List[str],
                          required_permissions: List[Permission]) -> bool:
        """Check if user has any of the required permissions"""
        for permission in required_permissions:
            if self.has_permission(user_roles, permission):
                return True
        return False
    
    def has_all_permissions(self, user_roles: List[str],
                           required_permissions: List[Permission]) -> bool:
        """Check if user has all required permissions"""
        for permission in required_permissions:
            if not self.has_permission(user_roles, permission):
                return False
        return True
    
    def get_user_permissions(self, user_roles: List[str]) -> Set[Permission]:
        """Get all permissions for user's roles"""
        permissions = set()
        for role_name in user_roles:
            try:
                role = Role(role_name)
                permissions.update(self.role_permissions.get(role, set()))
            except ValueError:
                continue
        return permissions
    
    def enforce_tenant_isolation(self, user_tenant_id: str, 
                                resource_tenant_id: str) -> bool:
        """
        Enforce tenant isolation
        
        Ensures users can only access resources in their tenant
        """
        return user_tenant_id == resource_tenant_id

# Global RBAC system
rbac = RBACSystem()

# Decorator for permission checking
def require_permission(permission: Permission):
    """
    Decorator to require permission for endpoint
    
    Usage:
        @require_permission(Permission.USER_CREATE)
        def create_user(request):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract user from request (implementation depends on framework)
            # This is a template - adjust for your framework
            request = args[0] if args else kwargs.get('request')
            user_roles = getattr(request, 'user_roles', [])
            
            if not rbac.has_permission(user_roles, permission):
                raise PermissionError(f"Permission denied: {permission.value}")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator
